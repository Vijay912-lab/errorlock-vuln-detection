from __future__ import annotations

import argparse
from pathlib import Path

from .data import CASTLE_MIN_JSON_URL, download_castle
from .providers import build_provider
from .runner import BenchmarkConfig, run_benchmark


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run ErrorLock CASTLE benchmark.")
    sub = parser.add_subparsers(dest="command", required=True)

    dl = sub.add_parser("download-castle", help="Download CASTLE-C250 JSON.")
    dl.add_argument("--out", default="data/CASTLE-C250.min.json")
    dl.add_argument("--url", default=CASTLE_MIN_JSON_URL)

    run = sub.add_parser("run", help="Run baseline vs ErrorLock benchmark.")
    run.add_argument("--dataset", required=True)
    run.add_argument(
        "--provider",
        choices=[
            "mock",
            "hf",
            "ollama",
            "openrouter",
            "groq",
            "hf-api",
            "gemini",
            "openai",
        ],
        default="mock",
    )
    run.add_argument("--model", default=None)
    run.add_argument("--out-dir", default="results/run")
    run.add_argument("--db", default=None)
    run.add_argument("--limit", type=int, default=None)
    run.add_argument("--train-size", type=float, default=0.4)
    run.add_argument("--seed", type=int, default=7)
    run.add_argument("--top-k", type=int, default=3)
    run.add_argument("--all-memory", action="store_true", help="Send every stored mistake to the ErrorLock prompt, ranked by similarity.")
    run.add_argument("--rag-memory", action="store_true", help="Send a compact RAG evidence pack built from reranked mistake candidates.")
    run.add_argument("--rag-candidate-k", type=int, default=25)
    run.add_argument("--rag-context-k", type=int, default=6)
    run.add_argument("--rag-snippet-chars", type=int, default=700)
    run.add_argument("--gated", action="store_true", help="Apply similarity/baseline gates before ErrorLock reprompting.")
    run.add_argument("--min-similarity", type=float, default=0.18)
    run.add_argument("--cwe-recheck-similarity", type=float, default=0.35)
    run.add_argument("--near-duplicate-similarity", type=float, default=0.95)
    run.add_argument("--allow-binary-change", action="store_true", help="Allow ErrorLock reprompts to change the baseline vulnerable/not-vulnerable decision.")
    run.add_argument("--selective-binary-override", action="store_true", help="Allow binary changes only when retrieved mistake memory strongly supports a known false-positive/false-negative pattern.")
    run.add_argument("--binary-override-similarity", type=float, default=0.62)
    run.add_argument("--binary-override-votes", type=int, default=2)
    run.add_argument("--allow-baseline-safe-recheck", action="store_true")
    run.add_argument("--skip-if-baseline-vulnerable", action="store_true")
    run.add_argument("--always-recheck-cwe", action="store_true", help="Do not skip when baseline already predicts vulnerable+CWE.")

    args = parser.parse_args(argv)
    if args.command == "download-castle":
        path = download_castle(Path(args.out), args.url)
        print(f"Downloaded CASTLE dataset to {path}")
        return

    out_dir = Path(args.out_dir)
    db = Path(args.db) if args.db else out_dir / "errorlock.sqlite"
    provider = build_provider(args.provider, args.model)
    summary = run_benchmark(
        provider,
        BenchmarkConfig(
            dataset_path=Path(args.dataset),
            out_dir=out_dir,
            db_path=db,
            limit=args.limit,
            train_size=args.train_size,
            seed=args.seed,
            top_k=args.top_k,
            all_memory=args.all_memory,
            rag_memory=args.rag_memory,
            rag_candidate_k=args.rag_candidate_k,
            rag_context_k=args.rag_context_k,
            rag_snippet_chars=args.rag_snippet_chars,
            gated=args.gated,
            min_similarity=args.min_similarity,
            cwe_recheck_similarity=args.cwe_recheck_similarity,
            near_duplicate_similarity=args.near_duplicate_similarity,
            preserve_binary_decision=not args.allow_binary_change or args.selective_binary_override,
            selective_binary_override=args.selective_binary_override,
            binary_override_similarity=args.binary_override_similarity,
            binary_override_votes=args.binary_override_votes,
            skip_if_baseline_not_vulnerable=not args.allow_baseline_safe_recheck,
            skip_if_baseline_vulnerable=args.skip_if_baseline_vulnerable,
            skip_if_baseline_has_cwe=not args.always_recheck_cwe,
        ),
    )
    print(f"Wrote results to {out_dir}")
    print(f"Baseline F1: {summary['baseline'].get('f1', 0):.3f}")
    print(f"ErrorLock F1: {summary['errorlock'].get('f1', 0):.3f}")


if __name__ == "__main__":
    main()
