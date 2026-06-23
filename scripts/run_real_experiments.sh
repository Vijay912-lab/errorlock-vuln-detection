#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m errorlock.cli download-castle --out data/CASTLE-C250.min.json

ollama pull qwen2.5-coder:0.5b
ollama pull qwen2.5-coder:1.5b

python3 -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider ollama \
  --model qwen2.5-coder:0.5b \
  --limit 20 \
  --out-dir results/qwen2_5_coder_0_5b_limit20

python3 -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider ollama \
  --model qwen2.5-coder:0.5b \
  --limit 20 \
  --top-k 1 \
  --out-dir results/qwen2_5_coder_0_5b_limit20_topk1

python3 -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider ollama \
  --model qwen2.5-coder:0.5b \
  --limit 20 \
  --top-k 5 \
  --out-dir results/qwen2_5_coder_0_5b_limit20_topk5

python3 -m errorlock.cli run \
  --dataset data/CASTLE-C250.min.json \
  --provider ollama \
  --model qwen2.5-coder:1.5b \
  --limit 20 \
  --out-dir results/qwen2_5_coder_1_5b_limit20

python3 -m errorlock.analysis --results-dir results --out results/aggregate_analysis.md
