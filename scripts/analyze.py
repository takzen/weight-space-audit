"""Grades every condition in results/, applies the decision rules of the plan, and writes results/summary.json and summary.md.

  python analyze.py <results_dir> <bench_dir> [<authors_eval_dir>]

Reference values come from the authors' per-problem files and shard scores, when <authors_eval_dir> is given.
Confidence intervals: 95 % percentile bootstrap over problems (samples of one problem are not independent).
"""
import glob
import json
import os
import sys
import threading
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mathgrade as Q  # noqa: E402

RESAMPLES = 10000
RNG_SEED = 20261102
WATCHDOG_S = 900  # the measurement queue waits for this script, so it may never hang the night's run

C0, E0, C1, C3, E1, C2 = ("C0_think_T06_pp15", "E0_edit_T06_pp15", "C1_think_T10_pp15", "C3_think_T10_pp20",
                          "E1_edit_T10_pp15", "C2_think_T06_pp00")
PUBLISHED_CUT = {"unedited": 0.93, "p50c": 0.33}  # the values named in the plan's calibration rule
# Differences reported for the page. Only the two marked rules in the plan decide anything; the others are descriptive.
COMPARISONS = [(E0, C0, "edit in the post's setting"), (C1, C0, "Q1: card temperature against the post's"),
               (E1, C1, "Q3: edit at the card's setting"), (C3, C0, "card temperature, presence 2.0, against the post's"),
               (C3, C1, "presence 2.0 against 1.5 at the card's temperature"), (E1, E0, "edited model: T=1.0 against T=0.6"),
               (E1, C0, "edit and card temperature together, against the post's baseline"),
               (C2, C0, "presence 0.0 against 1.5 at T=0.6")]

N1, E2 = "N1_nothink_T07_p08_pp15", "E2_edit_nothink_T07"
# Added after the plan was frozen, and labelled exploratory on the page. DEVIATIONS.md gives the reason.
EXPLORATORY = [(E2, N1, "the edit with thinking off")]
EXPLORATORY_AUTHORS = [(N1, "p50c", "unedited with thinking off, against the authors' edited model with thinking on"),
                       (N1, "unedited", "unedited with thinking off, against the authors' unedited model with thinking on"),
                       (E2, "p50c", "edited with thinking off, against the authors' edited model with thinking on")]


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def load_bench(bench_dir, name):
    with open(os.path.join(bench_dir, f"{name}.jsonl"), encoding="utf-8") as f:
        return {r["id"]: r for r in map(json.loads, f)}


def dup_share(words, n=8):
    """share of n-gram positions whose n-gram already occurred in `words`."""
    seen, dup, tot = set(), 0, 0
    for i in range(len(words) - n + 1):
        g = tuple(words[i:i + n])
        tot += 1
        if g in seen:
            dup += 1
        else:
            seen.add(g)
    return dup / tot if tot else 0.0


def grade_file(path, bench):
    """One graded record per sample; finished grading is cached next to the raw file."""
    cache = path[:-len(".jsonl")] + ".graded.json"
    with open(path, encoding="utf-8") as f:
        raw = [json.loads(line) for line in f if line.strip()]
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            done = json.load(f)
        if len(done) == len(raw):
            return done
    out = []
    for r in raw:
        pred, _ = Q.extract(r["text"])
        words = r["text"].split()
        out.append({"id": r["id"], "sample": r["sample"], "correct": int(Q.is_correct(pred, bench[r["id"]]["answer"])),
                    "pred": pred, "finish_reason": r["finish_reason"], "n_tokens": r["n_tokens"],
                    "closed_think": "</think>" in r["text"], "tail_dup8": round(dup_share(words[-1000:]), 3)})
    save_json(cache, out)
    return out


def by_problem(graded, value):
    d = {}
    for g in graded:
        d.setdefault(g["id"], []).append(value(g))
    return {k: float(np.mean(v)) for k, v in d.items()}


def boot_ci(values, seed=RNG_SEED):
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return [None, None]
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(RESAMPLES, len(values)))
    means = values[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def summarize(graded):
    n = len(graded)
    per = by_problem(graded, lambda g: g["correct"])
    cut_per = by_problem(graded, lambda g: g["finish_reason"] == "length")
    cut = [g for g in graded if g["finish_reason"] == "length"]
    done = [g for g in graded if g["finish_reason"] != "length"]
    return {
        "samples": n,
        "problems": len(per),
        "acc": float(np.mean([g["correct"] for g in graded])) if n else None,
        "acc_ci95": boot_ci(list(per.values())),
        "cut_share": len(cut) / n if n else None,
        "cut_ci95": boot_ci(list(cut_per.values())),
        "mean_tokens": float(np.mean([g["n_tokens"] for g in graded])) if n else None,
        "median_tokens": float(np.median([g["n_tokens"] for g in graded])) if n else None,
        "acc_given_finished": float(np.mean([g["correct"] for g in done])) if done else None,
        "finished_no_answer": sum(g["pred"] is None for g in done) / n if n else None,
        "cut_loop_share": sum(g["tail_dup8"] >= 0.8 for g in cut) / len(cut) if cut else None,
        "closed_think_share": sum(bool(g["closed_think"]) for g in graded) / n if n else None,
    }


def paired(a, b):
    """Mean of a - b over the problems both maps have, with its interval over problems."""
    shared = sorted(set(a) & set(b))
    diff = [a[i] - b[i] for i in shared]
    return {"problems": len(shared), "diff": float(np.mean(diff)) if shared else None, "ci95": boot_ci(diff)}


def authors_data(eval_dir, run, name):
    """The authors' per-problem accuracy, plus totals from the shard scores where they published them."""
    per, totals = {}, {"cut": 0, "total": 0, "tokens_sum": 0, "ok": 0, "ok_lenient": 0, "no_answer_finished": 0}
    for d in glob.glob(f"{eval_dir}/{run}/parts/{name}_s*of*"):
        p = f"{d}/{name}_per_problem.json"
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                for r in json.load(f):
                    per[r["id"]] = float(np.mean(r["correct"]))
        p = f"{d}/scores.json"
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                s = json.load(f).get(name, {})
            for k in totals:
                totals[k] += s.get(k, 0)
    return per, totals


def view(per, ids=None):
    vals = [per[i] for i in (ids if ids is not None else sorted(per)) if i in per]
    if not vals:
        return None
    return {"problems": len(vals), "acc": float(np.mean(vals)), "acc_ci95": boot_ci(vals)}


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}"


def signed(p):
    if p["diff"] is None:
        return "-"
    return f"{100 * p['diff']:+.1f} ({100 * p['ci95'][0]:+.1f} to {100 * p['ci95'][1]:+.1f}), n={p['problems']}"


def decide(conds, authors):
    """Applies the rules of the plan to whichever conditions exist so far."""
    out = {"comparisons": [], "calibration": {}, "q1": None, "q3": None, "exploratory": []}
    for a, b, what in EXPLORATORY:
        if a in conds and b in conds:
            out["exploratory"].append({"a": a, "b": b, "what": what, "acc": paired(conds[a]["per_problem"], conds[b]["per_problem"]),
                                       "cut": paired(conds[a]["cut_per_problem"], conds[b]["cut_per_problem"])})
    for a in (E0, E1):  # finishing relates to being right within a problem, so this describes finished answers and is not causal
        if a in conds and N1 in conds:
            finished, nothink = conds[a]["finished_per_problem"], conds[N1]["per_problem"]
            shared = sorted(set(finished) & set(nothink))
            out["exploratory"].append({"a": f"{a}:finished", "b": N1, "what": "finished answers with thinking on, against thinking off on the same problems",
                                       "acc": paired(finished, nothink), "a_mean": float(np.mean([finished[i] for i in shared])),
                                       "b_mean": float(np.mean([nothink[i] for i in shared]))})
    if E2 in conds and N1 in conds:  # fixed before E2 finished: fewer cuts alone is the same defect, so finished answers show whether the edit does more
        finished_e2, finished_n1 = conds[E2]["finished_per_problem"], conds[N1]["finished_per_problem"]
        shared = sorted(set(finished_e2) & set(finished_n1))
        if shared:
            out["exploratory"].append({"a": f"{E2}:finished", "b": f"{N1}:finished", "what": "finished answers only, thinking off, edited against unedited",
                                       "acc": paired(finished_e2, finished_n1), "a_mean": float(np.mean([finished_e2[i] for i in shared])),
                                       "b_mean": float(np.mean([finished_n1[i] for i in shared]))})
    for a, run, what in EXPLORATORY_AUTHORS:
        if a in conds and run in authors:
            out["exploratory"].append({"a": a, "b": f"authors:{run}", "what": what,
                                       "acc": paired(conds[a]["per_problem"], authors[run]["per_problem"])})
    for a, b, what in COMPARISONS:
        if a in conds and b in conds:
            acc = paired(conds[a]["per_problem"], conds[b]["per_problem"])
            cut = paired(conds[a]["cut_per_problem"], conds[b]["cut_per_problem"])
            out["comparisons"].append({"a": a, "b": b, "what": what, "acc": acc, "cut": cut})

    for cond, run in ((C0, "unedited"), (E0, "p50c")):
        if cond not in conds or run not in authors:
            continue
        diff = paired(conds[cond]["per_problem"], authors[run]["per_problem"])
        cut = conds[cond]["summary"]["cut_share"]
        acc_ok = bool(diff["ci95"][0] <= 0 <= diff["ci95"][1])
        cut_ok = bool(abs(cut - PUBLISHED_CUT[run]) <= 0.10)
        out["calibration"][cond] = {"authors_run": run, "acc_minus_authors": diff, "acc_ok": acc_ok, "cut_share": cut,
                                    "published_cut": PUBLISHED_CUT[run], "cut_ok": cut_ok, "passes": acc_ok and cut_ok,
                                    "problems": conds[cond]["summary"]["problems"]}
    if C0 in out["calibration"] and E0 in out["calibration"]:
        out["calibration"]["both_pass"] = out["calibration"][C0]["passes"] and out["calibration"][E0]["passes"]

    if C1 in conds and C0 in conds:
        gain = paired(conds[C1]["per_problem"], conds[C0]["per_problem"])
        drop = paired(conds[C0]["cut_per_problem"], conds[C1]["cut_per_problem"])
        gain_ok = bool(gain["diff"] >= 0.15 and gain["ci95"][0] > 0)
        drop_ok = bool(drop["diff"] >= 0.20)
        out["q1"] = {"gain": gain, "cut_drop": drop, "gain_rule_met": gain_ok, "cut_rule_met": drop_ok,
                     "verdict": "supported" if gain_ok and drop_ok else "rejected"}
    if E1 in conds and C1 in conds:
        out["q3"] = {"gain": paired(conds[E1]["per_problem"], conds[C1]["per_problem"]),
                     "cut_change": paired(conds[E1]["cut_per_problem"], conds[C1]["cut_per_problem"])}
    return out


def decisions_md(d):
    md = []
    if d["calibration"]:
        md += ["Calibration against the authors (plan rule; accuracy difference per problem, cut share against the published "
               "full-set value):", ""]
        for cond, c in d["calibration"].items():
            if cond == "both_pass":
                continue
            md.append(f"- {cond} vs {c['authors_run']}: accuracy difference {signed(c['acc_minus_authors'])} "
                      f"[{'ok' if c['acc_ok'] else 'FAIL'}]; cut share {pct(c['cut_share'])} vs {pct(c['published_cut'])} "
                      f"[{'ok' if c['cut_ok'] else 'FAIL'}]; {'PASS' if c['passes'] else 'FAIL'}")
        if "both_pass" in d["calibration"]:
            md.append(f"- Calibration overall: {'PASS' if d['calibration']['both_pass'] else 'FAIL'}")
        md.append("")
    if d["q1"]:
        q = d["q1"]
        md += [f"Q1 (rule: gain >= 15 points with interval above zero, and cut share down >= 20 points): **{q['verdict']}**. "
               f"Gain {signed(q['gain'])} [{'met' if q['gain_rule_met'] else 'not met'}]; "
               f"cut share down by {signed(q['cut_drop'])} [{'met' if q['cut_rule_met'] else 'not met'}].", ""]
    if d["q3"]:
        md += [f"Q3 (edit at the card's setting, E1 minus C1): accuracy {signed(d['q3']['gain'])}; "
               f"cut share {signed(d['q3']['cut_change'])}.", ""]
    if d["exploratory"]:
        md += ["Exploratory comparisons, added after the plan (points, 95% interval over problems):", ""]
        for c in d["exploratory"]:
            cut = f"; cut share {signed(c['cut'])}" if "cut" in c else ""
            md.append(f"- {c['a']} minus {c['b']} ({c['what']}): accuracy {signed(c['acc'])}{cut}")
        md.append("")
    if d["comparisons"]:
        md += ["All paired comparisons (points, 95% interval over problems):", ""]
        for c in d["comparisons"]:
            md.append(f"- {c['a']} minus {c['b']} ({c['what']}): accuracy {signed(c['acc'])}; cut share {signed(c['cut'])}")
        md.append("")
    return md


def main():
    threading.Timer(WATCHDOG_S, lambda: os._exit(3)).start()
    results, bench_dir = sys.argv[1], sys.argv[2]
    authors_dir = sys.argv[3] if len(sys.argv) > 3 else None
    table, md = {}, ["# Results (generated by scripts/analyze.py)", ""]
    for path in sorted(glob.glob(os.path.join(results, "*", "*.jsonl"))):
        cond, name = os.path.basename(os.path.dirname(path)), os.path.basename(path)[:-len(".jsonl")]
        graded = grade_file(path, load_bench(bench_dir, name))
        table.setdefault(name, {})[cond] = {"summary": summarize(graded),
                                            "per_problem": by_problem(graded, lambda g: g["correct"]),
                                            "cut_per_problem": by_problem(graded, lambda g: g["finish_reason"] == "length"),
                                            "finished_per_problem": by_problem([g for g in graded if g["finish_reason"] != "length"], lambda g: g["correct"])}

    out = {}
    for name, conds in table.items():
        subset_path = os.path.join(bench_dir, f"{name}_subset100.json")
        subset = None
        if name == "math500" and os.path.exists(subset_path):
            with open(subset_path, encoding="utf-8") as f:
                subset = sorted(json.load(f))
        out[name] = {"conditions": {}}
        md += [f"## {name}", "",
               "| Condition | Problems | Samples | Accuracy % (95% CI) | Cut at limit % | Mean tokens | Accuracy if finished % |",
               "|---|---|---|---|---|---|---|"]
        for cond in sorted(conds):
            s = conds[cond]["summary"]
            ci = s["acc_ci95"]
            md.append(f"| {cond} | {s['problems']} | {s['samples']} | {pct(s['acc'])} ({pct(ci[0])}-{pct(ci[1])}) | "
                      f"{pct(s['cut_share'])} | {s['mean_tokens']:,.0f} | {pct(s['acc_given_finished'])} |")
            out[name]["conditions"][cond] = dict(s)
            if subset:
                out[name]["conditions"][cond]["on_subset"] = view(conds[cond]["per_problem"], subset)
                cut_sub = view(conds[cond]["cut_per_problem"], subset)
                out[name]["conditions"][cond]["cut_on_subset"] = cut_sub["acc"] if cut_sub else None
        md.append("")

        refs = {}
        if authors_dir:
            md += ["Authors' published results:", ""]
            for run in ("unedited", "p50c"):
                per, totals = authors_data(authors_dir, run, name)
                if not per:
                    continue
                refs[run] = {"per_problem": per}
                entry = {"full": view(per), "subset": view(per, subset) if subset else None, "totals": totals,
                         "cut_share": totals["cut"] / totals["total"] if totals["total"] else None}
                out[name].setdefault("authors", {})[run] = entry
                line = f"- {run}: {pct(entry['full']['acc'])}% on all {entry['full']['problems']} problems"
                if entry["subset"]:
                    line += (f"; {pct(entry['subset']['acc'])}% ({pct(entry['subset']['acc_ci95'][0])}-"
                             f"{pct(entry['subset']['acc_ci95'][1])}) on the fixed subset")
                if entry["cut_share"] is not None:
                    line += f"; cut share {pct(entry['cut_share'])}"
                md.append(line)
            md.append("")

        d = decide(conds, refs)
        out[name]["decisions"] = d
        md += decisions_md(d)
    save_json(os.path.join(results, "summary.json"), out)
    with open(os.path.join(results, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))
    sys.stdout.flush()
    os._exit(0)  # ends the watchdog thread too


if __name__ == "__main__":
    main()
