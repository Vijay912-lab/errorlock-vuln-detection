# ErrorLock

**SQLite-backed mistake memory for LLM-based C vulnerability detection.**

A CS541 (Database Systems) research project. ErrorLock stores an LLM's past prediction mistakes in SQLite and retrieves similar ones at inference time, giving the model a "second chance" to fix repeated errors — especially wrong CWE classifications and missed vulnerability patterns.

> **Best result:** On the full CASTLE-C250 benchmark, ErrorLock improved F1 from **0.616 → 0.709** and CWE correctness from **0.433 → 0.520** (GPT-OSS-120B + gated RAG).  
> For Qwen2.5-Coder 0.5B, CWE correctness improved from **0.027 → 0.200** while preserving binary F1.

---

## What problem does this solve?

LLMs that detect code vulnerabilities tend to repeat the same mistakes: assigning the wrong CWE type, missing a pattern they've seen before, or confusing similar-looking safe and unsafe code. Standard prompting discards each prediction immediately.

ErrorLock treats incorrect predictions as **database records**, not lost information. When a similar code sample appears later, the stored mistakes are retrieved and injected into the prompt — effectively giving the model a searchable memory of its own past failures.

---

## Architecture

```
CASTLE-C250 dataset (250 labeled C code samples)
  │
  ├─► Train split (40%)
  │     └─► Baseline LLM prompt → parse JSON → compare to ground truth
  │               └─► wrong? → INSERT into SQLite mistakes table
  │
  └─► Test split (60%)
        └─► Baseline LLM prompt → baseline prediction
              └─► SELECT similar mistakes by TF-IDF code similarity
                    └─► [gating logic] → worth re-prompting?
                          └─► ErrorLock prompt (baseline + retrieved mistakes)
                                └─► final prediction → evaluate vs. ground truth
```

The `mistakes` table stores: model name, sample ID, source code, true label, true CWE/location, predicted label/CWE/location, failure type, and raw model response. Retrieval uses a blended score: **70% character n-gram TF-IDF + 30% identifier token similarity**, with small boosts when the retrieved mistake shares the same predicted vulnerability class or CWE.

---

## Key Features

- **SQLite mistake memory** — persistent, queryable; indexed on model, failure type, and CWE
- **Blended TF-IDF retrieval** — char n-gram + identifier token similarity over stored code
- **RAG mode** — retrieves top-25 candidates, reranks with MMR diversity, selects top-6 for context
- **Gated inference** — skips reprompting when: low similarity, baseline already says "not vulnerable", near-duplicate false positive, baseline already has a full CWE answer
- **Binary-lock mode** — ErrorLock only fixes CWE/location; the vulnerable/not-vulnerable call stays with the baseline to avoid regression
- **Multi-provider** — Mock, Ollama (local), HuggingFace, OpenRouter, Groq, Gemini, OpenAI-compatible

---

## Results Summary

| Model | Split | Baseline F1 | ErrorLock F1 | Baseline CWE | ErrorLock CWE |
|---|---|---:|---:|---:|---:|
| GPT-OSS-120B | Full C250 | 0.616 | **0.709** | 0.433 | **0.520** |
| Qwen2.5-Coder 1.5B | Full C250 | 0.762 | 0.762 | 0.127 | **0.220** |
| Qwen2.5-Coder 0.5B | Full C250 | 0.773 | 0.773 | 0.027 | **0.200** |
| DeepSeek-Coder 1.3B | Full C250 | 0.782 | **0.785** | 0.000 | 0.020 |
| Qwen2.5-Coder 1.5B | Limit-20 | 0.824 | 0.824 | 0.500 | **0.667** |
| Qwen2.5-Coder 0.5B | Limit-20 | 0.737 | **0.800** | 0.000 | 0.500 |

Gated + binary-locked ErrorLock consistently preserves or improves binary F1 while improving CWE correctness. Full results in [`results/aggregate_analysis.md`](results/aggregate_analysis.md).

---

## Project Structure

```
errorlock/
├── schema.sql      # SQLite table definition + indexes
├── memory.py       # MistakeMemory: CRUD, TF-IDF retrieval, RAG builder
├── runner.py       # Benchmark orchestrator + gating/merge logic
├── prompts.py      # Baseline and ErrorLock prompt builders
├── parser.py       # JSON response parser
├── providers.py    # LLM provider implementations
├── metrics.py      # Accuracy, F1, CWE/location correctness
├── cli.py          # CLI entry point
└── types.py        # Dataclasses: CastleSample, Prediction, ScoredPrediction

data/               # CASTLE-C250 dataset (JSON)
results/            # Per-run predictions.csv, summary.json, report.md, SQLite DB
tests/              # Unit tests for parser, runner, memory
latex_report/       # ACM-format paper source
CS541_ErrorLock_Final.ipynb  # Jupyter notebook with full analysis
```

---

## Setup

```bash
git clone <this-repo>
cd CS541-Course-Project-Error-Lock
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For Hugging Face local model runs:

```bash
pip install -r requirements-hf.txt
```

---

## Quick Start (no GPU required)

Run the deterministic mock detector to verify the pipeline without downloading any models:

```bash
python -m errorlock.cli run \
  --dataset data/sample/sample_castle.json \
  --provider mock \
  --out-dir results/mock_smoke
```

Outputs: `predictions.csv`, `summary.json`, `report.md`, `errorlock.sqlite`

---

## Running with Local LLMs (Ollama)

```bash
ollama pull qwen2.5-coder:1.5b

# Baseline vs. ErrorLock (gated + binary-locked):
python -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider ollama \
  --model qwen2.5-coder:1.5b \
  --gated \
  --min-similarity 0.18 \
  --out-dir results/qwen1_5b_gated
```

## RAG Memory Mode

```bash
python -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider ollama \
  --model qwen2.5-coder:1.5b \
  --gated \
  --rag-memory \
  --rag-candidate-k 25 \
  --rag-context-k 6 \
  --out-dir results/qwen1_5b_rag
```

## API Models (OpenRouter, Groq, Gemini, OpenAI)

Copy `.env.example` to `.env` and fill in your API key, then:

```bash
python -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider openrouter \
  --model openai/gpt-oss-120b:free \
  --gated \
  --rag-memory \
  --out-dir results/gpt120b_rag_gated
```

See [`API_MODELS.md`](API_MODELS.md) for all supported providers and model IDs.

---

## How the Gating Works

Gated mode (`--gated`) prevents ErrorLock from making things worse:

| Gate condition | Action |
|---|---|
| No mistakes in memory | Skip (no data to help) |
| Best similarity < 0.18 | Skip (retrieved mistakes are unrelated) |
| Near-duplicate of a known false positive | Skip (would repeat the mistake) |
| Baseline says "not vulnerable" | Skip by default (avoids false-positive inflation) |
| Baseline already has a full CWE answer | Skip unless CWE recheck evidence found |
| Otherwise | Apply ErrorLock repair prompt |

Binary-lock (`--allow-binary-change` is off by default) means ErrorLock can only refine the CWE and location fields — it cannot flip the vulnerable/not-vulnerable decision, which prevents F1 regression.

---

## Metrics

Each run reports: accuracy, precision, recall, F1, parse failure rate, binary correctness rate, CWE correctness rate, location correctness rate, failure type breakdown, confusion matrix.

---

## Download the Full CASTLE Dataset

```bash
python -m errorlock.cli download-castle --out data/CASTLE-C250.min.json
```

---

## Tests

```bash
pytest tests/
```

---

## Paper

The full write-up (ACM format) is in [`latex_report/`](latex_report/). A rendered summary is in [`FINAL_REPORT.md`](FINAL_REPORT.md).

---

## Tech Stack

Python 3.11 · SQLite (WAL mode) · scikit-learn (TF-IDF, cosine similarity) · pandas · Ollama · HuggingFace Transformers · OpenAI-compatible APIs
