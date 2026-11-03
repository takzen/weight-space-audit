#!/bin/bash
# Creates an isolated environment for the sampling-control experiment. Touches nothing outside ~/qwen-control.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
ROOT="$HOME/qwen-control"
mkdir -p "$ROOT"
cd "$ROOT"
uv venv --python 3.12 .venv
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install "vllm==0.33.0" "math-verify[antlr4_13_2]" datasets safetensors numpy huggingface_hub
python - <<'PY'
import torch, vllm, transformers, math_verify
print("torch", torch.__version__, "cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
print("vllm", vllm.__version__, "transformers", transformers.__version__)
print("math_verify ok")
PY
echo ENV_READY
