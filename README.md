# When Joint Information Changes Evidence-Completion Plans

This repository contains exact rational search for adaptive same-role requests,
whole-cohort replay, an exact-answer state machine, and the paper's decision and
acquisition analyses.

The central example has four entities and two missing roles, with startup prices
40 and 10 and unit variable work. Two populations share every per-entity two-role
law but require opposite first requests. Their adaptive expected costs are
1355/32 and 95/2 service-cost units; the 30-action minimax regret is 243/58.
The accompanying calculations examine reachability, price stability and when
acquiring joint observations pays for itself.

## Navigate

- [Paper-to-material map](paper-map.md): figures, tables and corresponding files.
- [Method guide](docs/method.md): state, replay, conditioning and cost accounting.
- [Results and units](results/README.md): summaries, CSVs, exact fractions and fields.
- [Example inputs](examples/README.md): cohort pool and passage-level evidence.
- [Experiment configuration](configs/paper.json) and [configuration guide](configs/README.md).
- Figures: [survivor distributions](figures/survivors.pdf) and [execution information flow](figures/executor.pdf).
- [Source and dependency notes](SOURCES.md).

## Run examples and checks

Use Python 3.10 or later and its standard library. Run from the repository root.
Python 3.14 was used for the supplied checks.

```sh
python scripts/demo.py
python scripts/verify.py
python scripts/export_tables.py
```

`demo.py` reads replay and evidence JSON inputs, compares whole-cohort and
product-slot estimates, and executes scans/completions until the exact certificate
holds. The clustered pool chooses `[0,1]` under joint replay and `[1,0]` under
product-slot replay. The evidence input returns entity 0 with score `4/5` and
representative passage IDs 0 and 1.

`verify.py` checks replay, equality and discard handling, incremental audit charges,
randomized answer states, cost identities, the stored minimax dual certificate,
and embedding/price-region contracts. `export_tables.py` reads archived numerical
outputs and writes nine CSVs under `results/tables`. Table 2 and Figure 1 follow
directly from the specified exact laws.

## Recompute the analyses

```sh
python src/check_adaptive.py
python src/check_information.py
python src/check_information_certificate.py
python src/check_learning.py
python src/check_product_exact.py
python src/check_conditioning.py
python src/check_acquisition.py
python src/check_protocol.py
python src/check_embedding_region.py
python src/check_acquisition_baselines.py
```

Run the minimax commands in this order: `check_adaptive.py` computes adaptive
optima, `check_information.py` computes initial-action regrets and the minimax
mixture, and `check_information_certificate.py` checks the certificate. JSON
outputs go to `results/generated`; conditioning prints JSON to standard output.
The certificate checker reads generated regrets when present and otherwise uses
the archived file.

`check_learning.py` evaluates 30,000 training pools and a four-scale adaptive
sweep. `check_product_exact.py` enumerates binomial–multinomial probabilities
through sample size 32. These calculations can take longer than the examples;
the [result archive](results/README.md) provides their outputs for browsing.

Parameters are defined in each analysis script and indexed by
`configs/paper.json`. That manifest documents the numerical contract. To use
other explicit replay and evidence inputs:

```sh
python scripts/demo.py --replay examples/replay.json --evidence examples/evidence.json
```

## Implementation and input contracts

| Module | Responsibility |
|---|---|
| [replay.py](src/replay.py) | Whole-matrix rejection, empirical slot-product comparator, role ordering and startup/variable charges |
| [exact_state.py](src/exact_state.py) | Sorted access, exact completion, representatives, safe discards and answer certificate |
| [check_adaptive.py](src/check_adaptive.py) | Rational Bayesian Bellman search and policy replay |
| [check_information.py](src/check_information.py) | Initial-action regrets and two-world minimax mixture |
| [check_information_certificate.py](src/check_information_certificate.py) | Dual lower bound and feasible stagewise upper bound |
| [check_learning.py](src/check_learning.py) | Training pools, stagewise learning, startup sweep and acceptance laws |
| [check_product_exact.py](src/check_product_exact.py) | Exact product-estimator error probabilities |
| [check_conditioning.py](src/check_conditioning.py) | Conditional grid, clipping contrast, slot shuffles and acquisition accounting |
| [check_acquisition.py](src/check_acquisition.py) | Finite-horizon sample-size choice |
| [check_protocol.py](src/check_protocol.py) | Random and directed state-machine checks |

Score matrices and exact streams are explicit inputs. The empirical product
comparator accepts up to one million Cartesian combinations; the adaptive solver
operates on the four-entity binary instance.

[embedding.json](examples/embedding.json) gives the five-entity, three-role
initialization. [check_embedding_region.py](src/check_embedding_region.py) reaches
it through scans/completions, checks 256 binary worlds and 256 observation masks,
and calculates initial-action gaps with a ternary-state dynamic program. The
continuous price region uses the paper's policy-count bound and exact box
arithmetic.

[check_acquisition_baselines.py](src/check_acquisition_baselines.py) computes
25 baseline/acquisition/horizon combinations and exact break-even horizons. It
separates the future no-sample policy from the policy producing audits.
[Acquisition results](results/archive/acquisition-baselines.json) retain every
candidate gain.
