"""Exact sorted-access/completion state and deterministic top-k certificate.
Scores lie in [0, score_upper], weights are positive, and passage identifiers
are unique within each role stream. Predictions never enter this state.
"""
class Protocol:
    def __init__(self, groups, n, m, k, weights=None, score_upper=1):
        self.g, self.n, self.m, self.k = groups, n, m, k
        self.w = weights or [1] * m
        self.eligible = {e for e in range(n) if all(groups[e, r] for r in range(m))}
        self.streams = [sorted([(s, p, e) for e in range(n)
                                for s, p in groups[e, r]],
                               key=lambda x: (-x[0], x[1])) for r in range(m)]
        self.pos, self.tau = [0] * m, [score_upper] * m
        self.seen, self.discarded, self.known = set(), set(), {}

    def complete(self, r, batch):
        for e in batch:
            assert e in self.eligible and e in self.seen
            if e not in self.discarded and (e, r) not in self.known:
                self.known[e, r] = min(self.g[e, r], key=lambda x: (-x[0], x[1]))

    def scan(self, r, count=1):
        for _ in range(count):
            if self.pos[r] == len(self.streams[r]):
                break
            s, p, e = self.streams[r][self.pos[r]]
            self.pos[r] += 1
            self.tau[r] = s
            if e in self.eligible:
                self.seen.add(e)
                if e not in self.discarded:
                    self.known.setdefault((e, r), (s, p))

    def resolved(self, e):
        return all((e, r) in self.known for r in range(self.m))

    def ub(self, e):
        return sum(self.w[r] * (self.known[e, r][0] if (e, r) in self.known
                               else self.tau[r]) for r in range(self.m))

    def state(self):
        done = [(self.ub(e), e, tuple(self.known[e, r] for r in range(self.m)))
                for e in self.seen - self.discarded if self.resolved(e)]
        h = sorted(done, key=lambda x: (-x[0], x[1]))[:self.k]
        low = h[-1][0] if len(h) == self.k else -float('inf')
        active = {e for e in self.seen - self.discarded if not self.resolved(e)}
        self.discarded |= {e for e in active if self.ub(e) < low}
        active -= self.discarded
        exhausted = [self.pos[r] == len(self.streams[r]) for r in range(self.m)]
        u0 = -float('inf') if any(exhausted) else sum(w*t for w,t in zip(self.w,self.tau))
        stop = all(exhausted) or (len(h) == self.k and u0 < low
                                 and all(self.ub(e) < low for e in active))
        return stop, h, active

    def reference(self):
        result = []
        for e in self.eligible:
            vals = tuple(min(self.g[e,r], key=lambda x:(-x[0],x[1])) for r in range(self.m))
            result.append((sum(w*v[0] for w,v in zip(self.w,vals)),e,vals))
        return sorted(result, key=lambda x:(-x[0],x[1]))[:self.k]
