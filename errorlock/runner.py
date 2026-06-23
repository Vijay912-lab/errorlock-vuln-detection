from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from .data import load_samples, train_test_split_samples
from .memory import MistakeMemory
from .metrics import rows_for_csv, summarize
from .parser import parse_prediction
from .prompts import baseline_prompt, errorlock_prompt
from .providers import LLMProvider
from .types import CastleSample, Prediction, ScoredPrediction, normalize_cwe


@dataclass(frozen=True)
class BenchmarkConfig:
    dataset_path: Path
    out_dir: Path
    db_path: Path
    limit: int | None = None
    train_size: float = 0.4
    seed: int = 7
    top_k: int = 3
    all_memory: bool = False
    rag_memory: bool = False
    rag_candidate_k: int = 25
    rag_context_k: int = 6
    rag_snippet_chars: int = 700
    gated: bool = False
    min_similarity: float = 0.18
    cwe_recheck_similarity: float = 0.35
    near_duplicate_similarity: float = 0.95
    preserve_binary_decision: bool = True
    selective_binary_override: bool = False
    binary_override_similarity: float = 0.62
    binary_override_votes: int = 2
    skip_if_baseline_not_vulnerable: bool = True
    skip_if_baseline_vulnerable: bool = False
    skip_if_baseline_has_cwe: bool = True


def run_benchmark(provider: LLMProvider, config: BenchmarkConfig) -> dict:
    config.out_dir.mkdir(parents=True, exist_ok=True)
    samples = load_samples(config.dataset_path, config.limit)
    train, test = train_test_split_samples(samples, train_size=config.train_size, seed=config.seed)
    memory = MistakeMemory(config.db_path)
    try:
        train_scores = _run_baseline_train(provider, train, memory)
        baseline_scores, errorlock_scores = _run_test(provider, test, memory, config)
    finally:
        memory.close()

    all_scores = train_scores + baseline_scores + errorlock_scores
    pd.DataFrame(rows_for_csv(all_scores)).to_csv(config.out_dir / "predictions.csv", index=False)

    summary = {
        "model": provider.name,
        "dataset": str(config.dataset_path),
        "n_total": len(samples),
        "n_train": len(train),
        "n_test": len(test),
        "top_k": config.top_k,
        "all_memory": config.all_memory,
        "rag_memory": config.rag_memory,
        "rag_candidate_k": config.rag_candidate_k,
        "rag_context_k": config.rag_context_k,
        "rag_snippet_chars": config.rag_snippet_chars,
        "gated": config.gated,
        "min_similarity": config.min_similarity,
        "cwe_recheck_similarity": config.cwe_recheck_similarity,
        "near_duplicate_similarity": config.near_duplicate_similarity,
        "preserve_binary_decision": config.preserve_binary_decision,
        "selective_binary_override": config.selective_binary_override,
        "binary_override_similarity": config.binary_override_similarity,
        "binary_override_votes": config.binary_override_votes,
        "skip_if_baseline_not_vulnerable": config.skip_if_baseline_not_vulnerable,
        "skip_if_baseline_vulnerable": config.skip_if_baseline_vulnerable,
        "skip_if_baseline_has_cwe": config.skip_if_baseline_has_cwe,
        "baseline": summarize(baseline_scores),
        "errorlock": summarize(errorlock_scores),
        "train_baseline_for_memory": summarize(train_scores),
    }
    (config.out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    (config.out_dir / "report.md").write_text(render_report(summary))
    return summary


def _run_baseline_train(
    provider: LLMProvider,
    train: list[CastleSample],
    memory: MistakeMemory,
) -> list[ScoredPrediction]:
    scored: list[ScoredPrediction] = []
    for sample in tqdm(train, desc=f"{provider.name} train/memory"):
        pred = parse_prediction(provider.generate(baseline_prompt(sample), sample))
        item = ScoredPrediction(sample=sample, prediction=pred, model=provider.name, method="train_baseline")
        memory.add_if_mistake(item)
        scored.append(item)
    return scored


def _run_test(
    provider: LLMProvider,
    test: list[CastleSample],
    memory: MistakeMemory,
    config: BenchmarkConfig,
) -> tuple[list[ScoredPrediction], list[ScoredPrediction]]:
    baseline: list[ScoredPrediction] = []
    errorlock: list[ScoredPrediction] = []
    for sample in tqdm(test, desc=f"{provider.name} test"):
        base_pred = parse_prediction(provider.generate(baseline_prompt(sample), sample))
        baseline.append(
            ScoredPrediction(sample=sample, prediction=base_pred, model=provider.name, method="baseline")
        )
        gate_mistakes = memory.retrieve(
            sample,
            model=provider.name,
            top_k=config.top_k,
            predicted_vulnerable=base_pred.vulnerable,
            predicted_cwe=base_pred.cwe,
        )
        memory_context = None
        rag_candidate_count = None
        if config.rag_memory:
            rag_context = memory.retrieve_rag_context(
                sample,
                model=provider.name,
                candidate_k=config.rag_candidate_k,
                context_k=config.rag_context_k,
                predicted_vulnerable=base_pred.vulnerable,
                predicted_cwe=base_pred.cwe,
                snippet_chars=config.rag_snippet_chars,
            )
            mistakes = rag_context.mistakes
            memory_context = rag_context.text
            rag_candidate_count = rag_context.candidate_count
        elif config.all_memory:
            mistakes = memory.retrieve(
                sample,
                model=provider.name,
                top_k=None,
                predicted_vulnerable=base_pred.vulnerable,
                predicted_cwe=base_pred.cwe,
            )
        else:
            mistakes = gate_mistakes
        max_similarity = gate_mistakes[0].similarity if gate_mistakes else None
        should_apply, gate_reason = _gate_errorlock(base_pred, gate_mistakes, config)
        if should_apply:
            fixed_pred = parse_prediction(
                provider.generate(
                    errorlock_prompt(
                        sample,
                        mistakes,
                        baseline=base_pred,
                        preserve_binary_decision=config.preserve_binary_decision,
                        selective_binary_override=config.selective_binary_override,
                        memory_context=memory_context,
                    ),
                    sample,
                )
            )
            fixed_pred = _merge_with_baseline(base_pred, fixed_pred, gate_mistakes, config)
        else:
            fixed_pred = base_pred
        errorlock.append(
            ScoredPrediction(
                sample=sample,
                prediction=fixed_pred,
                model=provider.name,
                method=_errorlock_method(config),
                errorlock_applied=should_apply,
                gate_reason=gate_reason,
                retrieved_count=rag_candidate_count or len(mistakes),
                max_similarity=max_similarity,
            )
        )
    return baseline, errorlock


def _errorlock_method(config: BenchmarkConfig) -> str:
    prefix = "errorlock_rag" if config.rag_memory else "errorlock_all_memory" if config.all_memory else "errorlock"
    return f"{prefix}_gated" if config.gated else prefix


def _merge_with_baseline(
    baseline: Prediction,
    errorlock: Prediction,
    mistakes,
    config: BenchmarkConfig,
) -> Prediction:
    if not config.preserve_binary_decision:
        return errorlock
    if not baseline.parsed:
        return errorlock
    if not errorlock.parsed:
        return baseline
    if config.selective_binary_override and _accept_binary_override(baseline, errorlock, mistakes, config):
        return errorlock
    if baseline.vulnerable is False:
        return Prediction(
            vulnerable=False,
            cwe=None,
            location=None,
            explanation=f"Binary decision preserved from baseline. {errorlock.explanation or ''}".strip(),
            raw=errorlock.raw,
        )
    return Prediction(
        vulnerable=baseline.vulnerable,
        cwe=errorlock.cwe or baseline.cwe,
        location=errorlock.location or baseline.location,
        explanation=f"Binary decision preserved from baseline. {errorlock.explanation or ''}".strip(),
        raw=errorlock.raw,
    )


def _accept_binary_override(
    baseline: Prediction,
    errorlock: Prediction,
    mistakes,
    config: BenchmarkConfig,
) -> bool:
    if not mistakes or mistakes[0].similarity < config.binary_override_similarity:
        return False
    if baseline.vulnerable is errorlock.vulnerable:
        return False
    if baseline.vulnerable is False and errorlock.vulnerable is True:
        votes = [
            m
            for m in mistakes
            if m.true_vulnerable
            and m.predicted_vulnerable is False
            and m.similarity >= config.binary_override_similarity
        ]
        if len(votes) < config.binary_override_votes:
            return False
        consensus_cwes = {normalize_cwe(m.true_cwe) for m in votes if normalize_cwe(m.true_cwe)}
        return not errorlock.cwe or not consensus_cwes or normalize_cwe(errorlock.cwe) in consensus_cwes
    if baseline.vulnerable is True and errorlock.vulnerable is False:
        votes = [
            m
            for m in mistakes
            if not m.true_vulnerable
            and m.predicted_vulnerable is True
            and m.similarity >= config.binary_override_similarity
        ]
        return len(votes) >= config.binary_override_votes
    return False


def _gate_errorlock(prediction: Prediction, mistakes, config: BenchmarkConfig) -> tuple[bool, str]:
    if not config.gated:
        return True, "ungated"
    if not mistakes:
        return False, "no_memory"
    best_similarity = mistakes[0].similarity
    if best_similarity < config.min_similarity:
        return False, "low_similarity"
    if (
        best_similarity >= config.near_duplicate_similarity
        and mistakes[0].true_vulnerable is False
        and prediction.parsed
        and prediction.vulnerable
    ):
        return False, "near_duplicate_false_positive"
    if (
        prediction.parsed
        and prediction.vulnerable is False
        and config.skip_if_baseline_not_vulnerable
        and not _has_false_negative_override_evidence(mistakes, config)
    ):
        return False, "baseline_not_vulnerable"
    if prediction.parsed and prediction.vulnerable is False and mistakes[0].true_vulnerable is False:
        return False, "similar_false_positive"
    if prediction.parsed and config.skip_if_baseline_has_cwe and prediction.vulnerable and prediction.cwe:
        if _should_recheck_cwe(prediction, mistakes, config):
            return True, "cwe_recheck"
        return False, "baseline_has_cwe"
    if prediction.parsed and config.skip_if_baseline_vulnerable and prediction.vulnerable:
        return False, "baseline_vulnerable"
    return True, "applied"


def _has_false_negative_override_evidence(mistakes, config: BenchmarkConfig) -> bool:
    if not config.selective_binary_override or not mistakes:
        return False
    votes = [
        m
        for m in mistakes
        if m.true_vulnerable
        and m.predicted_vulnerable is False
        and m.similarity >= config.binary_override_similarity
    ]
    return len(votes) >= config.binary_override_votes


def _should_recheck_cwe(prediction: Prediction, mistakes, config: BenchmarkConfig) -> bool:
    predicted_cwe = normalize_cwe(prediction.cwe)
    if not predicted_cwe or mistakes[0].similarity < config.cwe_recheck_similarity:
        return False
    disagreeing_true_cwes = [
        normalize_cwe(m.true_cwe)
        for m in mistakes
        if m.true_vulnerable and normalize_cwe(m.true_cwe) and normalize_cwe(m.true_cwe) != predicted_cwe
    ]
    if len(disagreeing_true_cwes) >= 2:
        return True
    same_wrong_cwe = [
        m
        for m in mistakes
        if normalize_cwe(m.predicted_cwe) == predicted_cwe and normalize_cwe(m.true_cwe) != predicted_cwe
    ]
    return len(same_wrong_cwe) >= 1 and len(disagreeing_true_cwes) >= 1


def render_report(summary: dict) -> str:
    base = summary["baseline"]
    err = summary["errorlock"]
    return f"""# ErrorLock Benchmark Report

Model: `{summary["model"]}`

Dataset: `{summary["dataset"]}`

Samples: {summary["n_total"]} total, {summary["n_train"]} memory-build train, {summary["n_test"]} fair test.

| Method | Accuracy | Precision | Recall | F1 | Parse Failures | CWE Correct |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | {base.get("accuracy", 0):.3f} | {base.get("precision", 0):.3f} | {base.get("recall", 0):.3f} | {base.get("f1", 0):.3f} | {base.get("parse_failure_rate", 0):.3f} | {base.get("cwe_correct_rate", 0):.3f} |
| ErrorLock | {err.get("accuracy", 0):.3f} | {err.get("precision", 0):.3f} | {err.get("recall", 0):.3f} | {err.get("f1", 0):.3f} | {err.get("parse_failure_rate", 0):.3f} | {err.get("cwe_correct_rate", 0):.3f} |

## Notes

ErrorLock builds SQLite mistake memory only from the training split. During test-time
retrieval it uses code similarity, not the test sample's ground-truth CWE.
Gated mode: {summary.get("gated", False)}.
"""
