"""Whole-matrix conditioning and fixed-boundary role-order cost replay."""
from fractions import Fraction as F
from itertools import permutations, product
import json


def load_case(path):
    with open(path,encoding='utf-8') as handle:
        raw=json.load(handle)
    case={k:raw[k] for k in raw}
    for key in ('weights','known_contributions','startup'):
        case[key]=[F(str(x)) for x in raw[key]]
    for key in ('bounds','variable_costs'):
        case[key]=[[F(str(x)) for x in row] for row in raw[key]]
    case['threshold']=F(str(raw['threshold']))
    case['matrices']=[[[F(str(x)) for x in row] for row in matrix]
                      for matrix in raw['matrices']]
    n,m=len(case['known_contributions']),len(case['weights'])
    if not n or not m or any(w<=0 for w in case['weights']):
        raise ValueError('Nonempty cohort and positive role weights required')
    if len(case['startup'])!=m or any(a<0 for a in case['startup']):
        raise ValueError('One nonnegative startup price per role required')
    for key in ('bounds','variable_costs'):
        if len(case[key])!=n or any(len(row)!=m for row in case[key]):
            raise ValueError(f'{key} must be entity-by-role')
    if any(not 0<=x<=1 for row in case['bounds'] for x in row):
        raise ValueError('Score bounds must lie in [0,1]')
    if any(x<=0 for row in case['variable_costs'] for x in row):
        raise ValueError('Variable costs must be positive')
    for matrix in case['matrices']:
        if len(matrix)!=n or any(len(row)!=m for row in matrix):
            raise ValueError('Every observation must be a complete cohort matrix')
        if any(not 0<=x<=1 for row in matrix for x in row):
            raise ValueError('Scores must lie in [0,1]')
    return case


def compatible(matrix,bounds):
    return all(x<=bounds[e][r] for e,row in enumerate(matrix) for r,x in enumerate(row))


def replay_cost(case,matrix,order):
    """Charge startup once per nonempty stage; keep unresolved equality alive."""
    m=len(case['weights'])
    if sorted(order)!=list(range(m)):
        raise ValueError('Order must be a permutation of all missing roles')
    alive=list(range(len(matrix)))
    observed=set()
    startup=variable=F(0)
    stages=[]
    for r in order:
        batch=alive[:]
        if batch:
            startup+=case['startup'][r]
            variable+=sum(case['variable_costs'][e][r] for e in batch)
        observed.add(r)
        alive=[e for e in alive if case['known_contributions'][e]+sum(
            case['weights'][t]*(matrix[e][t] if t in observed else case['bounds'][e][t])
            for t in range(m))>=case['threshold']]
        stages.append({'role':r,'requested':batch,'survivors':alive[:]})
    return startup+variable, startup, variable, stages


def estimate(case,product_slots=False):
    accepted=[x for x in case['matrices'] if compatible(x,case['bounds'])]
    if not accepted:
        return {'raw_count':len(case['matrices']),'accepted_count':0,'orders':[],
                'chosen_order':None}
    n,m=len(accepted[0]),len(accepted[0][0])
    # Exact Cartesian product of empirical slot vectors: small-example comparator.
    # Within-slot role dependence stays intact; only cross-slot association changes.
    size=len(accepted)**n if product_slots else len(accepted)
    if size>1000000:
        raise ValueError('Exact empirical product exceeds one million matrices')
    rows=[]
    for order in permutations(range(m)):
        matrices=product(*[[x[e] for x in accepted] for e in range(n)]) if product_slots else accepted
        totals=[F(0),F(0),F(0)]
        for matrix in matrices:
            cost=replay_cost(case,matrix,order)
            for i in range(3):totals[i]+=cost[i]
        rows.append({'order':list(order),'cost':str(totals[0]/size),
                     'startup_cost':str(totals[1]/size),'variable_cost':str(totals[2]/size)})
    # Lexicographically later order wins ties: [1,0] in the paper's two-role case.
    chosen=min(rows,key=lambda x:(F(x['cost']),tuple(-r for r in x['order'])))
    return {'raw_count':len(case['matrices']),'accepted_count':len(accepted),
            'orders':rows,'chosen_order':chosen['order']}


def acquisition_charge(startup,normal,audit):
    """Uncached positive-count groups only; normal/audit groups are disjoint."""
    ordinary=(startup+sum(normal)) if normal else 0
    extra=sum(audit)+(startup if audit and not normal else 0)
    return ordinary,extra
