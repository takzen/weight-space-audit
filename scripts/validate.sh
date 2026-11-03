#!/bin/bash
source "$HOME/qwen-control/.venv/bin/activate"
S=/mnt/c/projects/art/qwen-sampling-control/scripts
mkdir -p "$HOME/qwen-control/authors"
cp -r "$1" "$HOME/qwen-control/authors/eval"
python "$S/validate_grader.py" "$HOME/qwen-control/authors/eval"
python - <<'PY'
import vllm, inspect, torch
from vllm.v1.engine.llm_engine import LLMEngine
print("vllm", vllm.__version__, "torch", torch.__version__, "cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0))
print("add_request", inspect.signature(LLMEngine.add_request))
from vllm import LLM
for n in ("_add_request","_run_engine","generate","get_tokenizer","_add_completion_requests","_render_and_add_requests"):
    if hasattr(LLM,n): print(n, inspect.signature(getattr(LLM,n)))
print([n for n in dir(LLM) if not n.startswith('__')][:60])
PY
