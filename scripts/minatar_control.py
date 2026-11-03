"""Exploratory control for Experiment 5, added after the plan was frozen and outside its decision rules.

Question: how far does a short rule-based program get on the same three games, scored the same way as the post's networks?

The rules below were written once, by Claude, from the same game source files Astra received, and read only the observation.
They were not run on the game before the reported run and were not tuned afterwards: the first complete run is the result.
They are programs, not networks, so this says nothing about whether such rules fit in 32 + 32 tanh units. Astra's own network
is scored with the same code, which checks this evaluator against the authors' published means.

  python minatar_control.py <networks_dir> <out.json>
"""
import json
import multiprocessing as mp
import os
import sys

import numpy as np
from minatar import Environment

NOOP, LEFT, UP, RIGHT, DOWN, FIRE = range(6)
MAX_STEPS = 10_000
EPISODES = 1000
WORKERS = 4
# Which of the game's own channels feed each of the six network channels, as written in the authors' prompts.
SOURCES = {
    "breakout": {0: [0], 2: [3], 3: [1], 4: [2]},  # paddle, brick, ball, trail
    "seaquest": {0: [0, 1], 1: [5, 6, 4], 2: [5, 6, 9], 3: [2], 4: [3, 1], 5: [7, 8]},
    "asterix": {0: [0], 1: [1], 2: [3], 4: [2]},  # player, enemy, gold, trail
}


def breakout_rule(s):
    """Move the paddle to where the ball will be when it reaches the row above the paddle."""
    paddle = np.flatnonzero(s[9, :, 0])[0]
    by, bx = np.argwhere(s[:, :, 1])[0]
    ly, lx = np.argwhere(s[:, :, 2])[0]
    target, step = bx, bx - lx
    if by > ly and step != 0:
        for _ in range(8 - by):
            target += step
            if target < 0 or target > 9:
                target, step = min(max(target, 0), 9), -step
    return LEFT if target < paddle else RIGHT if target > paddle else NOOP


def heading(trail, y, x):
    """Things move sideways and show a trail in the cell behind them."""
    if x > 0 and trail[y, x - 1]:
        return 1
    if x < 9 and trail[y, x + 1]:
        return -1
    return 1 if x == 0 else -1


def asterix_rule(s):
    """Walk toward the nearest treasure, without stepping onto a cell an enemy occupies or is about to reach."""
    py, px = np.argwhere(s[:, :, 0])[0]
    hard, soft = set(), set()
    for y, x in np.argwhere(s[:, :, 1]):
        d = heading(s[:, :, 2], y, x)
        hard |= {(y, x), (y, x + d)}
        soft.add((y, x + 2 * d))
    gold = np.argwhere(s[:, :, 3])
    best, best_score = NOOP, -1e9
    for a, cell in ((NOOP, (py, px)), (LEFT, (py, max(0, px - 1))), (UP, (max(1, py - 1), px)),
                    (RIGHT, (py, min(9, px + 1))), (DOWN, (min(8, py + 1), px))):
        score = -1000.0 * (cell in hard) - 20.0 * (cell in soft)
        if len(gold):
            score -= min(abs(cell[0] - y) + abs(cell[1] - x) for y, x in gold)
        if score > best_score:
            best, best_score = a, score
    return best


def seaquest_rule(s):
    """Avoid what can hit next step, shoot what is ahead, fetch divers, and surface when oxygen is low or the crew is full."""
    y, x = np.argwhere(s[:, :, 0])[0]
    _, back = np.argwhere(s[:, :, 1])[0]
    facing = 1 if back < x else -1
    oxygen, carried = int(s[9, :, 7].sum()), int(s[9, :, 8].sum())
    hard, soft, enemies = set(), set(), []
    for c in (5, 6):
        for ey, ex in np.argwhere(s[:, :, c]):
            d = heading(s[:, :, 3], ey, ex)
            enemies.append((ey, ex))
            hard |= {(ey, ex), (ey, ex + d)}
            soft.add((ey, ex + 2 * d))
    for ey, ex in np.argwhere(s[:, :, 4]):  # enemy bullets move every step and show no direction
        hard |= {(ey, ex), (ey, ex - 1), (ey, ex + 1)}
        soft |= {(ey, ex - 2), (ey, ex + 2)}
    divers = [tuple(p) for p in np.argwhere(s[:, :, 9])]
    if carried >= 1 and (oxygen <= 3 or carried == 6):
        target = (0, x)
    elif divers and carried < 6:
        target = min(divers, key=lambda p: abs(p[0] - y) + abs(p[1] - x))
    elif enemies:
        target = (min(enemies, key=lambda p: abs(p[0] - y) + abs(p[1] - x))[0], x)
    else:
        target = (4, x)
    ahead = any(ey == y and (ex - x) * facing > 0 for ey, ex in enemies)
    behind = any(ey == y and (ex - x) * facing < -2 for ey, ex in enemies)
    best, best_score = NOOP, -1e9
    for a, cell in ((FIRE, (y, x)), (NOOP, (y, x)), (LEFT, (y, max(0, x - 1))), (RIGHT, (y, min(9, x + 1))),
                    (UP, (max(0, y - 1), x)), (DOWN, (min(8, y + 1), x))):
        score = -1000.0 * (cell in hard) - 20.0 * (cell in soft)
        if cell[0] == 0 and y > 0 and carried == 0:  # surfacing with nobody on board ends the game
            score -= 1000.0
        score -= abs(cell[0] - target[0]) + abs(cell[1] - target[1])
        if a == FIRE and ahead:
            score += 3.0
        if behind and not ahead and a == (RIGHT if facing < 0 else LEFT):
            score += 2.0
        if score > best_score:
            best, best_score = a, score
    return best


RULES = {"breakout": breakout_rule, "seaquest": seaquest_rule, "asterix": asterix_rule}


def network_policy(path, game, rng):
    n = np.load(path, allow_pickle=False)
    W1, b1 = n["actor/dense1/kernel"].astype(np.float64), n["actor/dense1/bias"].astype(np.float64)
    W2, b2 = n["actor/dense2/kernel"].astype(np.float64), n["actor/dense2/bias"].astype(np.float64)
    W3, b3 = n["actor/logits/kernel"].astype(np.float64), n["actor/logits/bias"].astype(np.float64)
    sources = SOURCES[game]

    def act(s):
        grid = np.zeros((10, 10, 6))
        for ch, src in sources.items():
            grid[:, :, ch] = s[:, :, src].any(axis=2)
        logits = np.tanh(np.tanh(grid.ravel() @ W1 + b1) @ W2 + b2) @ W3 + b3
        p = np.exp(logits - logits.max())
        return min(int(np.searchsorted(np.cumsum(p / p.sum()), rng.random())), 5)

    return act


def play(job):
    game, kind, seed, episodes, net_dir = job
    env = Environment(game, sticky_action_prob=0.1)
    env.seed(seed)
    policy = RULES[game] if kind == "rule" else network_policy(f"{net_dir}/{game}/hand.npz", game, np.random.default_rng(seed + 1))
    scores, lengths = [], []
    for _ in range(episodes):
        env.reset()
        total, steps, terminal = 0, 0, False
        while not terminal and steps < MAX_STEPS:
            r, terminal = env.act(policy(env.state()))
            total += r
            steps += 1
        scores.append(total)
        lengths.append(steps)
    return scores, lengths


def main():
    net_dir, out_path = sys.argv[1], sys.argv[2]
    out = {}
    with mp.Pool(WORKERS) as pool:
        for game in ("breakout", "asterix", "seaquest"):
            out[game] = {}
            for kind in ("network", "rule"):
                jobs = [(game, kind, 1000 * i + 7, EPISODES // WORKERS, net_dir) for i in range(WORKERS)]
                parts = pool.map(play, jobs)
                scores = np.array([x for p in parts for x in p[0]], dtype=float)
                lengths = np.array([x for p in parts for x in p[1]], dtype=float)
                out[game][kind] = {"mean": float(scores.mean()), "se": float(scores.std(ddof=1) / np.sqrt(len(scores))),
                                   "episodes": len(scores), "max": float(scores.max()), "mean_length": float(lengths.mean()),
                                   "share_hit_step_limit": float((lengths >= MAX_STEPS).mean())}
                print(game, kind, out[game][kind], flush=True)
                tmp = out_path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(out, f, indent=1)
                os.replace(tmp, out_path)
    print("MINATAR_DONE", flush=True)


if __name__ == "__main__":
    main()
