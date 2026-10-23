from artifact_io import result_path, read_result
"""Exact finite Bayesian decision search; no application timings.

The predictive distribution chooses actions but never certifies an unqueried
score. Every entity must have an observed zero or both observed ones.
Every nonempty subset of unresolved entities is an available role request.
"""
from functools import lru_cache
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

N=4
SETUPS=(40,10)
ALL=(1<<(2*N))-1

def populations():
    independent=[]
    for vals in product((0,1),repeat=2*N):
        bits=sum(v<<i for i,v in enumerate(vals))
        independent.append((bits,F(1,4)**sum(vals)*F(3,4)**(2*N-sum(vals))))
    clustered=[]
    for all_r in (0,1):
        for survivor in range(N):
            bits=(15 if all_r else 0)|(1<<(N+survivor))
            clustered.append((bits,(F(1,4) if all_r else F(3,4))/4))
    return dict(independent=tuple(independent),clustered=tuple(clustered))

def solve(pop, allow_audit=False, root_costs=None):
    actions_at={}
    @lru_cache(None)
    def posterior(known,ones):
        worlds=[(x,p) for x,p in pop if x&known==ones]
        mass=sum(p for _,p in worlds)
        return tuple((x,p/mass) for x,p in worlds)
    @lru_cache(None)
    def value(known,ones):
        pending=[]
        for e in range(N):
            mask=(1<<e)|(1<<(N+e))
            if (known&mask)&~ones or known&mask==mask:
                continue
            pending.append(e)
        if not pending:
            return F(0)
        best=None; choices=[]
        for r in range(2):
            avail=[e for e in (range(N) if allow_audit else pending)
                   if not known&(1<<(r*N+e))]
            for select in range(1,1<<len(avail)):
                batch=tuple(e for j,e in enumerate(avail) if select>>j&1)
                mask=sum(1<<(r*N+e) for e in batch)
                outcomes={}
                for x,p in posterior(known,ones):
                    observed=x&mask
                    outcomes[observed]=outcomes.get(observed,F(0))+p
                cost=F(SETUPS[r]+len(batch))+sum(
                    p*value(known|mask,ones|observed) for observed,p in outcomes.items())
                if root_costs is not None and known == 0:
                    root_costs[(r,batch)] = cost
                if best is None or cost<best:
                    best=cost;choices=[(r,batch)]
                elif cost==best:
                    choices.append((r,batch))
        actions_at[known,ones]=choices
        return best
    optimum=value(0,0)
    # Independently replay the chosen request tree on every supported score matrix.
    replay=F(0)
    for world,prob in pop:
        known=ones=paid=0
        while (known,ones) in actions_at:
            r,batch=actions_at[known,ones][0]
            mask=sum(1<<(r*N+e) for e in batch)
            assert mask & known == 0 and 0<len(batch)<=N
            paid+=SETUPS[r]+len(batch)
            known|=mask
            ones|=world&mask
        for e in range(N):
            mask=(1<<e)|(1<<(N+e))
            assert ((known&mask)&~ones) or known&mask==mask
        replay+=prob*paid
    assert replay==optimum
    return optimum,actions_at,value.cache_info().currsize

if __name__=='__main__':
    out={}
    for name,pop in populations().items():
        assert sum(p for _,p in pop)==1
        assert all(sum(p for x,p in pop if x>>i&1)==F(1,4) for i in range(2*N))
        for audit in (False,True):
            val,actions,states=solve(pop,audit)
            expected=F(1355,32) if name=='independent' else F(95,2)
            role=1 if name=='independent' else 0
            assert val==expected
            assert actions[0,0]==[(role,tuple(range(N)))]
            label=name+('_audit_allowed' if audit else '')
            out[label]=dict(optimal_cost=str(val),decimal=float(val),
                           optimal_first_actions=actions[0,0],states=states)
            print(label,out[label],flush=True)
    result_path('adaptive-results.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
