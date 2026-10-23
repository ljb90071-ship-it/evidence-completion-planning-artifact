# Paper-to-material map

Paper: **When Joint Information Changes Evidence-Completion Plans**. Section and table numbers refer to the accompanying twelve-page paper.

| Paper item | Browseable material | Executable mechanism / check |
|---|---|---|
| Section 2, Eq. 1 and Table 1: eligibility, maxima and information interface | [Method guide](docs/method.md), [evidence input](examples/evidence.json) | [exact_state.py](src/exact_state.py), `scripts/demo.py` |
| Section 2, Eq. 2: affine physical cost | [Configuration](configs/paper.json), [units](results/README.md) | `replay.replay_cost`; `replay.acquisition_charge` |
| Section 3.1, Eqs. 4–5: stagewise cost identity | [Table 2](results/tables/table2.csv) | `check_protocol.cost_test`, 200 populations × 6 orders |
| Section 3.2, Table 2: same marginals, opposite order | [Table 2 CSV](results/tables/table2.csv), [replay input](examples/replay.json) | `check_protocol.cost_test`; `scripts/demo.py` |
| Figure 1: survivor-count laws | [Vector figure](figures/survivors.pdf), [exact masses](results/tables/figure1.csv) | `scripts/export_tables.py` derives probability masses from the stated laws |
| Section 3.3, Eq. 6: all subset adaptive Bellman search | [Adaptive JSON](results/archive/adaptive-results.json) | `check_adaptive.populations`, `check_adaptive.solve`; supported-world policy replay assertion |
| Section 3.4, Eq. 8: minimax initial-action loss | [30 action CSV](results/tables/minimax-actions.csv), [mixture JSON](results/archive/information-results.json) | `check_information.py`; `check_information_certificate.py` |
| Section 3.6, Eq. 10: marginal union bounds | [Method guide](docs/method.md) | Analytic bounds in the paper; Table 2 provides concrete probabilities within them |
| Section 4.1, Eq. 11: multi-role replay cost | [Replay implementation](src/replay.py) | `replay_cost`; `check_protocol.cost_test` enumerates the general identity |
| Sections 4.2–4.3, Eqs. 12–13: complete reference matrices and whole-matrix rejection | [Method contracts](docs/method.md), [example pool](examples/replay.json) | `compatible`, `estimate`; `check_conditioning.py` checks matched finite populations |
| Section 4.4, Eq. 14: fixed-state concentration statement | [Method assumptions](docs/method.md) | Analytic statement in paper; no online adaptive-reuse experiment is substituted for it |
| Section 4.5: first-request selection | [Demo command](README.md) | `estimate` returns an order; example separately demonstrates exact-state execution |
| Section 4.6: incremental charge and slot shuffle | [Conditioning JSON](results/archive/conditioning-results.json) | `acquisition_charge`; 36 permutations and four accounting cases in `check_conditioning.py` |
| Figure 2 and Section 5, Eqs. 15–16: exact answer state | [Vector figure](figures/executor.pdf), [evidence example](examples/evidence.json) | `exact_state.Protocol`; mixed-access demo; `check_protocol.py` |
| Section 6.1: sampling setup | [Configuration](configs/paper.json), [learning archive](results/archive/learning-results.json) | `check_learning.py`, seed 20261011, six sizes × 5,000 pools |
| Section 6.2, Table 4: startup sweep | [Table 4 CSV](results/tables/table4.csv) | `check_learning.py` invokes exact DP at four startup scales |
| Section 6.3, Eq. 17 and Table 5: learning errors | [Table 5 CSV](results/tables/table5.csv) | `check_learning.py` binomial tail and simulation; `check_product_exact.py` exact product count |
| Section 6.4, Eq. 18 and Table 6: conditioning and coverage | [Table 6 CSV](results/tables/table6.csv), [conditioning JSON](results/archive/conditioning-results.json) | `check_conditioning.py` enumerates 160,000 grid matrices; `check_learning.py` acceptance laws |
| Section 6.5: isolate cohort association | [Conditioning JSON](results/archive/conditioning-results.json) | `check_conditioning.py` exhausts 36 independent slot-vector shuffles |
| Section 6.6, Eq. 19 and Table 7: acquisition horizon | [Table 7 CSV](results/tables/table7.csv) | `check_acquisition.py`, exact discrete gain maximization |
| Section 6.8: answer certificate checks | [Protocol code](src/check_protocol.py), [check output](results/archive/protocol-results.json) | 1,000 random cases; three directed tie, early-stop and persistent-discard cases |

| Section 3.2: reachable three-role top-k state | [Embedding input specification](examples/embedding.json) | `check_embedding_region.py`: 256 worlds × 256 masks; initialization through scans and completions |
| Section 3.3, Eq. 7: continuous price region | [Region results](results/archive/embedding-region-results.json), [method guide](docs/method.md) | Separate ternary-state DP checks root gaps; policy-count argument proves the continuous region |
| Section 3.5, Table 3 and Eq. 9: preliminary probes and uniform loss | [Table 3 CSV](results/tables/table3.csv) | All 30 initial requests grouped into eight exchangeable classes; exact positive-box bound 14931/22810 |
| Section 6.7, Table 8 and Eqs. 20–21: robust no-sample baseline and acquisition policy | [Table 8 CSV](results/tables/table8.csv), [exact gain archive](results/archive/acquisition-baselines.json) | `check_acquisition_baselines.py`: 25 combinations, every candidate gain and exact break-even thresholds |

The paper has no separately numbered algorithm listing. Its operative procedures are the Bellman recursion, stagewise cohort replay, compatibility filtering, sample acquisition accounting and exact-state protocol mapped above. Reference-stratum metadata and the query/scoring service are interface contracts; the repository supplies finite inputs rather than a DBMS integration. The fixed-state predictor and exact-state example are separate components, so an end-to-end online latency result should not be inferred from running them.
