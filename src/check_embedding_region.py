"""Reachable-state and price-region checks; standard library only. Writes to results/generated.

DP below uses ternary observation tuples and unnormalized integer world masses.
Embedding checks reuse the paper's exact-state class, copied locally unchanged
apart from its already published score_upper parameter. No external files needed.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import json
from exact_state import Protocol

from artifact_io import result_path
HERE = Path(__file__).resolve().parent

def worlds():
    ind = [(bits, 3**bits.count(0)) for bits in product((0, 1), repeat=8)]
    clu = [(tuple([r]*4+[int(e == j) for e in range(4)]), 3 if r == 0 else 1)
           for r in (0, 1) for j in range(4)]
    return {'independent': ind, 'clustered': clu}

def terminal(z):
    return all(z[e] == 0 or z[e+4] == 0 or z[e] == z[e+4] == 1 for e in range(4))

def solve(pop):
    root_actions = []
    @lru_cache(None)
    def value(z):
        if terminal(z):
            return F(0)
        supported = [(x, p) for x, p in pop if all(o == -1 or o == x[i] for i, o in enumerate(z))]
        mass = sum(p for _, p in supported)
        assert mass > 0
        costs = []
        for role in range(2):
            avail = [i for i in range(4*role, 4*role+4) if z[i] == -1]
            for select in range(1, 1 << len(avail)):
                indices = [i for j, i in enumerate(avail) if select >> j & 1]
                outcomes = {}
                for x, p in supported:
                    child = list(z)
                    for i in indices:
                        child[i] = x[i]
                    child = tuple(child)
                    outcomes[child] = outcomes.get(child, 0) + p
                cost = (40, 10)[role] + len(indices) + sum(F(p, mass)*value(child) for child, p in outcomes.items())
                costs.append(cost)
                if z == (-1,)*8:
                    root_actions.append({'role': role, 'batch': [i % 4 for i in indices], 'cost': cost})
        return min(costs)
    optimum = value((-1,)*8)
    for a in root_actions:
        a['gap'] = a['cost']-optimum
    winners = [a for a in root_actions if a['gap'] == 0]
    assert len(winners) == 1 and len(root_actions) == 30
    gap = min(a['gap'] for a in root_actions if a['gap'] > 0)
    return {'optimum': str(optimum), 'first_action': winners[0]['batch'],
            'first_role': winners[0]['role'], 'gap': str(gap),
            'visited_states': value.cache_info().currsize,
            'actions': [{k: str(v) if isinstance(v, F) else v for k, v in a.items()} for a in root_actions]}

def initialized(bits):
    # Roles 0,1,2 are t,r,s; one passage per entity-role; anchor entity ID 4.
    scores = [[F(1), F(bits[e]), F(bits[e+4])] for e in range(4)] + [[F(1), F(3,4), F(3,4)]]
    g = {(e,r): [(scores[e][r], 3*e+r)] for e in range(5) for r in range(3)}
    p = Protocol(g, 5, 3, 1, [F(1,3)]*3)
    p.scan(0, 5)
    assert p.seen == set(range(5)) and p.pos == [5,0,0]
    p.complete(1,[4]); p.complete(2,[4])
    stop,h,active = p.state()
    assert not stop and h[0][:2] == (F(5,6),4) and active == set(range(4))
    assert all(p.known[e,0][0] == 1 and (e,1) not in p.known and (e,2) not in p.known for e in range(4))
    return p

def embedding_check():
    checked = stopped = raised = 0
    # Every concrete binary world and every partial observation mask.
    # Each mask is reachable by at most two completion requests after initialization;
    # state is refreshed only at the end, as allowed by the exact access interface.
    for bits in product((0,1), repeat=8):
        for mask in range(256):
            p = initialized(bits)
            z = tuple(bits[i] if mask >> i & 1 else -1 for i in range(8))
            for r in (0,1):
                batch = [e for e in range(4) if mask >> (4*r+e) & 1]
                p.complete(r+1,batch)
            stop,h,active = p.state()
            assert h[-1][0] in (F(5,6),F(1))
            raised += h[-1][0] == 1
            assert stop == terminal(z), (bits,mask)
            assert active == {e for e in range(4) if not (z[e] == 0 or z[e+4] == 0 or z[e] == z[e+4] == 1)}
            if stop:
                assert h == p.reference()
                stopped += 1
            checked += 1
    return {'binary_worlds':256,'masks_per_world':256,'checked_states':checked,
            'terminal_states':stopped,'states_with_boundary_one':raised,
            'normalized_missing_weights':['1/2','1/2'],'known_contribution':'1/3',
            'initial_global_boundary':'5/6','normalized_local_boundary':'3/4'}

if __name__ == '__main__':
    inp = {'weights':['1/3']*3,'anchor_scores':['1','3/4','3/4'],'candidate_t':'1',
           'k':1,'baseline_startups':[40,10],'baseline_variable_costs':[1]*8,
           'startup_halfwidth':'1/2','variable_halfwidth':'1/10'}
    result_path('embedding-inputs.json').write_text(json.dumps(inp,indent=2),encoding='utf-8')
    dp = {}
    for name,pop in worlds().items():
        dp[name] = solve(pop)
        print(name,dp[name]['optimum'],'gap',dp[name]['gap'],flush=True)
    assert dp['independent']['gap'] == '725/128' and dp['clustered']['gap'] == '15/2'
    assert (dp['independent']['first_role'],dp['clustered']['first_role']) == (1,0)
    D = 4*F(1,2)+4*F(1,2)+8*F(1,10)
    margins = [F(dp[n]['gap'])-D for n in ('independent','clustered')]
    assert all(g>0 for g in margins)
    emb = embedding_check()
    result = {'dp':dp,'embedding':emb,'robust_region':{'D_box':str(D),
              'positive_root_gap_bounds':list(map(str,margins)),
              'common_first_action_minimax_lower_bound':str(margins[0]*margins[1]/sum(margins))}}
    result_path('embedding-region-results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'embedding':emb,'robust_region':result['robust_region']},indent=2))
