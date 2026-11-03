"""Shows how the reported Breakout rule loses. Diagnostic only: it does not change the reported control."""
import collections
import sys

import numpy as np
from minatar import Environment

sys.path.insert(0, "/mnt/c/projects/art/qwen-sampling-control/scripts")
from minatar_control import LEFT, NOOP, RIGHT, breakout_rule  # noqa: E402

names = {NOOP: "stay", LEFT: "left", RIGHT: "right"}
env = Environment("breakout", sticky_action_prob=0.1)
env.seed(123)
why = collections.Counter()
shown = 0
for ep in range(300):
    env.reset()
    hist = []
    terminal = False
    while not terminal:
        s = env.state()
        by, bx = np.argwhere(s[:, :, 1])[0]
        ly, lx = np.argwhere(s[:, :, 2])[0]
        p = np.flatnonzero(s[9, :, 0])[0]
        a = breakout_rule(s)
        hist.append((int(by), int(bx), int(ly), int(lx), int(p), names[a]))
        r, terminal = env.act(a)
    by, bx, ly, lx, p, a = hist[-1]
    why["sticky blamed" if env.last_action != {"stay": 0, "left": 1, "right": 3}[a] else "rule chose this"] += 1
    why[f"miss distance {abs(p - bx)}"] += 1
    if shown < 3:
        shown += 1
        print(f"--- episode {ep}, {len(hist)} steps, last 8 frames (ball row, col | previous row, col | paddle | action):")
        for f in hist[-8:]:
            print("   ", f)
print(why.most_common())
