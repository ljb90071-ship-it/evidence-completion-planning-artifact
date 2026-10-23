from artifact_io import result_path, read_result
"""Finite protocol checks; no application workload or latency is measured."""
from fractions import Fraction as F
from itertools import product, permutations
from collections import Counter
import json

def reject(pool, caps):
    return [m for m in pool if all(x <= caps[e][r]
            for e, row in enumerate(m) for r, x in enumerate(row))]

# A discrete counterpart to the continuous analytical conditioning example.
grid = [F(2*i+1, 40) for i in range(20)]
pool = [tuple((x,) for x in row) for row in product(grid, repeat=4)]
accepted = reject(pool, [(F(1,4),)]*4)
p = F(sum(m[0][0] >= F(1,5) for m in accepted), len(accepted))
q = F(sum(any(row[0] >= F(1,5) for row in m) for m in accepted), len(accepted))
clip_q = F(sum(any(min(row[0], F(1,4)) >= F(1,5) for row in m)
               for m in pool), len(pool))
assert p == F(1,5) and q == F(369,625) and clip_q == F(624,625)
assert F(len(accepted), len(pool)) == F(1,256)

# Correlated two-slot, two-role population: whole-matrix conditioning agrees
# with direct conditional enumeration and retains its within-matrix relation.
joint = [((i, j), (j, i)) for i, j in product(range(4), repeat=2)]
cond = reject(joint, [(2,1),(1,2)])
direct = [m for m in joint if m[0][0]<=2 and m[0][1]<=1]
assert cond == direct and len(cond) == 6
assert all(m[0][0] == m[1][1] and m[0][1] == m[1][0] for m in cond)

# Exhaust every pair of slot permutations for a small accepted complete pool.
small = [((0,1),(0,1)), ((1,0),(1,0)), ((1,1),(1,1))]
h = len(small)
qs = []
for left, right in product(permutations(range(h)), repeat=2):
    shuffled = [(small[left[i]][0], small[right[i]][1]) for i in range(h)]
    for e in range(2):
        assert Counter(m[e] for m in shuffled) == Counter(m[e] for m in small)
    assert len(reject(shuffled, [(1,1),(1,1)])) == h
    qs.append(F(sum(any(row[0] == 1 for row in m) for m in shuffled), h))
assert sum(qs, F(0))/len(qs) == 1-(1-F(2,3))**2 == F(8,9)
original_q = F(sum(any(row[0] == 1 for row in m) for m in small), h)
assert original_q == F(2,3)

def accounting(startup, normal, audit):
    ordinary = startup + sum(normal) if normal else 0
    extra = sum(audit) + (startup if audit and not normal else 0)
    physical = (startup if normal or audit else 0) + sum(normal) + sum(audit)
    assert ordinary + extra == physical
    return ordinary, extra

assert accounting(10,[2,3],[7]) == (15,7)
assert accounting(10,[],[7]) == (0,17)
assert accounting(10,[2],[]) == (12,0)
assert accounting(10,[],[]) == (0,0)
# A truncated source cannot cover a looser target interval.
def refinement(old_caps, new_caps):
    return all(new <= old for old,new in zip(old_caps,new_caps))
assert refinement([.5,.5],[.25,.4])
assert not refinement([.25,.5],[.5,.4])

print(json.dumps({
    'status': 'PASS',
    'finite_raw_matrices': len(pool), 'finite_accepted_matrices': len(accepted),
    'row_survival': float(p), 'conditional_nonempty': float(q),
    'clipped_nonempty': float(clip_q), 'acceptance': '1/256',
    'expected_accepted_of_32': .125,
    'correlated_conditioning_matrices': len(cond),
    'exhaustive_shuffle_pairs': len(qs),
    'original_nonempty': str(original_q), 'mean_shuffled_nonempty': '8/9',
    'slot_role_vector_marginals_preserved': True,
    'accounting_cases': 4, 'frontier_refinement_checks': 2,
    'application_benchmark_executed': False
}, indent=2))
