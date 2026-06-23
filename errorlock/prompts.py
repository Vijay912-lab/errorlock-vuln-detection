from __future__ import annotations

from .memory import Mistake
from .types import CastleSample, Prediction

SYSTEM_INSTRUCTIONS = """You are a careful C vulnerability detection engine.
Return only a single JSON object with these keys:
{
  "vulnerable": true or false,
  "cwe": "CWE-###" or null,
  "location": "short line/function description" or null,
  "explanation": "one concise sentence"
}
Think through the evidence internally, but do not include chain-of-thought,
markdown, bullet points, or extra text. Return JSON only."""


def baseline_prompt(sample: CastleSample) -> str:
    return f"""{SYSTEM_INSTRUCTIONS}

Analyze this C code:

```c
{sample.code}
```"""


def errorlock_prompt(
    sample: CastleSample,
    mistakes: list[Mistake],
    baseline: Prediction | None = None,
    preserve_binary_decision: bool = True,
    selective_binary_override: bool = False,
    memory_context: str | None = None,
) -> str:
    memory = memory_context or "\n\n".join(_format_mistake(m, i + 1) for i, m in enumerate(mistakes))
    if not memory:
        memory = "No prior mistakes were retrieved."
    baseline_text = _format_baseline(baseline)
    binary_policy = _binary_policy(baseline, preserve_binary_decision, selective_binary_override)
    return f"""{SYSTEM_INSTRUCTIONS}

You are running the ErrorLock repair pass. A baseline detector already made a
prediction. Your job is to use retrieved historical mistakes to catch repeated
error patterns, especially wrong CWE or wrong location.

Baseline prediction:
{baseline_text}

Binary-label policy:
{binary_policy}

Use the retrieved mistakes as warnings, not examples to copy. For each relevant
mistake, internally check:
1. What code pattern is similar?
2. What code pattern is different?
3. Does the difference change the vulnerability label?
4. Does the memory indicate a repeated CWE confusion?

Final self-check before output:
- If the binary label is fixed by policy, keep it exactly fixed.
- If vulnerable=false, cwe and location must be null.
- If vulnerable=true, return the best supported CWE and location.
- Do not copy a CWE from memory unless the new code supports it.

{memory}

Now analyze this new C code:

```c
{sample.code}
```"""


def _format_baseline(prediction: Prediction | None) -> str:
    if prediction is None or not prediction.parsed:
        return "No parsed baseline prediction is available."
    return (
        "{"
        f'"vulnerable": {str(prediction.vulnerable).lower()}, '
        f'"cwe": {_jsonish(prediction.cwe)}, '
        f'"location": {_jsonish(prediction.location)}, '
        f'"explanation": {_jsonish(prediction.explanation)}'
        "}"
    )


def _binary_policy(
    prediction: Prediction | None,
    preserve_binary_decision: bool,
    selective_binary_override: bool,
) -> str:
    if not preserve_binary_decision or prediction is None or not prediction.parsed:
        return "You may change the binary label if the code evidence clearly supports the change."
    fixed = str(prediction.vulnerable).lower()
    if selective_binary_override:
        return (
            f"Default to vulnerable={fixed}. Change it only if the retrieved mistakes "
            "show a highly similar repeated false-positive or false-negative pattern "
            "and the new code evidence independently supports the change."
        )
    return f"The binary label is locked. You must output vulnerable={fixed}."


def _jsonish(value: str | None) -> str:
    if value is None:
        return "null"
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _format_mistake(mistake: Mistake, index: int) -> str:
    return f"""Prior mistake {index} (similarity={mistake.similarity:.3f})
Failure type: {mistake.failure_type}
True label: vulnerable={mistake.true_vulnerable}, cwe={mistake.true_cwe}, location={mistake.true_location}
Wrong prediction: vulnerable={mistake.predicted_vulnerable}, cwe={mistake.predicted_cwe}, location={mistake.predicted_location}
Lesson: avoid repeating this failure only when the new code has the same security-relevant pattern.
Code:
```c
{mistake.code[:1800]}
```"""
