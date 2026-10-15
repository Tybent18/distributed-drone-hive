# Drone Hive — Research and Documentation Index

[Project home](../README.md) · [Research papers](../papers/README.md) · [Evidence catalog](../data/README.md) · [Demos](DEMOS.md)

This is the documentation home for the *software-only* Drone Hive project. It distinguishes **proposed architecture**, **working Python simulation**, **scripted 3D frontend**, and **validated experimental evidence**.

## Research and reproducibility

| Resource | Scope | Evidence status |
|---|---|---|
| [Research manuscript library](../papers/README.md) | Paper 1 and research-paper roadmap | Paper 1 is a draft, not peer reviewed |
| [Frozen Stage One evidence](../data/stage_one_baseline/runs/2026-09-15_relay-policy-v1/RUN.md) | 5 seeds, 24 drones, 240 steps; baseline policy comparison | Archived immutable simulation results |
| [Stage One methods](METHODS.md) | Carrier-only, fixed relay, adaptive frontier policies | Historical baseline, not a full hive-colony evaluation |
| [Stage One evidence guide](EVIDENCE.md) | Manifests, CSVs, figures, repeatability | Historical baseline |
| [Stage Two experiment protocol](STAGE_TWO_EXPERIMENT_PROTOCOL.md) | C0–C6, paired seeds, role-based colonies, physical constraints | Proposed study and engineering gates |
| [Stage Two initial engineering tests](STAGE_TWO_INITIAL_TEST_RESULTS.md) | 39 passing tests; 210+210 diagnostic rows | Diagnostic simulation only |
| [Experimental data catalog](../data/README.md) | Permanent files vs expiring CI artifacts | Source of truth for available evidence |
| [Charts and figure guide](FIGURES.md) | Plots and permitted interpretation | Stage One measured within the model |

## Design and implementation

| Resource | Purpose |
|---|---|
| [Architecture](ARCHITECTURE.md) | Independent colony authority, multi-network graph, hives, bees and eggs |
| [Founding design / vision](COLONY_VISION.md) | Research goal and design constraints |
| [Failure recovery](FAILURE_RECOVERY.md) | Emergency refuge and conditional egg radio bridging |
| [Safety and scope](SAFETY.md) | Limitations, operator oversight and environmental restrictions |
| [Research roadmap](ROADMAP.md) | Present validation and pending milestones |
| [Interactive demo gallery](DEMOS.md) | Six scripted WebGL GIFs and actual model-driven Python demonstrations |
| [Python simulator](../drone_hive/colony_web.py) | Source of numerical Stage Two engineering checks |
| [3D frontend](../frontend/) | Scripted interaction, **not** real Python state |

## Reproduction quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
pytest -q
python -m drone_hive.stage_two_smoke --output results/stage-two-diagnostic
python -m drone_hive.stage_two_ablation --output results/stage-two-ablation
```

The `results/` directory is diagnostic output, not a frozen publication dataset. Report the Git commit, package versions, all seeds and assumptions before claiming any comparison.

## Status of Stage Two PR

[Stage Two research PR #4](https://github.com/Tybent18/distributed-drone-hive/pull/4) contains the upgraded ledger, refuge checks, line-of-sight *geometry* and C0–C6 engineering ablation. Merge status and test verification are available on the PR page; do not interpret green CI as validation of physical drones.

**Policy:** preserve the September 2026 run unchanged, use new identifiers for every future study, and never label an illustrative GIF as experimental evidence.
