"""The non-LLM baseline for Experiment 1: the per-cell size of the first layer's weights, drawn as a 10 x 10 picture.

An input cell that is never active gets no gradient, so its outgoing weights stay at their small starting values. Cells the
game actually uses grow. One line of numpy therefore draws the game's board. No forward pass and no LLM are involved.

  python exp1_maps.py <authors_exp1_networks_dir> <out.json>
"""
import json
import sys

import numpy as np

NETS = {"breakout": "a9f535cc", "pong": "dfc6cb65", "pacman": "bdf99279", "freeway": "0bbcc3ea"}
CHANNELS = ["agent", "moving", "reward", "obstacle", "previous"]

base, out_path = sys.argv[1], sys.argv[2]
out = {}
for game, net in NETS.items():
    with np.load(f"{base}/{net}.npz", allow_pickle=False) as d:
        keys = [k for k in d.files if d[k].ndim == 2 and 500 in d[k].shape]
        weights = d[keys[0]]
        key_note = keys[0]
    weights = weights if weights.shape[0] == 500 else weights.T
    maps = np.linalg.norm(weights, axis=1).reshape(10, 10, 5)  # the whole baseline is this line
    median = float(np.median(maps))
    out[game] = {"key": key_note, "median": median, "max": float(maps.max()),
                 "channels": {name: np.round(maps[:, :, i], 3).tolist() for i, name in enumerate(CHANNELS)}}
    print(f"--- {game}: key {key_note}, median {median:.3f}, max {maps.max():.2f}")
    for i, name in enumerate(CHANNELS):
        m = maps[:, :, i]
        print(f"  [{name}] share of cells above 2x median: {(m > 2 * median).mean():.2f}")
        for row in m:
            print("    " + "".join("#" if v > 2 * median else "+" if v > 1.2 * median else "." for v in row))
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f)
