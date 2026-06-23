from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CastleSample:
    sample_id: str
    code: str
    vulnerable: bool
    cwe: str | None = None
    location: str | None = None
    meta: dict[str, Any] | None = None


@dataclass(frozen=True)
class Prediction:
    vulnerable: bool | None
    cwe: str | None = None
    location: str | None = None
    explanation: str | None = None
    raw: str = ""
    parse_error: str | None = None

    @property
    def parsed(self) -> bool:
        return self.parse_error is None and self.vulnerable is not None


@dataclass(frozen=True)
class ScoredPrediction:
    sample: CastleSample
    prediction: Prediction
    model: str
    method: str
    errorlock_applied: bool | None = None
    gate_reason: str | None = None
    retrieved_count: int = 0
    max_similarity: float | None = None

    @property
    def binary_correct(self) -> bool:
        return self.prediction.parsed and self.prediction.vulnerable == self.sample.vulnerable

    @property
    def cwe_correct(self) -> bool:
        if not self.sample.vulnerable:
            return self.binary_correct
        return self.binary_correct and normalize_cwe(self.prediction.cwe) == normalize_cwe(self.sample.cwe)

    @property
    def location_correct(self) -> bool:
        if not self.sample.vulnerable:
            return self.binary_correct
        if not self.binary_correct:
            return False
        expected = normalize_text(self.sample.location)
        actual = normalize_text(self.prediction.location)
        return bool(expected and actual and (expected in actual or actual in expected))

    @property
    def failure_type(self) -> str | None:
        if self.prediction.parse_error:
            return "parse_error"
        if self.binary_correct and self.cwe_correct:
            return None
        if self.prediction.vulnerable is not self.sample.vulnerable:
            return "wrong_binary_label"
        if not self.cwe_correct:
            return "wrong_cwe"
        if self.sample.vulnerable and not self.location_correct:
            return "wrong_location"
        return None


def normalize_cwe(value: str | None) -> str | None:
    if not value:
        return None
    text = str(value).strip().upper().replace("_", "-")
    if text.isdigit():
        return f"CWE-{text}"
    if text.startswith("CWE") and not text.startswith("CWE-"):
        return text.replace("CWE", "CWE-", 1)
    return text


def normalize_text(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())
