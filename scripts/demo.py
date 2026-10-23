"""Run finite input examples without an external service or data download."""
from pathlib import Path
import sys,json,argparse
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from replay import load_case,estimate
from exact_state import Protocol

parser=argparse.ArgumentParser()
parser.add_argument('--replay',type=Path,default=ROOT/'examples/replay.json')
parser.add_argument('--evidence',type=Path,default=ROOT/'examples/evidence.json')
args=parser.parse_args()
case=load_case(args.replay)
raw=json.loads(args.evidence.read_text(encoding='utf-8'))
groups={(e,r):[] for e in range(raw['n']) for r in range(raw['m'])}
for row in raw['groups']:
    groups[row['entity'],row['role']]=[(F(s),pid) for s,pid in row['passages']]
p=Protocol(groups,raw['n'],raw['m'],raw['k'],list(map(F,raw['weights'])))
trace=[]
step=0
while True:
    stop,answers,active=p.state()
    if stop:break
    # Simple progress controller: alternate completion and a round-robin scan.
    if step%2 and active:
        e=min(active,key=lambda e:(-p.ub(e),e))
        r=next(r for r in range(p.m) if (e,r) not in p.known)
        p.complete(r,[e]);trace.append({'kind':'complete','role':r,'entities':[e]})
    else:
        live=[r for r in range(p.m) if p.pos[r]<len(p.streams[r])]
        r=live[(step//2)%len(live)]
        p.scan(r);trace.append({'kind':'scan','role':r})
    step+=1
assert answers==p.reference()
result={'whole_cohort':estimate(case),'product_slots':estimate(case,True),
        'exact_answers':[{'entity':e,'score':str(s),
                          'representatives':[pid for _,pid in reps]} for s,e,reps in answers],
        'actions':trace,'discarded':sorted(p.discarded),
        'matches_exhaustive':True}
print(json.dumps(result,indent=2))
