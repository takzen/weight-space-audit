"""Builds the two checkpoints used by the sampling-control experiment.

  ~/qwen-control/models/text   text-only export of Qwen/Qwen3.5-0.8B (same tensors and config as the post's experiment)
  ~/qwen-control/models/p50c   the same, with the published p50c weight edit applied (the post's "50 forward passes" model)

Tensor bytes are copied verbatim (no float conversion). The base tensors and the edited tensors are checked against the
sha256 values the authors published in exp8_math/runs/p50c/edit/manifest.json, so a successful run proves that these are
the weights the post evaluated.
"""
import hashlib
import json
import shutil
import struct
import urllib.request
from pathlib import Path

import numpy as np
from huggingface_hub import hf_hub_download

REPO = "Qwen/Qwen3.5-0.8B"
REV = "2fc06364715b967f1860aea9cf38778875588b17"
LOGS = "https://raw.githubusercontent.com/RikiyaT/lm_understand-logs/main/exp8_math"
ROOT = Path.home() / "qwen-control"
HF = ROOT / "models" / "hf"
TEXT = ROOT / "models" / "text"
EDITED = ROOT / "models" / "p50c"
EDIT = ROOT / "edits" / "p50c"
WEIGHTS = "model.safetensors-00001-of-00001.safetensors"
HF_FILES = (WEIGHTS, "tokenizer.json", "vocab.json", "merges.txt", "chat_template.jinja")
# config files of the text-only export, as published by the authors
AUTHOR_FILES = ("config.json", "generation_config.json", "tokenizer_config.json")
# copied next to the weights in both checkpoints
SIDE_FILES = ("tokenizer.json", "vocab.json", "merges.txt", "chat_template.jinja")


def fetch(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    with urllib.request.urlopen(url, timeout=120) as r:
        dest.write_bytes(r.read())


def read_header(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        return json.loads(f.read(n)), 8 + n


def write_safetensors(path, items):
    """items: {name: (dtype string, shape, bytes)}, written in name order."""
    head, off = {}, 0
    names = sorted(items)
    for name in names:
        dt, shape, blob = items[name]
        head[name] = {"dtype": dt, "shape": list(shape), "data_offsets": [off, off + len(blob)]}
        off += len(blob)
    head["__metadata__"] = {"format": "pt"}
    h = json.dumps(head, separators=(",", ":")).encode()
    h += b" " * (-len(h) % 8)
    with open(path, "wb") as f:
        f.write(struct.pack("<Q", len(h)))
        f.write(h)
        for name in names:
            f.write(items[name][2])


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    HF.mkdir(parents=True, exist_ok=True)
    for name in HF_FILES:
        hf_hub_download(REPO, name, revision=REV, local_dir=HF)
        print("have", name, flush=True)

    for name in AUTHOR_FILES:
        fetch(f"{LOGS}/base_model/Qwen3.5-0.8B-text/{name}", TEXT / name)
    fetch(f"{LOGS}/runs/p50c/edit/manifest.json", EDIT / "manifest.json")
    fetch(f"{LOGS}/runs/p50c/edit/edit.npz", EDIT / "edit.npz")

    head, data_start = read_header(HF / WEIGHTS)
    items = {}
    with open(HF / WEIGHTS, "rb") as f:
        for name, info in head.items():
            if name == "__metadata__" or not name.startswith("model.language_model."):
                continue
            a, b = info["data_offsets"]
            f.seek(data_start + a)
            items[name] = (info["dtype"], info["shape"], f.read(b - a))
    print(f"{len(items)} language-model tensors, {sum(len(v[2]) for v in items.values()) / 1e9:.2f} GB", flush=True)

    TEXT.mkdir(parents=True, exist_ok=True)
    write_safetensors(TEXT / "model.safetensors", items)
    for name in SIDE_FILES:
        shutil.copyfile(HF / name, TEXT / name)

    man = json.loads((EDIT / "manifest.json").read_text())
    z = np.load(EDIT / "edit.npz")  # numeric arrays only; allow_pickle stays False
    edited = dict(items)
    for i, t in enumerate(man["tensors"]):
        dt, shape, blob = items[t["name"]]
        assert dt == "BF16" and list(shape) == t["shape"], (t["name"], dt, shape)
        assert t["form"] == "sparse", t["form"]
        got = sha(blob)
        assert got == t["base_sha256"], f"{t['name']}: base tensor differs from the one the edit was made on"
        bits = np.frombuffer(blob, dtype=np.uint16).copy().reshape(-1)
        bits[z[f"t{i}_idx"]] = z[f"t{i}_val"]
        new = bits.reshape(shape).tobytes()
        got = sha(new)
        assert got == t["edited_sha256"], f"{t['name']}: rebuilt tensor does not match the evaluated checkpoint"
        edited[t["name"]] = (dt, shape, new)
        print(f"{t['name']}: base and edited sha256 match the authors' manifest", flush=True)

    EDITED.mkdir(parents=True, exist_ok=True)
    write_safetensors(EDITED / "model.safetensors", edited)
    for name in AUTHOR_FILES:
        shutil.copyfile(TEXT / name, EDITED / name)
    for name in SIDE_FILES:
        shutil.copyfile(HF / name, EDITED / name)

    (HF / WEIGHTS).unlink()  # the two exports hold everything needed; frees 1.7 GB
    print("MODEL_READY", flush=True)


if __name__ == "__main__":
    main()
