"""Finite checks of exact state, ties, safe discards and service-cost identities.
The randomized fixtures use integer scores 0..10 for exact arithmetic;
dividing scores by 10 and weights by their sum gives the normalized paper model.
"""
from exact_state import Protocol as NormalizedProtocol
from fractions import Fraction as F
from itertools import product, permutations
import random, json
from artifact_io import result_path
class Protocol(NormalizedProtocol):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,score_upper=10,**kwargs)

def random_case(seed):
    rng = random.Random(seed)
    n,m = rng.randint(1,40),rng.randint(2,5)
    groups,pid = {},0
    for e,r in product(range(n),range(m)):
        ds=[]
        if rng.random()<.78:
            for _ in range(rng.randint(1,6)):
                ds.append((5 if seed%11==0 else rng.randrange(11),pid))
                pid+=1
        groups[e,r]=ds
    p=Protocol(groups,n,m,rng.randint(1,n+3),[rng.randint(1,5) for _ in range(m)])
    for step in range(20000):
        stop,h,active=p.state()
        if stop:
            assert h==p.reference(),(seed,h,p.reference())
            return step,len(p.discarded)
        live=[r for r in range(m) if p.pos[r]<len(p.streams[r])]
        if not active or step%8==0 or rng.random()<.4:
            p.scan(rng.choice(live),rng.randint(1,4))
        else:
            r=rng.randrange(m)
            batch=[e for e in active if (e,r) not in p.known]
            rng.shuffle(batch)
            p.complete(r,batch[:rng.randint(1,5)])
    raise AssertionError('nontermination')


def directed_checks():
    # Two exact tied entities, followed by a low eligible entity with unread duplicates.
    g={(0,0):[(8,0)],(0,1):[(8,1)],(1,0):[(8,2)],(1,1):[(8,3)],
       (2,0):[(1,4),(0,6)],(2,1):[(1,5),(0,7)]}
    p=Protocol(g,3,2,1)
    p.scan(0,3);p.scan(1,3)
    stop,h,_=p.state()
    assert stop and h==p.reference() and all(p.pos[r]<len(p.streams[r]) for r in range(2))
    # Unresolved entity 0 has U=L=16 and a better ID than incumbent entity 1.
    q=Protocol({(0,0):[(8,0)],(0,1):[(8,1)],(1,0):[(8,2)],(1,1):[(8,3)]},2,2,1)
    q.seen={0,1};q.known={(0,0):(8,0),(1,0):(8,2),(1,1):(8,3)};q.tau=[8,8]
    stop,_,active=q.state()
    assert not stop and 0 in active
    q.complete(1,[0]);assert q.state()[1]==q.reference()
    # Safe discard remains unresolved even after all streams are consumed.
    z=Protocol({(0,0):[(10,0)],(0,1):[(10,1)],(1,0):[(0,2)],(1,1):[(0,3)]},2,2,1)
    z.scan(0,2);z.complete(1,[0]);z.state()
    assert 1 in z.discarded and (1,1) not in z.known
    z.scan(1,2)
    assert z.state()[0] and z.state()[1]==z.reference() and (1,1) not in z.known


def masks_independent(n=4):
    return [(mask,F(1,4)**sum(mask)*F(3,4)**(n-sum(mask)))
            for mask in product((0,1),repeat=n)]


def cost_test():
    independent=masks_independent()
    cluster_r=[((0,0,0,0),F(3,4)),((1,1,1,1),F(1,4))]
    cluster_s=[(tuple(int(j==i) for j in range(4)),F(1,4)) for i in range(4)]
    def expectation(first,setup_first,setup_second):
        return sum(prob*(setup_first+4+setup_second*int(any(mask))+sum(mask))
                   for mask,prob in first)
    ans=[expectation(independent,40,10),expectation(independent,10,40),
         expectation(cluster_r,40,10),expectation(cluster_s,10,40)]
    assert ans==[F(6635,128),F(1355,32),F(95,2),F(55)]
    for dist in [independent,cluster_r,cluster_s]:
        assert sum(p for _,p in dist)==1
        assert all(sum(p*mask[e] for mask,p in dist)==F(1,4) for e in range(4))
        assert sum(p*sum(mask) for mask,p in dist)==1
    # General identity with correlated discrete scores and heterogeneous real work.
    rng=random.Random(19)
    for trial in range(200):
        b,m,h=4,3,7
        a=[rng.randrange(10) for _ in range(m)]
        v=[[rng.randint(1,8) for _ in range(m)] for _ in range(b)]
        matrices=[[[rng.randrange(11) for _ in range(m)] for _ in range(b)] for _ in range(h)]
        L=rng.randint(10,27)
        for order in permutations(range(m)):
            total=0;nonempty=[0]*m;members=[[0]*b for _ in range(m)]
            for scores in matrices:
                alive=set(range(b));known=set()
                for j,r in enumerate(order):
                    total+=a[r]*bool(alive)+sum(v[e][r] for e in alive)
                    nonempty[j]+=bool(alive)
                    for e in alive:members[j][e]+=1
                    known.add(r)
                    alive={e for e in alive if sum(scores[e][t] if t in known else 10
                                                   for t in range(m))>=L}
            identity=sum(a[r]*nonempty[j]+sum(v[e][r]*members[j][e] for e in range(b))
                         for j,r in enumerate(order))
            assert total==identity
    return ans


if __name__=='__main__':
    results=[random_case(seed) for seed in range(1000)]
    directed_checks()
    costs=cost_test()
    report={'random_instances':len(results),'max_steps':max(x[0] for x in results),
            'safe_discard_instances':sum(x[1]>0 for x in results),
            'directed_cases':3,'cost_identity_populations':200,'orders_per_population':6,
            'stagewise_costs':[str(x) for x in costs]}
    result_path('protocol-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
