from artifact_io import result_path, read_result
"""Finite-horizon acquisition choice in the same matched clustered law."""
from fractions import Fraction as F
from math import comb
from pathlib import Path
import json

sizes=(0,1,2,4,8,16,32)
def wrong(h):
    return sum((F(comb(h,k)*3**(h-k),4**h) for k in range(h+1)
                if 14*k>=11*h),F(0)) if h else F(1)
out=[]
for horizon in (1,4,16,64,256):
    for price in (3,58):
        gains={h:F(15,2)*(1-wrong(h))*horizon-price*h for h in sizes}
        chosen=max(sizes,key=lambda h:(gains[h],-h))
        out.append(dict(horizon=horizon,price=price,h=chosen,
                        net_gain=str(gains[chosen]),decimal=float(gains[chosen])))
result_path('acquisition-results.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
