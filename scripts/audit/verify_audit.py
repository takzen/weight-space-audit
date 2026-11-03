"""Re-reads the figures the audit quotes from the authors' logs. Reads data only."""
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
base = sys.argv[1]


def jl(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


print("=== files exp4")
for p in sorted(glob.glob(f"{base}/exp4_fix_car/**/*", recursive=True)):
    if os.path.isfile(p):
        print(" ", os.path.relpath(p, base), os.path.getsize(p))
for p in glob.glob(f"{base}/exp4_fix_car/eval/*.json"):
    print("---", os.path.basename(p), json.dumps(jl(p), ensure_ascii=False)[:1100])

print("\n=== files exp7 eval (top)")
for p in sorted(glob.glob(f"{base}/exp7_sycophancy/eval/*"))[:20]:
    print(" ", os.path.relpath(p, base))
for i in (1, 2, 3):
    p = f"{base}/exp7_sycophancy/eval/weights_only_{i}/patch_score.json"
    if os.path.exists(p):
        print(f"--- patch weights_only_{i}", json.dumps(jl(p), ensure_ascii=False)[:700])
for p in sorted(glob.glob(f"{base}/exp7_sycophancy/README*")):
    txt = open(p, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"[^\n]*(attempt|0\.5|P\(|probab|Tentative|55|chance)[^\n]*", txt):
        line = m.group(0).strip()
        if len(line) > 8:
            print("  README:", line[:260])

print("\n=== exp6 eval")
for b in ("budget_0", "budget_50"):
    p = f"{base}/exp6_go_from_scratch/eval/{b}/eval_submission.json"
    if os.path.exists(p):
        d = jl(p)
        print(b, json.dumps(d, ensure_ascii=False)[:800])

print("\n=== exp8 readme table")
p = f"{base}/exp8_math/README.md"
if os.path.exists(p):
    txt = open(p, encoding="utf-8", errors="replace").read()
    print("readme chars", len(txt))
    print(txt[:3500])
