"""Export browseable tables from archived results; no experiments are rerun."""
from pathlib import Path
from fractions import Fraction as F
from math import comb
import json,csv
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'results/archive';OUT=ROOT/'results/tables'
OUT.mkdir(parents=True,exist_ok=True)
def read(name):return json.loads((A/name).read_text(encoding='utf-8'))
def save(name,rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('table2.csv',[
    dict(world='independent',q_r='175/256',q_s='175/256',cost_r_s='6635/128',cost_s_r='1355/32'),
    dict(world='clustered',q_r='1/4',q_s='1',cost_r_s='95/2',cost_s_r='55')])
learning=read('learning-results.json')
save('table4.csv',[dict(startup_scale=x['lambda_'],world=name,cost=v['exact'],
    optimal_first_actions=json.dumps(v['first_actions']),visited_states=v['states'])
    for x in learning['adaptive_startup_sweep'] for name,v in x['worlds'].items()])
product={x['h']:x for x in read('independent-product-error.json')}
save('table5.csv',[dict(h=x['h'],whole_cohort_error=x['joint_exact_error'],
     product_error=product[x['h']]['fraction'],training_pools=x['repeats'],
     whole_cohort_wrong_count=x['joint_wrong'],product_wrong_count=x['product_wrong'])
     for x in learning['learning']])
save('table6.csv',[dict(law=name,acceptance=v['alpha'],expected_raw_for_8=v['expected_raw_for_8'] or 'Impossible')
                  for name,v in learning['acceptance_laws'].items()])
save('table7.csv',read('acquisition-results.json'))
save('figure1.csv',[dict(count=k,independent=str(F(comb(4,k)*3**(4-k),256)),
     clustered_r=str(F(3,4) if k==0 else F(1,4) if k==4 else F(0)),
     clustered_s=int(k==1)) for k in range(5)])
info=read('information-results.json')
save('minimax-actions.csv',[dict(role=x['role'],batch=json.dumps(x['batch']),
     independent_regret=x['regrets'][0],clustered_regret=x['regrets'][1]) for x in info['actions']])


region=read('embedding-region-results.json')
rootrows=[]
for role in (0,1):
    for size in range(1,5):
        row={'first_role':role,'batch_size':size}
        for world in ('independent','clustered'):
            matches=[a for a in region['dp'][world]['actions'] if a['role']==role and len(a['batch'])==size]
            assert len({a['gap'] for a in matches})==1
            row[world+'_regret']=matches[0]['gap']
        rootrows.append(row)
save('table3.csv',rootrows)
save('table8.csv',[{k:v for k,v in x.items() if k!='all_gains'} for x in read('acquisition-baselines.json')['rows'] if x['baseline']=='minimax'])

print('Exported 9 CSVs from archived values and the exact Figure 1/Table 2 laws.')
