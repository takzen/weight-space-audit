#!/bin/bash
# Runs the conditions of the plan in order. Saved answers are skipped on restart, so this script can be started again at any time.
source "$HOME/qwen-control/.venv/bin/activate"
ROOT=/mnt/c/projects/art/qwen-sampling-control
S=$ROOT/scripts
R=$ROOT/results
L=$ROOT/logs
Q=$HOME/qwen-control
DEADLINE=$(date -d '2026-11-03 07:30' +%s)
SUBSET=$Q/bench/math500_subset100.json
MAX_ATTEMPTS=5

say() { echo "$1 $(date '+%H:%M:%S')" | tee -a "$L/queue.log"; }

# run_set NAME CKPT SET SAMPLES T TOP_P TOP_K PRESENCE MAX_TOKENS THINKING(0/1) SEQS USE_SUBSET(0/1)
run_set() {
  local name=$1 ckpt=$2 set=$3 samples=$4 t=$5 p=$6 k=$7 pp=$8 max=$9 th=${10} seqs=${11} sub=${12}
  local log=$L/$name.$set.log attempt left
  mkdir -p "$R/$name"
  local args=(--ckpt "$Q/models/$ckpt" --bench "$Q/bench/$set.jsonl" --out "$R/$name/$set.jsonl" --temperature "$t"
              --top-p "$p" --top-k "$k" --presence "$pp" --max-tokens "$max" --samples "$samples" --max-num-seqs "$seqs")
  [ "$th" = 1 ] && args+=(--thinking)
  [ "$sub" = 1 ] && args+=(--ids "$SUBSET")
  printf '{"cond":"%s","weights":"%s","set":"%s","samples":%s,"temperature":%s,"top_p":%s,"top_k":%s,"presence_penalty":%s,"max_tokens":%s,"thinking":%s,"subset":%s,"max_num_seqs":%s,"vllm":"0.33.0"}\n' \
    "$name" "$ckpt" "$set" "$samples" "$t" "$p" "$k" "$pp" "$max" "$th" "$sub" "$seqs" > "$R/$name/$set.meta.json"
  say "COND_START $name $set"
  for attempt in $(seq 1 $MAX_ATTEMPTS); do
    left=$((DEADLINE - $(date +%s)))
    if [ "$left" -le 120 ]; then
      say "COND_SHORTENED_BY_DEADLINE $name $set"
      return
    fi
    python "$S/run_cond.py" "${args[@]}" --time-limit "$left" >> "$log" 2>&1
    if tail -n 5 "$log" | grep -a -q CONDITION_DONE; then
      say "COND_DONE $name $set"
      python "$S/analyze.py" "$R" "$Q/bench" "$Q/authors/eval" > "$L/analyze_latest.log" 2>&1 || say "ANALYZE_FAILED after $name"
      return
    fi
    if [ $((DEADLINE - $(date +%s))) -le 120 ]; then
      say "COND_SHORTENED_BY_DEADLINE $name $set"
      python "$S/analyze.py" "$R" "$Q/bench" "$Q/authors/eval" > "$L/analyze_latest.log" 2>&1 || say "ANALYZE_FAILED after $name"
      return
    fi
    say "COND_RETRY $name $set attempt $attempt"
    sleep 30
  done
  say "COND_FAILED $name $set"
}

say "QUEUE_START"
run_set N1_nothink_T07_p08_pp15 text math500 4 0.7 0.8  20 1.5 8192  0 32 0
run_set N1_nothink_T07_p08_pp15 text gsm8k   2 0.7 0.8  20 1.5 8192  0 32 0
run_set C0_think_T06_pp15       text math500 1 0.6 0.95 20 1.5 32768 1 10 1
run_set E0_edit_T06_pp15        p50c math500 1 0.6 0.95 20 1.5 32768 1 10 1
run_set C1_think_T10_pp15       text math500 1 1.0 0.95 20 1.5 32768 1 10 1
run_set C3_think_T10_pp20       text math500 1 1.0 0.95 20 2.0 32768 1 10 1
run_set E1_edit_T10_pp15        p50c math500 1 1.0 0.95 20 1.5 32768 1 10 1
run_set N2_nothink_T10_p10_pp20 text math500 4 1.0 1.0  20 2.0 8192  0 32 0
run_set N2_nothink_T10_p10_pp20 text gsm8k   2 1.0 1.0  20 2.0 8192  0 32 0
run_set C2_think_T06_pp00       text math500 1 0.6 0.95 20 0.0 32768 1 10 1
say "QUEUE_DONE"
