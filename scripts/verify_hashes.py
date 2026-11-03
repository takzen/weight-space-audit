"""Checks both checkpoints against the sha256 values in the authors' published edit manifest."""
import hashlib
import json
import struct
from pathlib import Path

root = Path.home() / "qwen-control"
man = json.loads((root / "edits/p50c/manifest.json").read_text())
ok_all = True
for ckpt, key in (("text", "base_sha256"), ("p50c", "edited_sha256")):
    path = root / "models" / ckpt / "model.safetensors"
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        head = json.loads(f.read(n))
        for t in man["tensors"]:
            a, b = head[t["name"]]["data_offsets"]
            f.seek(8 + n + a)
            ok = hashlib.sha256(f.read(b - a)).hexdigest() == t[key]
            ok_all &= ok
            print(ckpt, t["name"].split("layers.")[1], key, "OK" if ok else "MISMATCH", flush=True)
print("HASHES_OK" if ok_all else "HASHES_MISMATCH", flush=True)
