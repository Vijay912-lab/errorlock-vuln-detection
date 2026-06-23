from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from .types import CastleSample, normalize_cwe

CASTLE_MIN_JSON_URL = (
    "https://raw.githubusercontent.com/CASTLE-Benchmark/CASTLE-Benchmark/"
    "main/datasets/CASTLE-C250.min.json"
)
CASTLE_JSON_URL = (
    "https://raw.githubusercontent.com/CASTLE-Benchmark/CASTLE-Benchmark/"
    "main/datasets/CASTLE-C250.json"
)


def download_castle(path: Path, url: str = CASTLE_MIN_JSON_URL) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response:
        path.write_bytes(response.read())
    return path


def load_samples(path: Path | str, limit: int | None = None) -> list[CastleSample]:
    records = json.loads(Path(path).read_text())
    if isinstance(records, dict):
        records = records.get("tests") or records.get("samples") or records.get("data") or records
    if isinstance(records, dict):
        records = list(records.values())
    samples = [_normalize_record(record, i) for i, record in enumerate(records)]
    return samples[:limit] if limit else samples


def train_test_split_samples(
    samples: list[CastleSample],
    train_size: float = 0.4,
    seed: int = 7,
) -> tuple[list[CastleSample], list[CastleSample]]:
    from sklearn.model_selection import train_test_split

    labels = [f"{s.cwe}:{int(s.vulnerable)}" for s in samples]
    stratify = labels if len(set(labels)) > 1 and min(labels.count(x) for x in set(labels)) >= 2 else None
    train, test = train_test_split(samples, train_size=train_size, random_state=seed, stratify=stratify)
    return list(train), list(test)


def _normalize_record(record: dict[str, Any], index: int) -> CastleSample:
    sample_id = _first(record, ["id", "test_id", "name", "filename", "file", "path"]) or f"sample-{index:04d}"
    code = _first(record, ["code", "source", "source_code", "content", "program"])
    if code is None:
        code = _code_from_nested(record)
    vulnerable = _bool(_first(record, ["vulnerable", "is_vulnerable", "label", "target", "buggy"]))
    cwe = normalize_cwe(_first(record, ["cwe", "CWE", "weakness", "cwe_id", "true_cwe"]))
    location = _first(record, ["location", "line", "lines", "true_location", "vuln_line", "sink"])
    return CastleSample(
        sample_id=str(sample_id),
        code=str(code or ""),
        vulnerable=vulnerable,
        cwe=cwe,
        location=str(location) if location not in (None, "") else None,
        meta=record,
    )


def _first(record: dict[str, Any], keys: Iterable[str]) -> Any:
    lower = {str(k).lower(): v for k, v in record.items()}
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
        value = lower.get(key.lower())
        if value not in (None, ""):
            return value
    return None


def _code_from_nested(record: dict[str, Any]) -> str | None:
    for value in record.values():
        if isinstance(value, dict):
            found = _first(value, ["code", "source", "source_code", "content", "program"])
            if found:
                return str(found)
    return None


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "vulnerable", "buggy", "bad"}:
        return True
    if text in {"0", "false", "no", "safe", "clean", "good"}:
        return False
    return bool(value)
