from artifact_io import result_path
"""Exact acquisition value against fixed and minimax no-sample policies."""
from fractions import Fraction as F
from math import comb
from pathlib import Path
import json

SIZES=(0,1,2,4,8,16,32)
def error(h):
    return sum((F(comb(h,k)*3**(h-k),4**h) for k in range(h+1)
                if 14*k>=11*h),F(0))
def gain(h,horizon,price,baseline_regret):
    return horizon*(baseline_regret-F(15,2)*error(h))-price*h if h else F(0)
def compute():
    mix=F(64,145)
    incremental=(1-mix)*3+mix*F(21,2)
    assert incremental==F(183,29)
    rows=[]
    regimes=[('always_s','s_audits',F(15,2),F(3)),
             ('always_s','fresh',F(15,2),F(58)),
             ('minimax','s_audits',F(243,58),F(3)),
             ('minimax','mixture_audits',F(243,58),incremental),
             ('minimax','fresh',F(243,58),F(58))]
    for baseline,acquisition,regret,price in regimes:
        for horizon in (1,4,16,64,256):
            gains={h:gain(h,horizon,price,regret) for h in SIZES}
            h=max(SIZES,key=lambda x:(gains[x],-x))
            rows.append(dict(baseline=baseline,acquisition=acquisition,
                baseline_regret=str(regret),price=str(price),horizon=horizon,h=h,
                net_gain=str(gains[h]),decimal=float(gains[h]),
                all_gains={str(k):str(v) for k,v in gains.items()}))
    thresholds=[]
    for baseline,acquisition,regret,price in regimes:
        candidates={h:price*h/(regret-F(15,2)*error(h)) for h in SIZES[1:]
                    if regret>F(15,2)*error(h)}
        h=min(candidates,key=lambda h:(candidates[h],h))
        thresholds.append(dict(baseline=baseline,acquisition=acquisition,
            threshold=str(candidates[h]),threshold_decimal=float(candidates[h]),h=h))
    assert gain(1,1,F(3),F(243,58))==F(-159,232)
    return dict(mixture_r_probability=str(mix),mixture_audit_price=str(incremental),
                rows=rows,strict_positive_gain_horizon_thresholds=thresholds)
if __name__=='__main__':
    result=compute()
    result_path('acquisition-baselines.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result['strict_positive_gain_horizon_thresholds'],indent=2))
