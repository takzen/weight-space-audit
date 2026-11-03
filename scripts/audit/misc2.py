import sys,json,re,collections,statistics as st
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
base=sys.argv[1]; wsp=sys.argv[2]
print("=== EXP3 all-label stats")
S=json.load(open(f"{base}/exp3_language/eval/scores.json",encoding='utf-8'))
H=json.load(open(f"{base}/exp3_language/eval/heads.json",encoding='utf-8'))
cnt=collections.Counter(); byl=collections.defaultdict(list)
for r in S:
    h=H[r['net']]
    for k,l in r['head_labels'].items():
        cnt[l]+=1; byl[l].append((h[k]['prev'],h[k]['dist'],h[k]['induct'],k,r['net'][:6]))
print(cnt, 'total',sum(cnt.values()))
for l,v in byl.items():
    print(f"{l:9s} n={len(v):3d} median prev={st.median(x[0] for x in v):.3f} median dist={st.median(x[1] for x in v):.1f} max induct={max(x[2] for x in v):.3f}")
# agreement between the two attempts on same network
for net in H:
    a,b=[r for r in S if r['net']==net]
    same=sum(a['head_labels'][k]==b['head_labels'][k] for k in a['head_labels'])
    print(net,'label agreement r0 vs r1:',same,'/ 24')
print("\n=== EXP7 log (tail)"); print(open(f"{base}/exp7_sycophancy/runs/attention_tool/ask_devemb_s2.log",encoding='utf-8',errors='replace').read())
for i in (1,2,3):
    p=json.load(open(f"{base}/exp7_sycophancy/eval/weights_only_{i}/patch_score.json",encoding='utf-8'))
    print(f"--- patch weights_only_{i}:", type(p).__name__, (list(p)[:8] if isinstance(p,dict) else list(p[0])[:12]))
    print(json.dumps(p,ensure_ascii=False)[:900])
print("\n=== EXP6")
for b in ('budget_0','budget_50'):
    d=json.load(open(f"{base}/exp6_go_from_scratch/eval/{b}/eval_submission.json",encoding='utf-8'))
    print(b,{k:(v.get('score') if isinstance(v,dict) else v) for k,v in d.items()})
    print(b,'strong',json.load(open(f"{base}/exp6_go_from_scratch/eval/{b}/analysis_strong.json",encoding='utf-8')))
print('lr scan',open(f"{base}/exp6_go_from_scratch/eval/ppo_same_size/ppo_big_eval/eval_lr_scan.json",encoding='utf-8').read())
print('final b50',open(f"{base}/exp6_go_from_scratch/runs/budget_50/final_answer.md",encoding='utf-8',errors='replace').read())
print("\n=== EXP8 volume per run")
for run in ('p10c','p25c','p50c'):
    rows=[json.loads(l) for l in open(f"{base}/exp8_math/runs/{run}/tool_calls.jsonl",encoding='utf-8')]
    kinds=collections.Counter(r.get('kind') or r.get('type') or r.get('tool') for r in rows)
    print(run,'rows',len(rows),kinds)
    if run=='p50c':
        print(' keys',collections.Counter(tuple(sorted(r)) for r in rows).most_common(4))
        fw=[r for r in rows if (r.get('kind') or r.get('type') or r.get('tool')) not in ('python',None)]
        print(' first fw',json.dumps(fw[0],ensure_ascii=False)[:1200] if fw else 'none')
print("\n=== disclosure on the page")
t=open(f"{wsp}/assets/traces/exp8_math.json",encoding='utf-8').read()
for kw in ['repeats itself','such as repetition','Localize causally','failure mechanism','HOW TO WORK']:
    print('trace',repr(kw), kw in t)
html=open(f"{wsp}/page.html",encoding='utf-8').read()
txt=re.sub(r'<!--.*?-->','',html,flags=re.S)
for kw in ['repeats itself','failure mechanism','Snake','prompt v3','Trial runs','best seed','best of 3','1,152']:
    print('html-visible',repr(kw), kw in txt)
print("\n=== card: remaining rows")
s=open(f"{wsp}/qwen_readme.md",encoding='utf-8').read()
i=s.find('Experimental settings: top_p=0.95'); tb=s[:i]; tb=tb[tb.rfind('<table'):]
for tr in re.findall(r'<tr>(.*?)</tr>',tb,flags=re.S):
    c=[re.sub('<[^>]+>','',x).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>',tr,flags=re.S)]
    if c: print(c)
