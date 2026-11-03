"""Writes the benchmark files exactly as the authors' evaluate.py `prepare` does, plus the fixed problem subsets.

The subsets are drawn once with a seed fixed in advance, from ids sorted alphabetically, so anyone can re-derive them.
"""
import json
import random
import sys
from pathlib import Path

from datasets import load_dataset

OUT = Path(sys.argv[1])
SEED = 20261102
SUBSET_N = 100


def dump(name, rows):
    with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(name, len(rows), flush=True)


def subset(name, rows):
    ids = sorted(r["id"] for r in rows)
    chosen = sorted(random.Random(SEED).sample(ids, SUBSET_N))
    (OUT / f"{name}_subset{SUBSET_N}.json").write_text(json.dumps(chosen, indent=0), encoding="utf-8")
    print(name, "subset", len(chosen), chosen[:3], flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    math500 = [{"id": r["unique_id"], "problem": r["problem"], "answer": r["answer"]}
               for r in load_dataset("HuggingFaceH4/MATH-500", split="test")]
    gsm8k = [{"id": f"gsm8k_test_{i}", "problem": r["question"],
              "answer": r["answer"].split("####")[-1].strip().replace(",", "")}
             for i, r in enumerate(load_dataset("openai/gsm8k", "main", split="test"))]
    dump("math500", math500)
    dump("gsm8k", gsm8k)
    subset("math500", math500)
    subset("gsm8k", gsm8k)
    print("BENCH_READY", flush=True)


if __name__ == "__main__":
    main()
