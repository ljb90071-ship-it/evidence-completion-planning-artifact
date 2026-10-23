# When Joint Information Changes Evidence-Completion Plans

This repository accompanies the paper's finite decision and acquisition analysis. It provides exact rational search over adaptive same-role requests, a whole-cohort replay reference implementation, a separate exact-answer state machine, and the numerical data behind the figures and tables.

The central example has four entities, two missing roles, startup prices 40 and 10, and unit variable work. Two populations share every per-entity two-role law but require opposite optimal first requests. Their adaptive expected costs are 1355/32 and 95/2 service-cost units. A 30-action minimax calculation gives regret 243/58. A reachable three-role state realizes the local model, and the unique first requests remain opposite throughout a ten-dimensional price box. The acquisition analysis compares both always-s and the minimax no-sample policy, including the policy-dependent audit price 183/29. The sampling experiments then ask when complete joint observations identify a useful order and when their acquisition cost is worthwhile.

## Start by browsing

1. [Paper-to-material map](paper-map.md): every figure and table, with section and source locations.
2. [Method and implementation guide](docs/method.md): state, actions, replay, conditioning and cost accounting.
3. [Results and units](results/README.md): readable result summary, CSVs, exact fractions and field definitions.
4. [Example inputs](examples/README.md): a complete cohort pool and a passage-level evidence instance.
5. [Experiment configuration](configs/paper.json) and [configuration guide](configs/README.md).

The [survivor distributions](figures/survivors.pdf) and [execution information flow](figures/executor.pdf) are the paper's vector figures. CSVs can be opened directly in a text editor or spreadsheet; JSON holds the longer action lists and exact fractions.

## Run the small examples

Use Python 3.10 or later, with no third-party packages. Commands below run from this repository's root. Python 3.14 was used for the supplied checks.

```sh
python scripts/demo.py
python scripts/verify.py
python scripts/export_tables.py
```

`demo.py` reads the replay and evidence example JSON files. It computes whole-cohort and product-slot estimates, chooses the first role, and executes mixed scans/completions until the exact certificate holds. The clustered pool chooses `[0,1]` under joint replay and `[1,0]` under product-slot replay. The evidence instance returns entity 0 with score `4/5` and representative passage IDs 0 and 1. Its action trace is calculated from the input.

`verify.py` runs local mechanism and consistency checks: joint versus product replay, empty accepted pool, equality handling, empty continuation cost, incremental audit charges, 100 randomized exact-state instances, three directed tie/discard cases, 200 populations × 6 cost identities, and checks on archived adaptive/learning/acquisition results. It checks the stored 30-action minimax dual certificate and embedding/region contracts, and recomputes acquisition-baseline values; it does not rerun the adaptive search or embedding enumeration.

`export_tables.py` reads archived outputs and writes nine CSVs under `results/tables`. This is result analysis and table generation, not an experiment rerun. Table 2 and Figure 1 are derived directly from their stated exact laws. The archived outputs are not overwritten.

## Recompute the finite experiments

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

Run the minimax commands in the listed order: the first computes adaptive optima; `check_information.py` independently calls the solver to obtain every initial-action regret; the certificate command checks those regrets. Output JSON files go to `results/generated`, except conditioning, whose JSON is printed to stdout. The certificate command uses a generated regret file if present and otherwise the archived file. `check_learning.py` includes both the 30,000 training-pool simulation and the four-scale adaptive sweep. `check_product_exact.py` enumerates binomial–multinomial counts through sample size 32. These commands can take longer than the small examples; their values are already browsable in the archive.

The scripts are fixed paper experiments, with parameters visible in their source and indexed by `configs/paper.json`. That JSON documents the experiment contract; it does not silently override constants in the paper-check scripts. To explore other replay inputs without changing the paper experiments:

```sh
python scripts/demo.py --replay examples/replay.json --evidence examples/evidence.json
```

## Reading the implementation

| Module | Responsibility |
|---|---|
| [replay.py](src/replay.py) | Whole-matrix rejection, exact empirical slot-product comparator, role-order replay, startup/variable charges |
| [exact_state.py](src/exact_state.py) | Sorted accesses, exact completions, deterministic representatives, safe discards and answer certificate |
| [check_adaptive.py](src/check_adaptive.py) | Rational Bayesian Bellman search and policy replay on each supported matrix |
| [check_information.py](src/check_information.py) | Enumerate initial-action regrets and solve the two-world minimax mixture |
| [check_information_certificate.py](src/check_information_certificate.py) | Dual lower bound and feasible stagewise upper bound |
| [check_learning.py](src/check_learning.py) | Shared training pools, stagewise learning comparison, startup sweep and acceptance laws |
| [check_product_exact.py](src/check_product_exact.py) | Exact product-estimator wrong-order probabilities |
| [check_conditioning.py](src/check_conditioning.py) | Conditional grid, clipping contrast, slot shuffles and acquisition accounting |
| [check_acquisition.py](src/check_acquisition.py) | Finite-horizon sample-size choice |
| [check_protocol.py](src/check_protocol.py) | Random and directed checks of the exact state machine |

The implementation is a finite reference model. Its score inputs and exact streams are supplied explicitly; no DBMS connector, scorer inference or hardware latency measurement is required. The empirical product comparator enumerates at most one million matrices and is intended for small pools. The adaptive solver is specialized to the four-entity binary instance. These scopes correspond to the distinct mechanisms evaluated in the paper.

See [source and dependency notes](SOURCES.md). No data download, service credential or network access is needed.

## Reachability, price stability and acquisition baselines

[embedding.json](examples/embedding.json) specifies the five-entity, three-role initialization. [check_embedding_region.py](src/check_embedding_region.py) constructs it through actual scans/completions, checks all 256 binary worlds and 256 observation masks, and uses a separate ternary-state DP to calculate all initial-action gaps. The continuous price region follows the policy-count bound in the paper; the script checks its gap and box arithmetic, rather than sampling prices and extrapolating.

[check_acquisition_baselines.py](src/check_acquisition_baselines.py) computes 25 baseline/acquisition/horizon combinations and exact break-even horizons. It preserves the difference between changing the future no-sample policy while holding acquisition fixed and changing the policy that produces audits. [Archived results](results/archive/acquisition-baselines.json) contain every candidate gain, not just the selected size.
