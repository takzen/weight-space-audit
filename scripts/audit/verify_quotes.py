"""Finds the exact text behind the quotes the audit uses. Reads data only."""
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
base = sys.argv[1]


def grep(pattern, root, exts=("*.md", "*.txt", "*.py", "*.json", "*.jsonl", "*.log"), maxhits=8, width=300, flags=re.I):
    hits = 0
    for ext in exts:
        for p in glob.glob(f"{root}/**/{ext}", recursive=True):
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in re.finditer(pattern, txt, flags):
                s = max(0, m.start() - width // 2)
                print(f"  [{os.path.relpath(p, base)}] ...{txt[s:m.end() + width // 2]!r}")
                hits += 1
                if hits >= maxhits:
                    return


print("=== exp1: initialization-scale")
grep(r"initiali[sz]ation[- ]scale", f"{base}/exp1_which_game", maxhits=3)
print("=== exp3: how 'copy' is defined in the prompt")
grep(r"induction", f"{base}/exp3_language/runs", exts=("prompt*", "message*", "*.txt"), maxhits=3)
for p in glob.glob(f"{base}/exp3_language/*.md"):
    t = open(p, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"[^\n]*(0\.3|0\.2\b|cutoff|threshold)[^\n]*", t):
        print("  README:", m.group(0)[:260])
print("=== exp4 README lines")
t = open(f"{base}/exp4_fix_car/README.md", encoding="utf-8", errors="replace").read()
for m in re.finditer(r"[^\n]*(rel_change|relative|1\.3738|73 steps|every episode|identical|deterministic|0\.95)[^\n]*", t):
    print("  ", m.group(0)[:320])
a = open(f"{base}/exp4_fix_car/runs/oneshot_repair/reply/answer.md", encoding="utf-8", errors="replace").read()
print("  ANSWER:", a[:1500].replace("\n", " | "))
r = json.load(open(f"{base}/exp4_fix_car/eval/oneshot_result.json", encoding="utf-8"))
print("  result keys", list(r))
print("  ", json.dumps({k: r[k] for k in r if k not in ("edit_report", "changes", "text")}, ensure_ascii=False)[:900])
print("  text", str(r.get("text"))[:1500])
print("=== exp6 same size + margins")
for p in sorted(glob.glob(f"{base}/exp6_go_from_scratch/eval/*/*.json"))[:14]:
    print("  ", os.path.relpath(p, base))
for b in ("budget_0", "budget_50"):
    d = json.load(open(f"{base}/exp6_go_from_scratch/eval/{b}/eval_submission.json", encoding="utf-8"))
    print(" ", b, {k: (round(v.get("score", 0), 3), round(v.get("mean_margin", 0), 1), round(v.get("stones_captured_per_game", 0), 1)) for k, v in d.items() if isinstance(v, dict)})
print("=== exp7 base model")
t = open(f"{base}/exp7_sycophancy/README.md", encoding="utf-8", errors="replace").read()
for m in re.finditer(r"[^\n]*(starting model|base model|unedited|before fine|follows? (every|all|100)|follow rate)[^\n]*", t, re.I):
    print("  ", m.group(0)[:320])
for m in re.finditer(r"[^\n]*(patch_score|causal check|margin|random)[^\n]*", t):
    print("  P:", m.group(0)[:320])
print("=== exp8 code comments")
grep(r"thinking looped|NON-thinking|55\.5|50\.8|thinking on gave|92 ?%", f"{base}/exp8_math/code", exts=("*.py",), maxhits=8, width=500)
print("=== exp8 prompt quotes")
grep(r"repeats itself|repeating itself", f"{base}/exp8_math/runs/p50c/turns/t001", exts=("prompt*",), maxhits=4, width=500)
