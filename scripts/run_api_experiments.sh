#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m errorlock.cli download-castle --out data/CASTLE-C250.min.json

# Requires OPENROUTER_API_KEY. OpenRouter has a free-model collection, but
# individual model availability/rate limits can change.
if [[ -n "${OPENROUTER_API_KEY:-}" ]]; then
  python3 -m errorlock.cli run \
    --dataset data/CASTLE-C250.min.json \
    --provider openrouter \
    --model openai/gpt-oss-120b:free \
    --limit 20 \
    --out-dir results/api_openrouter_gpt_oss_120b_free_limit20

  python3 -m errorlock.cli run \
    --dataset data/CASTLE-C250.min.json \
    --provider openrouter \
    --model openai/gpt-oss-20b:free \
    --limit 10 \
    --out-dir results/api_openrouter_gpt_oss_20b_free_limit10
fi

# Requires GROQ_API_KEY. Groq has free-plan limits and an OpenAI-compatible API.
if [[ -n "${GROQ_API_KEY:-}" ]]; then
  python3 -m errorlock.cli run \
    --dataset data/CASTLE-C250.min.json \
    --provider groq \
    --model openai/gpt-oss-20b \
    --limit 20 \
    --out-dir results/api_groq_gpt_oss_20b_limit20
fi

# Requires HF_TOKEN or HUGGINGFACEHUB_API_TOKEN.
if [[ -n "${HF_TOKEN:-}${HUGGINGFACEHUB_API_TOKEN:-}" ]]; then
  python3 -m errorlock.cli run \
    --dataset data/CASTLE-C250.min.json \
    --provider hf-api \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --limit 20 \
    --out-dir results/api_hf_llama_3_1_8b_limit20
fi

# Requires GEMINI_API_KEY or GOOGLE_API_KEY.
if [[ -n "${GEMINI_API_KEY:-}${GOOGLE_API_KEY:-}" ]]; then
  python3 -m errorlock.cli run \
    --dataset data/CASTLE-C250.min.json \
    --provider gemini \
    --model gemini-2.5-flash-lite \
    --limit 8 \
    --out-dir results/api_gemini_2_5_flash_lite_limit8
fi

# OpenAI is not a permanent free API, but if you have credits/key, this works.
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  python3 -m errorlock.cli run \
    --dataset data/CASTLE-C250.min.json \
    --provider openai \
    --model gpt-5.4-mini \
    --limit 20 \
    --out-dir results/api_openai_gpt_5_4_mini_limit20
fi

python3 -m errorlock.analysis --results-dir results --out results/aggregate_analysis.md
