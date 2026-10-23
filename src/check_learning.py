from artifact_io import result_path, read_result
"""Finite/synthetic cost-decision experiments; no application latency data."""
import json, random, math
from fractions import Fraction as F
from pathlib import Path
from itertools import product
from check_adaptive import solve, populations
import check_adaptive as adaptive

def main():
    rng=random.Random(20261011)
    rows=[]
    repeats=5000
    for h in [1,2,4,8,16,32]:
        wrong_joint=wrong_product=0
        for _ in range(repeats):
            r_ones=0
            s_counts=[0]*4
            for _ in range(h):
                r_ones+=rng.random()<.25
                s_counts[rng.randrange(4)]+=1
            pr=r_ones/h
            joint_r=44+14*pr
            joint_s=55
            ib_r=44+10*(1-(1-pr)**4)+4*pr
            ib_s=15+40*(1-math.prod(1-n/h for n in s_counts))
            wrong_joint+=joint_r>=joint_s
            wrong_product+=ib_r>=ib_s
        exact_error=sum(F(math.comb(h,k))*F(1,4)**k*F(3,4)**(h-k)
                        for k in range(h+1) if F(44)+14*F(k,h)>=55)
        rows.append(dict(h=h,joint_wrong=wrong_joint,product_wrong=wrong_product,
                         repeats=repeats,joint_exact_error=float(exact_error),
                         joint_expected_regret=float(exact_error*F(15,2)),
                         product_mean_regret=wrong_product/repeats*7.5))
    sweep=[]
    for lam in [F(0),F(1,10),F(1),F(10)]:
        adaptive.SETUPS=(40*lam,10*lam)
        vals={}
        for name,pop in populations().items():
            optimum,actions,states=solve(pop,allow_audit=True)
            vals[name]=dict(cost=float(optimum),exact=str(optimum),
                            first_actions=actions[0,0],states=states)
        sweep.append(dict(lambda_=float(lam),worlds=vals))
    adaptive.SETUPS=(40,10)
    # Equal slot-compatibility marginals can imply incompatible acquisition costs.
    acceptance={}
    laws={
        'independent':[(mask,F(1,4)**sum(mask)*F(3,4)**(4-sum(mask)))
                       for mask in product((0,1),repeat=4)],
        'shared':[((0,0,0,0),F(3,4)),((1,1,1,1),F(1,4))],
        'exclusive':[(tuple(int(i==j) for i in range(4)),F(1,4)) for j in range(4)]}
    for name,law in laws.items():
        assert sum(p for _,p in law)==1
        assert all(sum(p*mask[i] for mask,p in law)==F(1,4) for i in range(4))
        alpha=sum(p for mask,p in law if all(mask))
        acceptance[name]=dict(alpha=str(alpha),expected_raw_for_8=str(8/alpha) if alpha else None)
    report=dict(seed=20261011,learning=rows,adaptive_startup_sweep=sweep,
                acceptance_laws=acceptance,
                experiment='synthetic decisions and exact finite cost; not elapsed service measurements')
    result_path('learning-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(learning=rows,sweep=[dict(lambda_=x['lambda_'],
          costs={k:v['cost'] for k,v in x['worlds'].items()},
          first_action_counts={k:len(v['first_actions']) for k,v in x['worlds'].items()}) for x in sweep]),indent=2))

if __name__=='__main__':main()
