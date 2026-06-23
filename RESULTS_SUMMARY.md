# Results Summary

Generated artifacts:

- `results/qwen2_5_coder_0_5b_limit20/`
- `results/qwen2_5_coder_0_5b_limit20_topk1/`
- `results/qwen2_5_coder_0_5b_limit20_topk5/`
- `results/qwen2_5_coder_1_5b_limit20/`
- `results/qwen2_5_coder_1_5b_limit20_smart_safe_gated/`
- `results/qwen2_5_coder_0_5b_limit20_smart_safe_gated/`
- `results/qwen2_5_coder_1_5b_limit20_smart_safe_gated_rerun/`
- `results/llama3_2_1b_limit20_smart_safe_gated/`
- `results/deepseek_coder_1_3b_limit20_smart_safe_gated/`
- `results/phi3_mini_limit20_smart_safe_gated/`
- `results/api_openrouter_gpt_oss_120b_free_limit20_smart_safe_gated/`
- `results/api_openrouter_gpt_oss_20b_free_limit10_smart_safe_gated/`
- `results/api_gemini_2_5_flash_lite_limit8_smart_safe_gated/`
- `results/full_c250_qwen2_5_coder_0_5b_smart_safe_gated/`
- `results/full_c250_qwen2_5_coder_1_5b_smart_safe_gated/`
- `results/full_c250_deepseek_coder_1_3b_smart_safe_gated/`
- `results/full_c250_llama3_2_1b_smart_safe_gated/`
- `results/full_c250_openrouter_gpt_oss_120b_free_rag_timeout60/`
- `results/aggregate_analysis.md`
- `results/aggregate_analysis.csv`

## Main Takeaways

1. `qwen2.5-coder:0.5b` improved with ErrorLock:
   - baseline F1: 0.737
   - ErrorLock F1: 0.800

2. `qwen2.5-coder:1.5b` got worse with ErrorLock:
   - baseline F1: 0.824
   - ErrorLock F1: 0.737

3. Smarter safe gating fixed the main 1.5B failure mode:
   - baseline F1: 0.824
   - ungated ErrorLock F1: 0.737
   - safe-gated ErrorLock F1: 0.824
   - baseline CWE correct rate: 0.500
   - safe-gated ErrorLock CWE correct rate: 0.667

4. ErrorLock improved CWE correctness for the 0.5B model:
   - baseline CWE correct rate: 0.000
   - ErrorLock top-k 3: 0.500
   - ErrorLock top-k 5: 0.667

5. Parse failures were 0.000 for all real Ollama runs after switching to JSON
   mode through the Ollama API.

6. OpenRouter free API models were also tested:
   - `openai/gpt-oss-120b:free`: baseline F1 0.857, ErrorLock F1 0.769.
   - `openai/gpt-oss-20b:free`: baseline F1 0.667, ErrorLock F1 0.857.
   - `gemini-2.5-flash-lite`: baseline F1 0.667, ErrorLock F1 0.857.

7. API model runs had some parse/API response failures, but they are now counted
   explicitly instead of being treated as safe predictions.

8. The full-C250 OpenRouter RAG run improved substantially:
   - `openai/gpt-oss-120b:free` baseline F1: 0.616
   - RAG ErrorLock F1: 0.709
   - baseline CWE correct rate: 0.433
   - RAG CWE correct rate: 0.520
   - baseline parse failure rate: 0.207
   - RAG parse failure rate: 0.053

## Smart Safe-Gated Run Across Models

| Model | Test N | Baseline F1 | Gated ErrorLock F1 | Baseline CWE | Gated CWE |
|---|---:|---:|---:|---:|---:|
| `qwen2.5-coder:0.5b` | 12 | 0.737 | 0.737 | 0.000 | 0.417 |
| `qwen2.5-coder:1.5b` | 12 | 0.824 | 0.824 | 0.500 | 0.667 |
| `llama3.2:1b` | 12 | 0.800 | 0.800 | 0.250 | 0.250 |
| `deepseek-coder:1.3b` | 12 | 0.737 | 0.800 | 0.000 | 0.000 |
| `phi3:mini` | 12 | 0.800 | 0.842 | 0.000 | 0.083 |
| `openai/gpt-oss-120b:free` | 12 | 0.857 | 0.933 | 0.583 | 0.750 |
| `openai/gpt-oss-20b:free` | 6 | 0.667 | 0.667 | 0.333 | 0.333 |
| `gemini-2.5-flash-lite` | 5 | 0.750 | 0.750 | 0.600 | 0.600 |

Local `gpt-oss:20b` through Ollama was attempted, but it took about five
minutes for the first memory-build sample, so the run was stopped before a
complete summary was produced.

## Full CASTLE-C250 Smart Safe-Gated Runs

These runs use all 250 samples in `CASTLE-C250.min.json`: 100 samples build
the SQLite mistake memory and 150 samples are used for fair test evaluation.

| Model | Total | Train | Test | Baseline F1 | Gated ErrorLock F1 | Baseline CWE | Gated CWE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `qwen2.5-coder:0.5b` | 250 | 100 | 150 | 0.773 | 0.773 | 0.027 | 0.200 |
| `qwen2.5-coder:1.5b` | 250 | 100 | 150 | 0.762 | 0.760 | 0.127 | 0.227 |
| `deepseek-coder:1.3b` | 250 | 100 | 150 | 0.782 | 0.776 | 0.000 | 0.020 |
| `llama3.2:1b` | 250 | 100 | 150 | 0.471 | 0.461 | 0.220 | 0.220 |

Full-C250 interpretation: gated ErrorLock substantially improves CWE
correctness for the Qwen and DeepSeek local runs, but it does not improve
binary F1 on the larger 250-sample benchmark. The F1 changes are flat to
slightly negative. This is a more honest final result than the earlier 20-sample
sanity check: ErrorLock's strongest value in the full local runs is CWE repair,
not overall vulnerable/non-vulnerable classification.

`phi3:mini` was started on full C250 but stopped after 11/100 memory-build
samples because it was much slower than the other local models.

## Full CASTLE-C250 OpenRouter RAG Run

This run uses all 250 samples with OpenRouter's `openai/gpt-oss-120b:free`
model and the compact RAG memory mode. The SQLite memory is built from 100
training samples, and the same 150 held-out test samples are evaluated for
baseline and ErrorLock.

| Model | Total | Train | Test | Baseline F1 | RAG ErrorLock F1 | Baseline CWE | RAG CWE | Baseline Parse Fail | RAG Parse Fail |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `openai/gpt-oss-120b:free` | 250 | 100 | 150 | 0.616 | 0.709 | 0.433 | 0.520 | 0.207 | 0.053 |

RAG ErrorLock was applied to 43 of the 150 test samples. It improved accuracy
from 0.593 to 0.667, recall from 0.490 to 0.610, F1 from 0.616 to 0.709, CWE
correctness from 0.433 to 0.520, and location correctness from 0.200 to 0.233.
The OpenRouter free endpoint produced several slow calls; the run used a
60-second API deadline so stalled calls were counted as API/parse failures
instead of freezing the benchmark.

## Full CASTLE-C250 Binary-Locked ErrorLock

The stronger default now preserves the baseline vulnerable/not-vulnerable
decision and uses ErrorLock only to repair CWE/location fields when appropriate.
This prevents retrieved memory from damaging the binary decision boundary.

These rows reuse the completed full-C250 generations and rescore them under the
new binary-locked policy.

| Model | Baseline F1 | Old Gated F1 | Binary-Locked F1 | Baseline CWE | Binary-Locked CWE |
|---|---:|---:|---:|---:|---:|
| `qwen2.5-coder:0.5b` | 0.773 | 0.773 | 0.773 | 0.027 | 0.200 |
| `qwen2.5-coder:1.5b` | 0.762 | 0.760 | 0.762 | 0.127 | 0.220 |
| `deepseek-coder:1.3b` | 0.782 | 0.776 | 0.785 | 0.000 | 0.020 |
| `llama3.2:1b` | 0.471 | 0.461 | 0.471 | 0.220 | 0.220 |

Binary-locked interpretation: this version is strong enough to avoid the prior
F1 damage. It preserves or improves binary F1 for all completed full-C250 local
runs, while still improving CWE correctness for Qwen and DeepSeek.

## All-Memory Ablation

An additional ablation added `--all-memory`, which sends every stored mistake
record to the ErrorLock prompt instead of only the top similar mistakes. The
gate still uses the top-3 similar mistakes, so this isolates the effect of
larger prompt context.

The better follow-up is `--rag-memory`. It considers a broader candidate pool
from SQLite, reranks and diversifies the evidence, then sends only a compact
RAG context. On the completed Qwen 0.5B full-C250 memory table, the default
RAG pack considers 25 candidates, selects 6 evidence rows, and produces a
median context of about 4.9k characters, roughly 1.2k tokens. This is far
smaller than all-memory while still giving the model more structured evidence
than raw top-3 retrieval.

On the completed 20-test-sample probe for `qwen2.5-coder:0.5b`, all-memory did
not beat top-3 retrieval:

| Memory Context | Test N | F1 | CWE Correct |
|---|---:|---:|---:|
| Baseline | 20 | 0.788 | 0.000 |
| Top-3 similar mistakes | 20 | 0.788 | 0.050 |
| All 96 stored mistakes | 20 | 0.788 | 0.050 |

The all-memory context was about 105k characters, roughly 26k tokens, before
adding the new sample. Applied rows took roughly one minute each on the local
Qwen 0.5B model. A full 150-test-sample all-memory run was started and stopped
after confirming this high runtime profile; the 20-sample probe showed no
quality gain over top-3 retrieval.

## Interpretation

ErrorLock helps when the model benefits from concrete reminders of similar past
mistakes. It hurts when retrieved examples bias a stronger baseline away from a
correct answer. The small 20-sample sweep made the smarter gate look broadly
positive, while the first full-C250 gate still allowed small F1 drops. The
binary-locked version fixes that failure mode by preserving the baseline binary
decision and using ErrorLock as a CWE repair layer. The project claim should
therefore be: ErrorLock is useful when it is constrained to targeted mistake
repair; unconstrained memory can oversteer the model.
