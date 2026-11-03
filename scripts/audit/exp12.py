import sys,json,numpy as np
base=sys.argv[1]
nets={'breakout':'a9f535cc','pong':'dfc6cb65','pacman':'bdf99279','freeway':'0bbcc3ea'}
chs=['agent','moving','reward','obstacle','prev']
print("=== EXP1: non-LLM baseline: per-cell L2 norm of first-layer outgoing weights (500 inputs -> 32 units)")
def find(d,pref):
    return [k for k in d.files if pref in k]
for g,i in nets.items():
    d=np.load(f"{base}/exp1_which_game/networks/{i}.npz",allow_pickle=False)
    if g=='breakout': print('keys',d.files[:12],[d[k].shape for k in d.files[:6]])
    k=[k for k in d.files if d[k].ndim==2 and 500 in d[k].shape and 'actor' in k.lower()] or [k for k in d.files if d[k].ndim==2 and 500 in d[k].shape]
    W=d[k[0]]
    if W.shape[0]!=500: W=W.T
    n=np.linalg.norm(W,axis=1)
    # input index layout: try (row,col,ch)
    desc=open(f"{base}/exp1_which_game/networks/description.txt",encoding='utf-8').read()
    M=n.reshape(10,10,5)
    print(f"\n--- {g}  key={k[0]} global median norm={np.median(n):.2f}, max={n.max():.2f}")
    thr=np.median(n)*2.0
    for c,name in enumerate(chs[:4]):
        print(f"  [{name}]  frac cells 'active'(>2x median)={np.mean(M[:,:,c]>thr):.2f}")
        for r in range(10):
            print("    "+"".join('#' if M[r,x,c]>thr else ('+' if M[r,x,c]>thr*0.6 else '.') for x in range(10)))
print()
print("=== EXP2: non-LLM baseline: output-layer maps (64 -> 144)")
d2={'circle':'d88aba69','square':'a6a9dfb7','triangle':'246a5b58'}
for g,i in d2.items():
    d=np.load(f"{base}/exp2_diffusion/networks/{i}.npz",allow_pickle=False)
    W3=d['W3']; 
    if W3.shape[1]!=144: W3=W3.T
    b=d['b3'].reshape(12,12)
    # per hidden-unit strongest; print top-unit edge map and the bias
    norms=np.linalg.norm(W3,axis=1); order=np.argsort(-norms)
    print(f"\n--- {g}: W3 {W3.shape}; three strongest hidden units' output weights (# >+t, o <-t), t=0.5*max")
    rows=[]
    for u in order[:3]:
        m=W3[u].reshape(12,12); t=0.5*np.abs(m).max()
        rows.append(["".join('#' if m[r,c]>t else ('o' if m[r,c]<-t else '.') for c in range(12)) for r in range(12)])
    for r in range(12): print("   "+"   ".join(rows[j][r] for j in range(3)))
