# Paper experiment configuration

[paper.json](paper.json) records the numerical contract used by the fixed experiments. The paper scripts keep these constants directly in readable source; editing this manifest alone does not change their execution.

| Fields | Interpretation and implementation |
|---|---|
| entities, roles, score_values, per_role_success_probability | Four-entity binary populations in `check_adaptive.populations` |
| weights, boundary | Equal-role aggregate at frozen 3/4; binary terminal certificate is observed zero or two ones |
| startup, variable_cost_per_group | Startup 40/10 per nonempty role request, one unit per score; `check_adaptive.SETUPS` and request length |
| startup_scales | Multiply both startup prices; `check_learning` adaptive sweep, variable prices unchanged |
| sample_sizes, training_pools_per_size, seed | Six sample sizes, 5,000 pools each, seed 20261011 in `check_learning` |
| conditioning_grid_midpoints, conditioning_upper, conditioning_survival | Midpoint grid and threshold in `check_conditioning` |
| acquisition_sizes, horizons, sample_prices | Discrete optimization in `check_acquisition` |

The two JSON examples are executable configuration for `scripts/demo.py`. The general replay implementation accepts different complete matrices, known contributions, bounds, prices and weights. Its exact product comparator is deliberately bounded to one million Cartesian combinations; the fixed-paper analytic product-error script uses binomial–multinomial enumeration instead.

`coordinate_system` and `embedding` identify the residual-state interpretation. `robust_box` gives the simultaneous price interval used in the analytic certificate. `no_sample_regrets` and `mixture_audit_price` are used in the baseline calculations documented by `check_acquisition_baselines.py`; they are parameter records, not a generic optimizer configuration interface.
