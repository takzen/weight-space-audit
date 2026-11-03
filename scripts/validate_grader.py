"""Regrades the authors' published first samples with mathgrade.py and compares with their per-problem results.

Run with the authors' MATH-500 evaluation parts downloaded under <eval_dir>/<run>/parts/math500_s*of10/.
A perfect match proves the copied grader and the installed math-verify behave like the ones behind the post's numbers.
"""
import glob
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mathgrade as Q  # noqa: E402

eval_dir = sys.argv[1]
total = agree = 0
disagreements = []
for run in ("unedited", "p50c"):
    run_total = run_ok_mine = run_ok_theirs = 0
    for d in sorted(glob.glob(f"{eval_dir}/{run}/parts/math500_s*of10")):
        per = {r["id"]: r for r in json.load(open(f"{d}/math500_per_problem.json", encoding="utf-8"))}
        with gzip.open(f"{d}/math500_first_samples.jsonl.gz", "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                pred, _ = Q.extract(r["text"])
                mine = int(Q.is_correct(pred, r["answer"]))
                theirs = per[r["id"]]["correct"][0]
                run_total += 1
                run_ok_mine += mine
                run_ok_theirs += theirs
                if mine == theirs:
                    agree += 1
                else:
                    disagreements.append((run, r["id"], pred, r["answer"], theirs, mine))
                total += 1
    print(f"{run}: {run_total} samples, correct by this grader {run_ok_mine}, in the authors' file {run_ok_theirs}")
print(f"agreement: {agree}/{total}")
for x in disagreements[:20]:
    print("DISAGREE", x)
print("GRADER_OK" if agree == total else "GRADER_MISMATCH")
