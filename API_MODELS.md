# Free/Free-Tier API Models

The benchmark now supports API providers that expose OpenAI-compatible chat
completions.

## Important

These are free-tier APIs, not anonymous public endpoints. You still need a
provider API key. No key is currently set in this shell environment.

## Supported Providers

### OpenRouter

Environment:

```bash
export OPENROUTER_API_KEY="..."
```

Example free model runs:

```bash
python3 -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider openrouter \
  --model openai/gpt-oss-120b:free \
  --limit 20 \
  --out-dir results/api_openrouter_gpt_oss_120b_free_limit20
```

Other free OpenRouter model IDs can be selected from OpenRouter's free model
collection. Availability and limits can change. During this run,
`google/gemma-3-27b-it:free` returned 404, so the script uses currently listed
GPT-OSS free models instead.

### Groq

Environment:

```bash
export GROQ_API_KEY="..."
```

Example:

```bash
python3 -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider groq \
  --model openai/gpt-oss-20b \
  --limit 20 \
  --out-dir results/api_groq_gpt_oss_20b_limit20
```

### Hugging Face Inference Providers

Environment:

```bash
export HF_TOKEN="..."
```

Example:

```bash
python3 -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider hf-api \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --limit 20 \
  --out-dir results/api_hf_llama_3_1_8b_limit20
```

### Gemini

Environment:

```bash
export GEMINI_API_KEY="..."
```

Example:

```bash
python3 -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider gemini \
  --model gemini-2.5-flash-lite \
  --limit 20 \
  --out-dir results/api_gemini_2_5_flash_lite_limit20
```

### OpenAI

OpenAI is supported for completeness, but it is generally not a permanent free
API. Use it only if you have credits or an API key.

Environment:

```bash
export OPENAI_API_KEY="..."
```

Example:

```bash
python3 -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider openai \
  --model gpt-5.4-mini \
  --limit 20 \
  --out-dir results/api_openai_gpt_5_4_mini_limit20
```

## Run All Configured API Experiments

```bash
./scripts/run_api_experiments.sh
```

The script automatically skips providers whose API keys are not set.

## Completed API Runs In This Workspace

Using OpenRouter:

- `openai/gpt-oss-120b:free`, 20-sample run
- `openai/gpt-oss-20b:free`, 10-sample run
- `gemini-2.5-flash-lite`, 8-sample run

The attempted `meta-llama/llama-3.3-70b-instruct:free` run hit OpenRouter rate
limits, so it was not kept as a valid result.
