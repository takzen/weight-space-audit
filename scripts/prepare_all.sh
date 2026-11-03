#!/bin/bash
set -euo pipefail
source "$HOME/qwen-control/.venv/bin/activate"
S=/mnt/c/projects/art/qwen-sampling-control/scripts
python "$S/prepare_model.py"
python "$S/prepare_bench.py" "$HOME/qwen-control/bench"
ls -la "$HOME/qwen-control/models/text" "$HOME/qwen-control/models/p50c" | cut -c1-120
