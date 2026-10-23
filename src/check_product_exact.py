from artifact_io import result_path, read_result
"""Independent exact check of the product estimator's wrong-order rate.

K ~ Binomial(h,1/4); slot counts C ~ Multinomial(h;1/4,...,1/4).
They are independent because the two role columns are generated independently.
The product estimator chooses s on ties. This checks a fixed two-order model,
not an adaptive executor or an application benchmark.
"""
from pathlib import Path
from fractions import Fraction as F
import math
import json

rows = []
for h in (1, 2, 4, 8, 16, 32):
    numerator = 0
    for a in range(h+1):
        for b in range(h-a+1):
            for c in range(h-a-b+1):
                counts = (a, b, c, h-a-b-c)
                ways = math.factorial(h)//math.prod(math.factorial(x) for x in counts)
                prod = math.prod(h-x for x in counts)
                for k in range(h+1):
                    # h^4 * (estimated cost(r->s) - estimated cost(s->r)).
                    delta = -h**4-10*(h-k)**4+4*k*h**3+40*prod
                    if delta >= 0:
                        numerator += ways*math.comb(h,k)*3**(h-k)
    probability = F(numerator, 4**(2*h))
    rows.append(dict(h=h, exact_product_wrong=float(probability), fraction=str(probability)))
assert rows[0]['fraction'] == '1/4'
assert rows[1]['fraction'] == '7/16'
text = json.dumps(rows, indent=2)
result_path('independent-product-error.json').write_text(text, encoding='utf-8')
print(text)
