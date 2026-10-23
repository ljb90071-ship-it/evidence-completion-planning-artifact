from artifact_io import result_path, read_result
"""Dual certificate using the stored DP root regrets; not a new DP."""
from fractions import Fraction as F
from pathlib import Path
import json

data=json.loads(read_result('information-results.json').read_text(encoding='utf-8'))
assert len(data['actions']) == 30
q=F(64,145)
value=F(243,58)
for action in data['actions']:
    independent,clustered=map(F,action['regrets'])
    assert q*independent+(1-q)*clustered >= value
# Direct stagewise policies are feasible without receiving a genie law.
r_regret=F(6635,128)-F(1355,32)
s_regret=F(55)-F(95,2)
assert r_regret==F(1215,128) and s_regret==F(15,2)
assert q*r_regret==(1-q)*s_regret==value
print('PASS: 30-action dual lower bound and feasible randomized stagewise upper bound = 243/58.')
