"""Second scoring of Astra's Breakout network with new seeds and float32 weights, to see whether 493 against the published 517 is noise."""
import json
import multiprocessing as mp
import sys

import numpy as np
from minatar import Environment

sys.path.insert(0, "/mnt/c/projects/art/qwen-sampling-control/scripts")
from minatar_control import MAX_STEPS, SOURCES  # noqa: E402

PATH = sys.argv[1]


def play(job):
    seed, episodes = job
    env = Environment("breakout", sticky_action_prob=0.1)
    env.seed(seed)
    rng = np.random.default_rng(seed + 1)
    n = np.load(PATH, allow_pickle=False)
    W1, b1, W2, b2 = n["actor/dense1/kernel"], n["actor/dense1/bias"], n["actor/dense2/kernel"], n["actor/dense2/bias"]
    W3, b3 = n["actor/logits/kernel"], n["actor/logits/bias"]
    src = SOURCES["breakout"]
    out = []
    for _ in range(episodes):
        env.reset()
        total, steps, terminal = 0, 0, False
        while not terminal and steps < MAX_STEPS:
            s = env.state()
            g = np.zeros((10, 10, 6), dtype=np.float32)
            for ch, c in src.items():
                g[:, :, ch] = s[:, :, c].any(axis=2)
            lo = np.tanh(np.tanh(g.ravel() @ W1 + b1) @ W2 + b2) @ W3 + b3
            p = np.exp((lo - lo.max()).astype(np.float64))
            a = min(int(np.searchsorted(np.cumsum(p / p.sum()), rng.random())), 5)
            r, terminal = env.act(a)
            total += r
            steps += 1
        out.append(total)
    return out


if __name__ == "__main__":
    with mp.Pool(4) as pool:
        parts = pool.map(play, [(50000 + i * 977, 500) for i in range(4)])
    x = np.array([v for p in parts for v in p], dtype=float)
    print(json.dumps({"mean": x.mean(), "se": x.std(ddof=1) / np.sqrt(len(x)), "episodes": len(x)}))
    print("RECHECK_DONE")
