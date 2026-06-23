from __future__ import annotations

import json
import re
from typing import Any

from .types import Prediction, normalize_cwe


def parse_prediction(text: str) -> Prediction:
    raw = text or ""
    try:
        data = _extract_json(raw)
        vulnerable = _parse_bool(_get(data, "vulnerable", "is_vulnerable", "label"))
        return Prediction(
            vulnerable=vulnerable,
            cwe=normalize_cwe(_get(data, "cwe", "cwe_id", "weakness")),
            location=_as_str(_get(data, "location", "line", "vulnerable_location")),
            explanation=_as_str(_get(data, "explanation", "reason", "rationale")),
            raw=raw,
        )
    except Exception as exc:
        return Prediction(vulnerable=None, raw=raw, parse_error=str(exc))


def _extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped, flags=re.I).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, flags=re.S)
        if not match:
            raise ValueError("no JSON object found")
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("JSON response is not an object")
    return data


def _get(data: dict[str, Any], *keys: str) -> Any:
    lower = {str(k).lower(): v for k, v in data.items()}
    for key in keys:
        if key in data:
            return data[key]
        if key.lower() in lower:
            return lower[key.lower()]
    return None


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "yes", "1", "vulnerable", "buggy"}:
        return True
    if text in {"false", "no", "0", "safe", "clean", "not vulnerable"}:
        return False
    raise ValueError(f"cannot parse vulnerable field: {value!r}")


def _as_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)
