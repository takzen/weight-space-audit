"""Runs one experimental condition with vLLM and appends every finished answer to a JSONL file.

The prompt and the engine settings follow the authors' evaluate.py (chat template, instruction, bfloat16, a token cap of
max_tokens + 2,048 for the context, per-sample seeds 0..n-1). Restarting skips the answers that are already saved, so a
crash or a reboot loses at most the answers in flight.

  python run_cond.py --ckpt DIR --bench FILE --out FILE --temperature 0.6 --top-p 0.95 --top-k 20 --presence 1.5 \
                     --max-tokens 32768 --thinking --samples 1 [--ids FILE | --exclude-ids FILE --limit N]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathgrade import build_prompt  # noqa: E402


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--bench", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--temperature", type=float, required=True)
    ap.add_argument("--top-p", type=float, required=True)
    ap.add_argument("--top-k", type=int, required=True)
    ap.add_argument("--presence", type=float, required=True)
    ap.add_argument("--max-tokens", type=int, required=True)
    ap.add_argument("--thinking", action="store_true")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--ids")
    ap.add_argument("--exclude-ids")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--gpu-mem", type=float, default=0.80)
    ap.add_argument("--max-num-seqs", type=int, default=8)
    ap.add_argument("--time-limit", type=float, help="stop after this many seconds, keeping saved answers")
    return ap.parse_args()


def load_todo(a):
    with open(a.bench, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    if a.ids:
        keep = set(json.load(open(a.ids, encoding="utf-8")))
        rows = [r for r in rows if r["id"] in keep]
    if a.exclude_ids:
        drop = set(json.load(open(a.exclude_ids, encoding="utf-8")))
        rows = [r for r in rows if r["id"] not in drop]
    if a.limit:
        rows = rows[:a.limit]
    done = set()
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    done.add((r["id"], r["sample"]))
    todo = [(r, s) for s in range(a.samples) for r in rows if (r["id"], s) not in done]
    return rows, todo, len(done)


def stop_leftover_engines():
    """Kills engine processes left by earlier runs started from this directory.

    vLLM's engine process keeps running when its parent dies, so a leftover would hold the GPU memory and make the next
    run fail at start. Conditions run one at a time, so any engine with this working directory is a leftover. The engine's
    process title overwrites its visible environment, which is why the directory is the check.
    """
    import psutil
    found = []
    for p in psutil.process_iter(["cmdline"]):
        try:
            if "VLLM::EngineCore" in " ".join(p.info["cmdline"] or []) and p.cwd() == os.getcwd():
                p.kill()
                found.append(p)
        except psutil.Error:
            continue
    if found:
        psutil.wait_procs(found, timeout=30)
        time.sleep(5)  # the driver releases the memory shortly after the process ends
        print(f"stopped {len(found)} leftover engine process(es)", flush=True)


def stop_own_engine():
    """The exit at the end of main() skips vLLM's normal shutdown, so the engine has to be stopped here."""
    import psutil
    for child in psutil.Process().children(recursive=True):
        try:
            child.kill()
        except psutil.Error:
            continue


def main():
    a = parse_args()
    stop_leftover_engines()
    rows, todo, already = load_todo(a)
    print(f"problems {len(rows)}, samples {a.samples}, saved {already}, to do {len(todo)}", flush=True)
    if not todo:
        print("CONDITION_DONE", flush=True)
        return

    # The FlashInfer sampler needs a CUDA toolkit to JIT-compile and is never used for requests with explicit seeds
    # (see Sampler.sample in vLLM), which all requests here have. Switching it off changes nothing in the sampling.
    os.environ["VLLM_USE_FLASHINFER_SAMPLER"] = "0"
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import RequestOutputKind

    llm = LLM(model=a.ckpt, dtype="bfloat16", gpu_memory_utilization=a.gpu_mem, max_model_len=a.max_tokens + 2048,
              max_num_seqs=a.max_num_seqs, enable_prefix_caching=False, seed=0)
    tok = llm.get_tokenizer()
    engine = llm.llm_engine
    os.makedirs(os.path.dirname(a.out), exist_ok=True)

    def prompt_of(r):
        return tok.apply_chat_template([{"role": "user", "content": build_prompt(r["problem"])}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=a.thinking)

    print("first prompt:", repr(prompt_of(rows[0]))[:400], flush=True)
    pending = list(todo)
    info, next_id = {}, 0
    t0, last_log = time.time(), time.time()
    tokens_total = finished = 0
    with open(a.out, "a", encoding="utf-8") as out:
        while pending or info:
            if a.time_limit and time.time() - t0 > a.time_limit:
                print(f"time limit reached with {len(info)} answers in flight", flush=True)
                break
            while pending and len(info) < a.max_num_seqs:
                r, s = pending.pop(0)
                rid = str(next_id)
                next_id += 1
                sp = SamplingParams(temperature=a.temperature, top_p=a.top_p, top_k=a.top_k,
                                    presence_penalty=a.presence, max_tokens=a.max_tokens, seed=s,
                                    output_kind=RequestOutputKind.FINAL_ONLY)
                engine.add_request(rid, prompt_of(r), sp)
                info[rid] = (r, s, time.time())
            for o in engine.step():
                if not o.finished:
                    continue
                r, s, t_start = info.pop(o.request_id)
                c = o.outputs[0]
                if c.finish_reason not in ("stop", "length"):
                    raise RuntimeError(f"{r['id']} ended with {c.finish_reason}; not saved")
                n = len(c.token_ids)
                tokens_total += n
                finished += 1
                out.write(json.dumps({"id": r["id"], "sample": s, "text": c.text, "finish_reason": c.finish_reason,
                                      "n_tokens": n, "wall_s": round(time.time() - t_start, 1)},
                                     ensure_ascii=False) + "\n")
                out.flush()
                os.fsync(out.fileno())
            now = time.time()
            if now - last_log > 60:
                last_log = now
                print(f"[{(now - t0) / 60:.1f} min] saved {finished}/{len(todo)}, in flight {len(info)}, "
                      f"tokens in saved answers {tokens_total:,}", flush=True)
    print(f"done in {(time.time() - t0) / 60:.1f} min, tokens in saved answers {tokens_total:,}", flush=True)
    if not pending and not info:
        print("CONDITION_DONE", flush=True)
    sys.stdout.flush()
    stop_own_engine()
    os._exit(0)  # the engine's worker threads do not need an orderly shutdown; every answer is already on disk


if __name__ == "__main__":
    main()
