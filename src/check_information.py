from artifact_io import result_path, read_result
"""Exact minimax initial-action regret; continuation receives the true law."""
import json
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import check_adaptive as dp

costs=[]; opt=[]
for name,pop in dp.populations().items():
    root={}
    v,_,_=dp.solve(pop,True,root)
    costs.append(root); opt.append(v)
keys=list(costs[0])
regrets={a:tuple(c[a]-v for c,v in zip(costs,opt)) for a in keys}
# A two-row zero-sum game has an optimum supported on at most two actions.
# Check every pure strategy and every crossing of two action regret segments.
best=min((max(r),[(a,F(1))]) for a,r in regrets.items())
for a,b in combinations(keys,2):
    x,y=regrets[a],regrets[b]
    denom=(x[0]-y[0])-(x[1]-y[1])
    if denom:
        t=(y[1]-y[0])/denom
        if 0<=t<=1:
            r=tuple(t*u+(1-t)*v for u,v in zip(x,y))
            candidate=(max(r),[(a,t),(b,1-t)])
            if candidate[0]<best[0]: best=candidate
out={'minimax_regret':str(best[0]),'decimal':float(best[0]),
     'mixture':[{'role':a[0],'batch':a[1],'probability':str(p)} for a,p in best[1]],
     'actions':[{'role':a[0],'batch':a[1],'regrets':list(map(str,r))} for a,r in regrets.items()]}
result_path('information-results.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='actions'},indent=2))
