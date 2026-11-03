import sys,json,gzip,glob,os,statistics as st,collections
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
base=sys.argv[1]
def load(run):
    rows=[];per={}
    for d in sorted(glob.glob(f"{base}/exp8_math/eval/{run}/parts/math500_s*of10")):
        with gzip.open(f"{d}/math500_first_samples.jsonl.gz",'rt',encoding='utf-8') as f:
            rows+= [json.loads(l) for l in f]
        for r in json.load(open(f"{d}/math500_per_problem.json",encoding='utf-8')):
            per[r['id']]=r
    return rows,per
def dup_frac(w,n=8):
    # fraction of n-gram positions in w whose n-gram occurred earlier in w
    seen=set();d=0;tot=0
    for i in range(len(w)-n+1):
        g=tuple(w[i:i+n]);tot+=1
        if g in seen:d+=1
        else:seen.add(g)
    return d/max(tot,1)
WIN=1000;STEP=250
for run in ('unedited','p50c'):
    rows,per=load(run)
    print('==',run,'rows',len(rows),'fields',list(rows[0].keys()),'per',len(per))
    finished=[r for r in rows if '</think>' in r['text']]
    unfinished=[r for r in rows if '</think>' not in r['text']]
    wl=lambda r:len(r['text'].split())
    print(' closed think:',len(finished),'not closed:',len(unfinished),'median words closed',st.median(map(wl,finished)) if finished else None,'median words unclosed',st.median(map(wl,unfinished)) if unfinished else None)
    for thr in (0.5,0.7,0.8,0.9,0.95):
        fa=0;fa_correct=0;det=[];nodet=0
        for r in rows:
            w=r['text'].split()
            think=w
            first=None
            for e in range(WIN,len(w)+1,STEP):
                if dup_frac(w[e-WIN:e])>=thr:
                    first=e;break
            c=per[r['id']]['correct'][0] if r['id'] in per else None
            closed='</think>' in r['text']
            if closed:
                if first is not None:
                    fa+=1; fa_correct+= c==1
            else:
                if first is None: nodet+=1
                else: det.append(first/len(w))
        print(f' thr={thr}: closed-with-trigger(false alarm)={fa} (of which correct={fa_correct}) of {len(finished)} | unclosed triggered={len(det)} not={nodet} | median onset as share of final length={st.median(det) if det else None}')
