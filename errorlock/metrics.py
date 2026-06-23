from __future__ import annotations

from collections import Counter
from typing import Iterable

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from .types import ScoredPrediction


def summarize(scored: Iterable[ScoredPrediction]) -> dict:
    rows = list(scored)
    if not rows:
        return {}
    y_true = [r.sample.vulnerable for r in rows]
    y_pred = [bool(r.prediction.vulnerable) if r.prediction.parsed else False for r in rows]
    parse_failures = sum(not r.prediction.parsed for r in rows)
    failures = Counter(r.failure_type or "correct" for r in rows)
    return {
        "n": len(rows),
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "parse_failure_rate": parse_failures / len(rows),
        "binary_correct_rate": sum(r.binary_correct for r in rows) / len(rows),
        "cwe_correct_rate": sum(r.cwe_correct for r in rows) / len(rows),
        "location_correct_rate": sum(r.location_correct for r in rows) / len(rows),
        "failure_counts": dict(failures),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[False, True]).tolist(),
    }


def rows_for_csv(scored: Iterable[ScoredPrediction]) -> list[dict]:
    output = []
    for r in scored:
        p = r.prediction
        output.append(
            {
                "model": r.model,
                "method": r.method,
                "sample_id": r.sample.sample_id,
                "true_vulnerable": r.sample.vulnerable,
                "true_cwe": r.sample.cwe,
                "true_location": r.sample.location,
                "pred_vulnerable": p.vulnerable,
                "pred_cwe": p.cwe,
                "pred_location": p.location,
                "parsed": p.parsed,
                "parse_error": p.parse_error,
                "binary_correct": r.binary_correct,
                "cwe_correct": r.cwe_correct,
                "location_correct": r.location_correct,
                "failure_type": r.failure_type,
                "errorlock_applied": r.errorlock_applied,
                "gate_reason": r.gate_reason,
                "retrieved_count": r.retrieved_count,
                "max_similarity": r.max_similarity,
                "explanation": p.explanation,
                "raw": p.raw,
            }
        )
    return output
