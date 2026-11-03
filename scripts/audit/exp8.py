import sys,json,re,collections
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
base=sys.argv[1]
for run in ('p10c','p25c','p50c'):
    rows=[json.loads(l) for l in open(f"{base}/exp8_math/runs/{run}/tool_calls.jsonl",encoding='utf-8')]
    fw=[r for r in rows if r['kind']=='forward']
    gen=0;tf=0;gp=0;tp=0;tok=0;both=0;seen=set();fails=0
    for r in fw:
        q=r['request']; res=r.get('result')
        ok = not (isinstance(res,dict) and res.get('error')) 
        if not ok: fails+=1; continue
        if q.get('type')=='generate':
            items=len(q.get('problems',[]))+len(q.get('prompts',[]) or [])
            n=q.get('n',1); m=2 if q.get('model')=='both' else 1
            gen+=items*n*m; gp+=1; both+= (m==2)
            if isinstance(res,dict):
                def walk(d):
                    global tok
                for key in ('mean_tokens','mean_length'):
                    if key in res and isinstance(res[key],(int,float)): tok+=res[key]*items*n*m
        else:
            tf+=len(q.get('texts',[]) or q.get('chats',[]) or []); tp+=1
    print(run,'forward calls',len(fw),'failed',fails,'| generation passes',gp,'(paired',both,') answers generated',gen,'| teacher-forced passes',tp,'texts read',tf)
    if run=='p50c':
        print(' first result keys', list(fw[0]['result'].keys())[:25] if isinstance(fw[0]['result'],dict) else str(fw[0]['result'])[:400])
        print(' first result', json.dumps(fw[0]['result'],ensure_ascii=False)[:900])
        hs=sum(1 for r in fw if 'hidden_states' in json.dumps(r['request'].get('return',{})) or r['request'].get('activations'))
        print(' passes requesting activations/hidden states:',hs)
        # how much python touches weights vs activations
        py=[r for r in rows if r['kind']=='python']
        kw={'load(':0,'hidden_states':0,'/work/fwd_':0,'_acts':0,'svd':0}
        for r in py:
            c=r['code']
            for k in kw:
                if k in c: kw[k]+=1
        print(' python runs',len(py),'mentioning:',kw)
