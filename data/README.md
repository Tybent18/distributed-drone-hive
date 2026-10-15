# Drone Hive — Experimental Evidence Catalog

[Project home](../README.md) · [Documentation index](../docs/INDEX.md) · [Figures](../docs/FIGURES.md) · [Research manuscripts](../papers/README.md)

**Evidence status:** A GitHub CI check proves that code ran under the modeled assumptions; it does not prove a real-world UAV deployment. **Frozen Stage One** numerical results must not be combined into Stage Two effect estimates.

## Permanent versioned experimental evidence

| Date (UTC) | Run | Experimental question | Status | Files |
|---|---|---|---|---|
| 2026-09-15 | `2026-09-15_relay-policy-v1` | Carrier-only, fixed relay and adaptive frontier exploration | Frozen historical simulation baseline | [Run documentation](stage_one_baseline/runs/2026-09-15_relay-policy-v1/RUN.md) · [CSV aggregate](stage_one_baseline/runs/2026-09-15_relay-policy-v1/aggregate_summary.csv) · [Manifest](stage_one_baseline/runs/2026-09-15_relay-policy-v1/manifest.json) |

## Stage Two: reproducible engineering diagnostics — CI artifacts, NOT committed frozen evidence

| Experiment | Matrix | Location | Interpretation |
|---|---|---|---|
| Seven fault scenarios | 10 deterministic seeds × 7 scenarios × 3 phases = **210 rows** | [Validated CI run #38653201008](https://github.com/Tybent18/distributed-drone-hive/actions/runs/38653201008) → `stage-two-diagnostic-py3.12` | Invariant and fault instrumentation diagnostics |
| C0–C6 architecture ablation | 10 paired seeds × 7 conceptual arms × 3 conditions = **210 rows** | [Validated CI run #38653201008](https://github.com/Tybent18/distributed-drone-hive/actions/runs/38653201008) → `stage-two-ablation-py3.12` | Preliminary mechanism debug ONLY; resources and staffing not matched |
| Automated source checks | **39 tests passed** on Python 3.10 and 3.12 | [Validated CI](https://github.com/Tybent18/distributed-drone-hive/actions/runs/38653201008) | Passing software assertions under current model assumptions |

**CI artifacts expire.** These links are reproducibility aids; their results should not be described as an immutable public Stage Two dataset. This research hub *does not* silently convert those artifacts into archived evidence.

Recreate diagnostic rows after checking out the source version:

```bash
pip install -e ".[dev]"
pytest -q
python -m drone_hive.stage_two_smoke --output results/stage-two-diagnostic
python -m drone_hive.stage_two_ablation --output results/stage-two-ablation
```

Use the [Stage Two protocol](../docs/STAGE_TWO_EXPERIMENT_PROTOCOL.md) and [current findings](../docs/STAGE_TWO_INITIAL_TEST_RESULTS.md) when interpreting these runs. The model lacks balanced construction/energy costs, a complete physical charging system, calibrated sensors, and a verified comparative survival study.

## Evidence policy

New research-grade studies receive a unique immutable `data/<experiment_id>/runs/<YYYY-MM-DD_name-vN>/` folder with source commit, parameters, seeds, record hashes, per-run files, performance intervals, limitations and validation output. Never overwrite previous experiments to retrofit a preferred outcome.
