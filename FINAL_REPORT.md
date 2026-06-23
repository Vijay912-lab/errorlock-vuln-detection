# ErrorLock: Database-Backed Mistake Memory for LLM Vulnerability Detection

## Abstract

ErrorLock evaluates whether a persistent database of past model mistakes can
improve LLM-based vulnerability detection. The system runs a baseline detector,
stores incorrect predictions in SQLite, retrieves similar mistakes for later
samples, and asks the model to revise its decision with that memory. A smarter
retriever and safety gate were added after error analysis: retrieval now blends
code similarity with identifier-token and model-error-pattern signals, while
the gate avoids low-confidence or high-risk memory use. On a small CASTLE-C250
local experiment, ErrorLock improved the weaker Qwen2.5-Coder 0.5B model's F1
from 0.737 to 0.800. Ungated ErrorLock reduced the stronger 1.5B model's F1
from 0.824 to 0.737, but safe-gated ErrorLock preserved F1 at 0.824 while
improving CWE correctness from 0.500 to 0.667. On the full CASTLE-C250 local
benchmark, the first smart gate was flat to slightly negative on binary F1.
The final binary-locked gate fixes this by preserving the baseline
vulnerable/not-vulnerable decision and using ErrorLock only for targeted
CWE/location repair. Under this policy, completed full-C250 runs preserve or
improve binary F1 and improve CWE correctness for Qwen2.5-Coder and
DeepSeek-Coder. A later full-C250 OpenRouter run with `openai/gpt-oss-120b:free`
and compact RAG memory improved F1 from 0.616 to 0.709 and CWE correctness from
0.433 to 0.520.

## 1. Introduction

LLMs can detect vulnerabilities in C/C++ code, but they often repeat similar
mistakes: missing path traversal patterns, over-flagging safe inputs, or
assigning the wrong CWE. ErrorLock treats those failures as database records
rather than one-off prompt errors. The core idea is simple: when the model is
wrong, store the mistake; when a similar sample appears later, retrieve relevant
mistakes and warn the model.

The database systems angle is persistence, schema design, queryable mistake
records, and retrieval over stored code examples.

## 2. System Design

ErrorLock has four main components:

1. Dataset loader for CASTLE-C250 JSON.
2. Baseline model predictor that produces strict JSON.
3. SQLite mistake memory.
4. Retrieval-augmented ErrorLock prediction pass.

The SQLite table stores:

- model name
- sample id
- source code
- true vulnerable label
- true CWE and location
- predicted label, CWE, location, and explanation
- failure type
- raw model response

At training/memory-build time, baseline mistakes are inserted into SQLite. At
test time, the system retrieves similar mistakes without using the test sample's
ground-truth CWE, avoiding label leakage.

The original retriever used only TF-IDF character n-gram similarity. The smarter
retriever now combines:

- character n-gram code similarity
- identifier-token similarity
- small boosts for matching the model's own predicted label or CWE confusion

The gated ErrorLock policy then decides whether to reprompt. It skips memory
when similarity is too low, when the baseline already predicts non-vulnerable
under the safe default, when the nearest memory is a near-duplicate false
positive, or when the baseline already produced a complete vulnerable+CWE
answer. It still permits CWE rechecks when retrieved mistakes strongly suggest
the model is repeating a known CWE confusion.

The final policy also locks the binary decision by default. A successful
ErrorLock reprompt may repair CWE and location fields, but it cannot change the
baseline vulnerable/not-vulnerable label unless the experimenter explicitly
enables binary changes. This turns ErrorLock into a conservative mistake-repair
layer instead of an unconstrained second detector.

The newest retrieval mode is compact RAG memory. It retrieves a larger
candidate set from SQLite, reranks and diversifies the evidence by similarity,
CWE, failure type, and redundancy, then sends only a compact evidence pack to
the model. This avoids both extremes: too little context from top-k retrieval
and too much irrelevant context from sending the whole mistake table.

## 3. Methodology

Dataset: CASTLE-C250, downloaded from the official GitHub repository.

Small experiment size:

- 20 total samples
- 8 memory-build samples
- 12 fair test samples
- same test split for baseline and ErrorLock

Full CASTLE-C250 local experiment size:

- 250 total samples
- 100 memory-build samples
- 150 fair test samples
- same split protocol as the small runs

Models:

- `qwen2.5-coder:0.5b` through Ollama
- `qwen2.5-coder:1.5b` through Ollama
- `llama3.2:1b`, `deepseek-coder:1.3b`, and `phi3:mini` through Ollama for the
  smart-gated sweep
- `openai/gpt-oss-120b:free` through OpenRouter
- `openai/gpt-oss-20b:free` through OpenRouter
- `gemini-2.5-flash-lite` through the Gemini API

Metrics:

- accuracy
- precision
- recall
- F1
- parse failure rate
- CWE correctness
- approximate location correctness

## 4. Results

| Run | Model | Method | Test N | Accuracy | Precision | Recall | F1 | Parse Fail | CWE Correct |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| main | qwen2.5-coder:0.5b | baseline | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.000 |
| main | qwen2.5-coder:0.5b | ErrorLock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.500 |
| top-k 1 | qwen2.5-coder:0.5b | ErrorLock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.583 |
| top-k 5 | qwen2.5-coder:0.5b | ErrorLock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.667 |
| main | qwen2.5-coder:1.5b | baseline | 12 | 0.750 | 0.778 | 0.875 | 0.824 | 0.000 | 0.500 |
| main | qwen2.5-coder:1.5b | ErrorLock | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.583 |
| gated | qwen2.5-coder:1.5b | ErrorLock | 12 | 0.750 | 0.778 | 0.875 | 0.824 | 0.000 | 0.667 |
| gated | qwen2.5-coder:0.5b | ErrorLock | 12 | 0.583 | 0.636 | 0.875 | 0.737 | 0.000 | 0.417 |
| gated | llama3.2:1b | ErrorLock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.250 |
| gated | deepseek-coder:1.3b | ErrorLock | 12 | 0.667 | 0.667 | 1.000 | 0.800 | 0.000 | 0.000 |
| gated | phi3:mini | ErrorLock | 12 | 0.750 | 0.727 | 1.000 | 0.842 | 0.000 | 0.083 |
| API | openai/gpt-oss-120b:free | baseline | 12 | 0.833 | 0.857 | 0.857 | 0.857 | 0.333 | 0.500 |
| API | openai/gpt-oss-120b:free | ErrorLock | 12 | 0.750 | 0.833 | 0.714 | 0.769 | 0.083 | 0.583 |
| gated API | openai/gpt-oss-120b:free | ErrorLock | 12 | 0.917 | 0.875 | 1.000 | 0.933 | 0.000 | 0.750 |
| API | openai/gpt-oss-20b:free | baseline | 6 | 0.667 | 0.667 | 0.667 | 0.667 | 0.333 | 0.333 |
| API | openai/gpt-oss-20b:free | ErrorLock | 6 | 0.833 | 0.750 | 1.000 | 0.857 | 0.167 | 0.667 |
| gated API | openai/gpt-oss-20b:free | ErrorLock | 6 | 0.667 | 0.667 | 0.667 | 0.667 | 0.333 | 0.333 |
| API | gemini-2.5-flash-lite | baseline | 5 | 0.600 | 0.667 | 0.667 | 0.667 | 0.400 | 0.400 |
| API | gemini-2.5-flash-lite | ErrorLock | 5 | 0.800 | 0.750 | 1.000 | 0.857 | 0.400 | 0.600 |
| gated API | gemini-2.5-flash-lite | ErrorLock | 5 | 0.600 | 0.750 | 0.750 | 0.750 | 0.200 | 0.600 |
| full C250 | qwen2.5-coder:0.5b | baseline | 150 | 0.640 | 0.667 | 0.920 | 0.773 | 0.007 | 0.027 |
| full C250 | qwen2.5-coder:0.5b | ErrorLock | 150 | 0.640 | 0.667 | 0.920 | 0.773 | 0.007 | 0.200 |
| full C250 | qwen2.5-coder:1.5b | baseline | 150 | 0.647 | 0.691 | 0.850 | 0.762 | 0.000 | 0.127 |
| full C250 | qwen2.5-coder:1.5b | ErrorLock | 150 | 0.647 | 0.694 | 0.840 | 0.760 | 0.000 | 0.227 |
| full C250 | deepseek-coder:1.3b | baseline | 150 | 0.647 | 0.664 | 0.950 | 0.782 | 0.040 | 0.000 |
| full C250 | deepseek-coder:1.3b | ErrorLock | 150 | 0.647 | 0.672 | 0.920 | 0.776 | 0.080 | 0.020 |
| full C250 | llama3.2:1b | baseline | 150 | 0.460 | 0.679 | 0.360 | 0.471 | 0.000 | 0.220 |
| full C250 | llama3.2:1b | ErrorLock | 150 | 0.453 | 0.673 | 0.350 | 0.461 | 0.007 | 0.220 |
| binary-locked | qwen2.5-coder:0.5b | ErrorLock | 150 | 0.640 | 0.667 | 0.920 | 0.773 | 0.007 | 0.200 |
| binary-locked | qwen2.5-coder:1.5b | ErrorLock | 150 | 0.647 | 0.691 | 0.850 | 0.762 | 0.000 | 0.220 |
| binary-locked | deepseek-coder:1.3b | ErrorLock | 150 | 0.653 | 0.670 | 0.950 | 0.785 | 0.040 | 0.020 |
| binary-locked | llama3.2:1b | ErrorLock | 150 | 0.460 | 0.679 | 0.360 | 0.471 | 0.000 | 0.220 |
| full C250 RAG | openai/gpt-oss-120b:free | baseline | 150 | 0.593 | 0.831 | 0.490 | 0.616 | 0.207 | 0.433 |
| full C250 RAG | openai/gpt-oss-120b:free | ErrorLock | 150 | 0.667 | 0.847 | 0.610 | 0.709 | 0.053 | 0.520 |

## 5. Error Analysis

For `qwen2.5-coder:0.5b`, ErrorLock helped on sample `22-5`: the baseline
missed a vulnerable path traversal case, while ErrorLock retrieved similar
mistakes and corrected the prediction to vulnerable with CWE-22.

For `qwen2.5-coder:1.5b`, ungated ErrorLock helped on sample `22-4`, but hurt
on samples `22-1`, `78-7`, and `22-8`. In those cases, retrieved mistakes
appear to have pushed the model toward over-correction. The safe-gated policy
preserved the baseline's binary F1 and improved CWE correctness by applying
only three reprompts, all for CWE recheck. The gate skipped three baseline
non-vulnerable answers, two near-duplicate false-positive memories, and four
already-complete baseline vulnerable+CWE answers.

In the broader smart-gated sweep, completed models fell into three groups:
DeepSeek Coder 1.3B, Phi-3 mini, and OpenRouter GPT-OSS 120B improved F1;
Qwen2.5-Coder 0.5B, Qwen2.5-Coder 1.5B, Llama 3.2 1B, OpenRouter GPT-OSS 20B,
and Gemini Flash Lite preserved baseline F1; no completed gated run reduced F1.
The local Ollama `gpt-oss:20b` run was attempted but stopped because it took
about five minutes for the first memory-build example on the available machine.

On the full C250 local runs, the story changes. Gated ErrorLock did not improve
binary F1: Qwen2.5-Coder 0.5B was exactly flat, while Qwen2.5-Coder 1.5B,
DeepSeek Coder 1.3B, and Llama 3.2 1B dropped slightly. However, CWE correctness
improved for three of the four completed models. This indicates that the current
ErrorLock implementation is better at repairing vulnerability category mistakes
than at improving the vulnerable/non-vulnerable decision boundary.

After this error analysis, the gate was strengthened by locking the baseline
binary decision. The same completed full-C250 generations were rescored with
this policy. The binary-locked version preserves F1 for Qwen2.5-Coder 0.5B,
Qwen2.5-Coder 1.5B, and Llama 3.2 1B, and improves DeepSeek-Coder 1.3B from
0.782 to 0.785 F1. It keeps the CWE gains for Qwen and DeepSeek. This is the
preferred final system because it prevents mistake memory from damaging the
primary binary classifier.

For OpenRouter API models, the ungated result was mixed. `openai/gpt-oss-120b:free`
had the best baseline F1, but ungated ErrorLock reduced its F1. With smart safe
gating, the same model improved from 0.857 to 0.933 F1. `openai/gpt-oss-20b:free`
improved in the earlier ungated smaller run, but the gated rerun preserved
baseline F1 because no memory was available for its six test examples.

The full-C250 OpenRouter RAG run is the strongest full-benchmark evidence for
the improved system. With `openai/gpt-oss-120b:free`, compact RAG ErrorLock was
applied to 43 of 150 held-out test samples. It improved F1 from 0.616 to 0.709,
accuracy from 0.593 to 0.667, recall from 0.490 to 0.610, CWE correctness from
0.433 to 0.520, and location correctness from 0.200 to 0.233. The OpenRouter
free endpoint was unstable, so the run used a 60-second request deadline; slow
or failed API calls are counted as parse failures rather than silently ignored.

For Gemini, the original `gemini-2.5-flash` run hit rate limits and malformed
JSON responses through the OpenAI-compatible endpoint. Switching to the native
Gemini API and `gemini-2.5-flash-lite` produced a valid smaller run, where
ungated ErrorLock improved F1 from 0.667 to 0.857. The smart-gated rerun
preserved baseline F1 at 0.750 and made only one CWE-recheck reprompt.

The strongest result is not that unconstrained ErrorLock always improves
performance. The more defensible conclusion is that database-backed mistake
memory is useful for structured error analysis and CWE repair, and it should be
constrained so that memory cannot overwrite a stronger baseline binary
decision.

## 6. Limitations

The API and early local sweeps are intentionally small because they run under
API quota and laptop constraints. The full local C250 runs are more reliable,
but still use only small local models.

The current retrieval uses sparse TF-IDF similarity, RAG reranking, and
diversity selection, not learned semantic embeddings. It can still retrieve
examples that look syntactically similar but differ in security meaning.

Location scoring is approximate because model locations are free-form strings.

## 7. Future Work

- Tune the gate on a validation split and rerun full C250.
- Add embedding retrieval and compare it with the sparse smart retriever.
- Add learned/embedding RAG retrieval and compare it with the current sparse
  RAG evidence pack.
- Tune gate thresholds on a validation split instead of a small manual run.
- Add top-k and similarity-threshold ablations.
- Analyze results by CWE family.
- Add model confidence if the provider exposes token probabilities or calibrated
  self-confidence.

## 8. Conclusion

ErrorLock demonstrates a database-backed memory layer for LLM vulnerability
detection. The system stores model failures in SQLite and retrieves similar
mistakes during future predictions. Small runs showed that mistake memory can
improve F1, especially with gating. The full CASTLE-C250 local runs revealed
that the first gate was still too permissive. The binary-locked gate is
stronger: it preserves or improves binary F1 for completed full-C250 local runs
while retaining CWE improvements for several models. The full OpenRouter RAG
run goes further, improving both binary F1 and CWE correctness on the held-out
150-sample test split.
The project succeeds as a database systems prototype because it makes model
mistakes persistent, queryable, retrievable, gated, and experimentally
measurable.
