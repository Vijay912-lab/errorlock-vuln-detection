from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def build_analysis(results_dir: Path, out: Path) -> None:
    summaries = []
    for path in sorted(results_dir.glob("*/summary.json")):
        data = json.loads(path.read_text())
        for method in ["baseline", "errorlock"]:
            metrics = data.get(method, {})
            summaries.append(
                {
                    "run": path.parent.name,
                    "model": data.get("model"),
                    "method": method,
                    "n_test": data.get("n_test"),
                    "accuracy": metrics.get("accuracy"),
                    "precision": metrics.get("precision"),
                    "recall": metrics.get("recall"),
                    "f1": metrics.get("f1"),
                    "parse_failure_rate": metrics.get("parse_failure_rate"),
                    "cwe_correct_rate": metrics.get("cwe_correct_rate"),
                    "location_correct_rate": metrics.get("location_correct_rate"),
                }
            )
    df = pd.DataFrame(summaries)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out.with_suffix(".csv"), index=False)
    out.write_text(render_markdown(df))


def render_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "# ErrorLock Analysis\n\nNo summaries found.\n"
    pivot_lines = []
    for run, group in df.groupby("run"):
        pivot_lines.append(f"## {run}\n")
        cols = [
            "model",
            "method",
            "n_test",
            "accuracy",
            "precision",
            "recall",
            "f1",
            "parse_failure_rate",
            "cwe_correct_rate",
        ]
        pivot_lines.append(_markdown_table(group[cols]))
        pivot_lines.append("")
    return "# ErrorLock Aggregate Analysis\n\n" + "\n".join(pivot_lines)


def _markdown_table(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for _, row in df.iterrows():
        values = []
        for col in headers:
            value = row[col]
            if isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--out", default="results/aggregate_analysis.md")
    args = parser.parse_args()
    build_analysis(Path(args.results_dir), Path(args.out))
    print(f"Wrote {args.out} and {Path(args.out).with_suffix('.csv')}")


if __name__ == "__main__":
    main()
