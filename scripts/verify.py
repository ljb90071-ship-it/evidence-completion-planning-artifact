"""Check archived table consistency plus executable local mechanism examples."""
from pathlib import Path
from fractions import Fraction as F
from math import comb
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from replay import load_case,estimate,compatible,replay_cost,acquisition_charge
from check_protocol import directed_checks,random_case,cost_test
def read(name):return json.loads((ROOT/'results/archive'/name).read_text(encoding='utf-8'))
c=json.loads((ROOT/'configs/paper.json').read_text(encoding='utf-8'))
assert c['startup']==[40,10] and c['entities']==4 and c['boundary']=='3/4'
assert c['sample_sizes']==[1,2,4,8,16,32] and c['seed']==20261011
case=load_case(ROOT/'examples/replay.json')
joint=estimate(case);product=estimate(case,True)
assert joint['accepted_count']==16 and joint['chosen_order']==[0,1]
assert [F(x['cost']) for x in joint['orders']]==[F(95,2),F(55)]
assert product['chosen_order']==[1,0]
rejected=dict(case,bounds=[[F(0),F(0)]]*4)
assert estimate(rejected)['accepted_count']==0
assert estimate(rejected)['chosen_order'] is None
# Equality survives, and an empty continuation pays no startup.
tiny=dict(weights=[F(1,2)]*2,known_contributions=[0],bounds=[[1,1]],
          threshold=F(1,2),startup=[40,10],variable_costs=[[1,1]])
assert replay_cost(tiny,[[0,1]],[0,1])[3][0]['survivors']==[0]
tiny['threshold']=F(3,4)
assert replay_cost(tiny,[[0,1]],[0,1])[0]==41
assert acquisition_charge(10,[2,3],[7])==(15,7)
assert acquisition_charge(10,[],[7])==(0,17)
directed_checks()
for seed in range(100):random_case(seed)
assert cost_test()==[F(6635,128),F(1355,32),F(95,2),F(55)]
dp=read('adaptive-results.json')
assert F(dp['independent_audit_allowed']['optimal_cost'])==F(1355,32)
assert F(dp['clustered_audit_allowed']['optimal_cost'])==F(95,2)
info=read('information-results.json');q=F(64,145);value=F(243,58)
assert len(info['actions'])==30 and F(info['minimax_regret'])==value
for a in info['actions']:
    x,y=map(F,a['regrets']);assert q*x+(1-q)*y>=value
assert q*F(1215,128)==(1-q)*F(15,2)==value
learning=read('learning-results.json');prod=read('independent-product-error.json')
for a,b in zip(learning['learning'],prod):
    h=a['h'];assert h==b['h']
    wrong=sum((F(comb(h,k)*3**(h-k),4**h) for k in range(h+1) if 14*k>=11*h),F(0))
    assert abs(a['joint_exact_error']-float(wrong))<1e-15
    assert b['exact_product_wrong']==float(F(b['fraction']))
for row in read('acquisition-results.json'):
    def gain(h):
        error=sum((F(comb(h,k)*3**(h-k),4**h) for k in range(h+1) if 14*k>=11*h),F(0)) if h else F(1)
        return F(15,2)*(1-error)*row['horizon']-row['price']*h
    h=max(c['acquisition_sizes'],key=lambda h:(gain(h),-h))
    assert h==row['h'] and gain(h)==F(row['net_gain'])
cond=read('conditioning-results.json')
assert F(cond['finite_accepted_matrices'],cond['finite_raw_matrices'])==F(1,256)
assert cond['conditional_nonempty']==float(F(369,625))
assert cond['clipped_nonempty']==float(F(624,625))
print('PASS: local replay, exact-state checks, archived probabilities, 30-action dual certificate, acquisition choices.')
print('This command checks archived adaptive results; use src/check_adaptive.py to rerun the Bellman search.')

from check_acquisition_baselines import compute
assert compute()==read('acquisition-baselines.json')
region=read('embedding-region-results.json')
assert region['embedding']['checked_states']==65536
assert region['embedding']['terminal_states']==4096
assert region['robust_region']['positive_root_gap_bounds']==['553/640','27/10']
assert F(region['robust_region']['common_first_action_minimax_lower_bound'])==F(14931,22810)
for world,gap in [('independent','725/128'),('clustered','15/2')]:
    assert region['dp'][world]['gap']==gap
    assert len(region['dp'][world]['actions'])==30
print('PASS: acquisition baselines recomputed; archived embedding and region contracts checked.')
