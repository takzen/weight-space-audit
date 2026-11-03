#!/bin/bash
# Throughput test only. Uses MATH-500 problems OUTSIDE the fixed subset, and the answers are not part of any result.
source "$HOME/qwen-control/.venv/bin/activate"
S=/mnt/c/projects/art/qwen-sampling-control/scripts
Q=$HOME/qwen-control
python - <<'PY'
import hashlib, json, struct
from pathlib import Path
root = Path.home() / "qwen-control"
man = json.loads((root / "edits/p50c/manifest.json").read_text())
for ckpt, key in (("text", "base_sha256"), ("p50c", "edited_sha256")):
    path = root / "models" / ckpt / "model.safetensors"
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        head = json.loads(f.read(n))
        for t in man["tensors"]:
            a, b = head[t["name"]]["data_offsets"]
            f.seek(8 + n + a)
            ok = hashlib.sha256(f.read(b - a)).hexdigest() == t[key]
            print(ckpt, t["name"].split("layers.")[1], key, "OK" if ok else "MISMATCH")
PY
mkdir -p "$Q/speed"; rm -f "$Q/speed/bench.jsonl"
python "$S/run_cond.py" --ckpt "$Q/models/text" --bench "$Q/bench/math500.jsonl" --exclude-ids "$Q/bench/math500_subset100.json" \
  --limit 40 --out "$Q/speed/bench.jsonl" --temperature 0.6 --top-p 0.95 --top-k 20 --presence 1.5 --max-tokens 32768 \
  --thinking --max-num-seqs "$1" --time-limit "$2" &
PID=$!
sleep 100
for i in 1 2 3 4 5; do nvidia-smi --query-gpu=memory.used,utilization.gpu,temperature.gpu,power.draw --format=csv,noheader; sleep 20; done
wait $PID
