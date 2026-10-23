# Reference model and invariants

## Three distinct calculations

The repository separates the exact query state, a fixed-boundary cost predictor, and an exact finite policy optimizer. A prediction never enters an answer certificate. The adaptive binary optimizer proves the finite separation; it is not the outer controller of the passage-level example.

`exact_state.Protocol` stores role streams sorted by decreasing score then passage ID. The first stream occurrence gives that entity's maximum and tie-broken representative. `complete(role, batch)` obtains the same maximum directly for seen eligible entities. The directory rejects any entity with an empty required role before completion. `state()` maintains fully resolved top-k answers, unresolved active entities and permanently discarded entities. It drops an unresolved entity only when its upper score is strictly below the current kth exact score. An unresolved equality stays active; a resolved tied loser is ranked by entity ID. If a stream is exhausted, no wholly unseen eligible entity remains. The stop condition uses exact maxima and unread-score bounds, not statistical estimates.

The example controller alternates legal completion with round-robin scans. The progress rule matters: cached no-op requests alone cannot establish termination. The supplied reference state computes maxima from in-memory passages; an integrating service must provide the same exact access and unread-bound contract.

## Fixed-boundary replay

In `replay.py`, a matrix has one row per ordered cohort slot and one column per missing role. `known_contributions[e]` is the weighted sum from roles already complete; `weights` covers the missing roles. `bounds[e][r]` bounds a missing score. The local threshold is frozen for all orders of a single decision.

1. Keep a reference matrix only if **all** its entries satisfy their current bounds. Never clip an entry or splice accepted rows from different rejected matrices.
2. For an order, begin with every cohort member alive. A nonempty stage pays its role startup plus the current variable prices for its surviving rows.
3. Substitute that stage's exact sampled scores into upper bounds. Keep rows whose upper score is at least the threshold. Equality is retained.
4. Average total costs over accepted complete matrices and choose the lowest-cost order. Only its first request is a prospective execution action; the real state must be refreshed before planning again.

The optional product comparator forms the Cartesian product of the accepted pool's empirical **whole role vector at each slot**. All roles of a row move together. This preserves each slot's within-entity law and changes only cross-slot association. Rejection happens first. With an empty accepted pool, the estimator reports no chosen order; a caller must select a legal fallback using a specified prior or deterministic policy.

Reference-stratum selection is an input contract here. The example supplies one matched stratum. A production integration must keep acquisition bounds, cohort size, role mask, scorer/snapshot identity and selection conditions attached to observations. A common coarse key alone does not justify pooling different conditional laws. New bounds must refine a previously truncated reference population. The code's compatibility predicate does not establish these population assumptions by itself.

## Exact adaptive binary search

`check_adaptive.py` encodes the eight binary scores in an integer: bits 0–3 are role r for entities 0–3, and bits 4–7 are role s. `(known, ones)` records the observed mask and positive observations. The posterior sums rational probability masses of supported worlds consistent with these observations.

A terminal entity has an **observed** zero or both observed ones. Posterior probability one is not a certificate. At a nonterminal state, the solver enumerates every nonempty subset of unobserved bits in a single role. With `allow_audit=True`, already eliminated entities may receive an information-only probe. Each request costs startup plus its number of new scores. Every transition reveals at least one new bit, so memoized recursion terminates. The chosen policy is separately replayed on all supported matrices and its expected cost compared with the recursive value.

The solver evaluates the supported finite populations. For an off-support execution observation, a general controller may reveal any new score until the observation certificate holds; this fallback is not needed to compute the two stated expectations. `check_information.py` uses all 30 initial actions and a world-aware continuation to form a lower-bound game. `check_information_certificate.py` checks its dual and the matching feasible randomized two-stage policy, with full-r probability 64/145 and full-s probability 81/145.

## Learning and paying for observations

The clustered training pool draws its all-r bit independently from the single surviving s slot. Ties between estimated orders choose s first. Whole-cohort wrong-order probability is the binomial tail `14K >= 11h`. The product calculation sums the independent binomial K and multinomial slot counts; the exact result and the 5,000-pool simulation per h are different outputs.

For positive h the acquisition objective is `horizon * (baseline_regret - 7.5 * wrong(h)) - price * h`. Baseline regret is 15/2 for always-s and 243/58 for the minimax mixture. At h=0 net gain is zero. Sample sizes are restricted to `{0,1,2,4,8,16,32}`; h=0 means no acquisition and zero net gain. Gains identify their no-sample baseline explicitly. Equal gains choose the smaller h. Prices 3 and 58 represent s-first incremental and fresh acquisition in the same matched clustered law. When the mixture also produces audits, its incremental price is 183/29; this is separate from merely changing the future comparison baseline.

For shared requests, normal uncached work pays startup when present; additional audit work pays only its variable cost. An audit-only request pays startup and variable cost. Empty requests cost zero. `acquisition_charge` exposes this decomposition; callers must partition uncached groups into disjoint normal and audit sets before calling it.

## Reachable local coordinates and price stability

The binary four-row replay input uses residual coordinates of a three-role query, rather than an unseen two-role query. In the full state, equal role weights are 1/3, every candidate's observed t score is one, and a completed incumbent sets boundary 5/6. Subtracting the known 1/3 contribution and dividing by remaining weight 2/3 yields the local weights 1/2 and boundary 3/4. A new score-one answer raises the global boundary, but unresolved upper-score equality still blocks the scalar certificate. The `initialized` function and the example trace implement this legal initialization.

The lookup slack is upper score minus the current result boundary. Slack bins follow cohort order (descending upper score, then entity ID); exact acquisition conditions remain in the reference tag. Matching these bins alone is not a proof of population matching.

For the robustness check, any fixed policy has at most four startups per role and one access per entity-role group. Differences of two policies' coefficients are thus bounded by four and one. The absolute weighted price perturbation D bounds the change in a cost difference. Baseline root gaps 725/128 and 15/2 remain positive throughout D < 725/128. Startup intervals [39.5,40.5], [9.5,10.5] and eight independent variable intervals [0.9,1.1] give D <= 24/5. The retained margins imply conservative common-action regret at least 14931/22810 throughout this box; the exact 243/58 value applies at the baseline prices.
