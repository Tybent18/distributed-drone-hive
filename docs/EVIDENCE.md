# Evidence guide

[← Project home](../README.md) · [Methods](METHODS.md) · [Roadmap](ROADMAP.md)

Every run exports a self-describing evidence bundle:

- `manifest.json`: runtime, parameters, conditions, and claim boundary;
- `step_metrics.csv`: policy, seed, scenario, and time-step telemetry;
- `run_summary.csv`: final outcome for each independent run;
- `aggregate_summary.csv`: mean and sample standard deviation by condition;
- `policy_comparison.png`: coverage and survival under nominal and failure conditions;
- `exploration_trajectories.png`: five-seed progression over time.

The checked-in baseline is a software validation dataset. It is suitable for auditing deterministic execution, metric production, and relative behavior inside this model. It is not evidence that RF or microwave transfer will power a physical drone swarm.

The [data catalog](../data/README.md) indexes committed evidence by UTC collection date and immutable run ID. The first frozen bundle is [`2026-09-15_relay-policy-v1`](../data/stage_one_baseline/runs/2026-09-15_relay-policy-v1/). Smoke runs and incomplete jobs are not part of that catalog.
