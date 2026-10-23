# Results, units and data dictionary

All costs and regrets are **service-cost units**, with startup paid once per nonempty request and variable work paid per entity-role group. They are not seconds, milliseconds or throughput. Scores, probabilities and startup scaling factors are dimensionless. Pool sizes, states, requests and horizons are counts. Fraction strings such as `1355/32` preserve exact rational values; decimal columns are for convenient viewing.

## Main results

| Quantity | Independent population | Clustered population |
|---|---:|---:|
| Stagewise r then s cost | 51.8359375 | 47.5 |
| Stagewise s then r cost | 42.34375 | 55 |
| Adaptive optimum, startup scale 1 | 42.34375 | 47.5 |
| Optimal first action, scale 1 | all four s scores | all four r scores |
| Adaptive optimum, scale 0 | 5 | 4.4375 |

Across the two populations, the tight minimax initial-action regret is `243/58`, attained by full r with probability `64/145` and full s with probability `81/145`. Costs use exact score certificates even when information-only probes are permitted.

At h=8, whole-cohort wrong-order probability is approximately 0.00038147 and product error approximately 0.977722. Table 5 gives exact-law errors; the separate training counts are 5,000-pool simulation checks. In the conditioning grid, 625 of 160,000 matrices pass all bounds: acceptance 1/256, nonempty probability 369/625 after rejection and 624/625 after clipping. Eight accepted matrices require 2,048 raw draws in expectation under independent compatibility.

## CSV navigation

| File | Fields and meaning |
|---|---|
| [table2.csv](tables/table2.csv) | `world`; `q_r/q_s`: nonempty survivor probabilities; `cost_r_s/cost_s_r`: exact stagewise costs |
| [table4.csv](tables/table4.csv) | `startup_scale`; `world`; exact `cost`; `optimal_first_actions`: JSON list of `[role,[entity IDs]]`; `visited_states`: memoized DP states |
| [table5.csv](tables/table5.csv) | `h`: complete matrices per pool; `whole_cohort_error/product_error`: exact-law wrong-order probabilities; `training_pools`: simulation denominator; `*_wrong_count`: simulated wrong choices |
| [table6.csv](tables/table6.csv) | `law`; exact full-matrix `acceptance`; `expected_raw_for_8`: expected raw draws for eight acceptances, or `Impossible` at zero acceptance |
| [table7.csv](tables/table7.csv) | `horizon`: future decisions; `price`: units per acquired matrix; `h`: chosen matrix count; exact `net_gain` and its `decimal` value |
| [figure1.csv](tables/figure1.csv) | `count`: survivor count 0–4; other columns: probability masses in the three laws |
| [minimax-actions.csv](tables/minimax-actions.csv) | `role`: 0=r, 1=s; `batch`: entity IDs 0–3; regrets relative to the corresponding world-specific adaptive optimum |

Table 1 describes the access interface and has no numerical result file. The CSVs retain greater precision than the paper's rounded display. `exclusive` in Table 6 data is the paper's “Exactly one slot” law; `shared` is the common compatibility event.

## Archived JSON

| File | Structure |
|---|---|
| [adaptive-results.json](archive/adaptive-results.json) | Four records: each world with and without information-only probes. `optimal_cost` is exact; `decimal` is its float; `optimal_first_actions` includes all tied first actions; `states` counts visited states. |
| [learning-results.json](archive/learning-results.json) | `seed`; `learning` with sample sizes, exact whole-cohort errors, simulation counts and expected regrets; `adaptive_startup_sweep`; `acceptance_laws` with exact fraction strings. `product_mean_regret` is simulation mean, not the exact Table 5 product error. |
| [independent-product-error.json](archive/independent-product-error.json) | One record per h; `fraction` is exact product wrong-order probability and `exact_product_wrong` its float. |
| [information-results.json](archive/information-results.json) | `minimax_regret`, decimal, mixture and all 30 actions. Each action's `regrets` is ordered independent then clustered. The lower-bound continuation receives the population law. |
| [conditioning-results.json](archive/conditioning-results.json) | Grid counts/probabilities, correlated acceptance count, 36 shuffle pairs, nonempty probabilities, accounting/refinement check counts. `status` records completion of that finite script, not a broader system benchmark. |
| [acquisition-results.json](archive/acquisition-results.json) | Same records as Table 7 CSV; exact gains include sample cost and stagewise decision regret over the given horizon. |

The archived JSON is the result baseline supplied with the paper. Recomputing writes separately under `results/generated`; no script overwrites the archive. `scripts/export_tables.py` deliberately reads the archive, so table generation does not silently switch to a locally modified experiment. The generated directory need not exist in a fresh download.

[Protocol check output](archive/protocol-results.json) records 1,000 randomized instances, 146 exercising safe discard, three directed cases and 200 populations with six orders each. The maximum action count is 299; this is an operation count, not a timing measurement.

## Added decision and acquisition evidence

- [table3.csv](tables/table3.csv): all eight role/size classes representing 30 first requests; each world column is exact regret after population-optimal continuation.
- [embedding-region-results.json](archive/embedding-region-results.json): independent ternary-state DP (`dp`, with exact root costs/gaps and visited states including terminal states), `embedding` (256 worlds × 256 masks, terminal and raised-boundary counts), and `robust_region` (worst box D, two positive root-gap margins, conservative uniform regret bound). Counts are state counts, not runtime metrics.
- [table8.csv](tables/table8.csv): minimax-baseline acquisition rows. `acquisition` identifies s-first audits, mixture audits or fresh collection; `price` and `baseline_regret` are exact service-cost units; `horizon`, `h`, `net_gain` and `decimal` have the same meanings as Table 7.
- [acquisition-baselines.json](archive/acquisition-baselines.json): all 25 rows, each including `all_gains` for the full candidate grid. `strict_positive_gain_horizon_thresholds` holds the exact real horizon threshold, its decimal and the sample size attaining it. Positive benefit requires a strictly larger horizon; integer horizons round upward when the threshold is nonintegral.

Against the mixture, fresh acquisition first pays at integer horizon 26 rather than 11 against always-s. Keeping s-first acquisition at price 3 changes future-policy comparison only; mixture-produced audits instead cost 183/29. At horizons 4 and 16 these two acquisition regimes choose h=2/4 and h=1/2, respectively. All values evaluate the same matched clustered population and exact learning error.
