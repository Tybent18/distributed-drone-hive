"""Reproducible experiment matrix and evidence export."""

from __future__ import annotations

import csv
import json
import platform
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .config import DeploymentPolicy, SimulationConfig
from .simulation import HiveSimulation, SimulationResult
from .visualization import plot_comparison, plot_trajectories


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_suite(
    output_dir: Path,
    *,
    seeds: tuple[int, ...] = (7, 21, 42, 84, 101),
    steps: int = 240,
    drones: int = 24,
    progress: Callable[[int, int, str], None] | None = None,
) -> list[SimulationResult]:
    output_dir.mkdir(parents=True, exist_ok=False)
    policies = tuple(DeploymentPolicy)
    conditions = [(DeploymentPolicy.CARRIER_ONLY, False)]
    conditions.extend(
        (policy, failure)
        for policy in (DeploymentPolicy.FIXED_RELAY, DeploymentPolicy.ADAPTIVE_FRONTIER)
        for failure in (False, True)
    )
    total = len(seeds) * len(conditions)
    results: list[SimulationResult] = []
    histories: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []

    for policy, failure in conditions:
        for seed in seeds:
            cfg = SimulationConfig(
                policy=policy,
                seed=seed,
                steps=steps,
                drones=drones,
                hive_failure_step=steps // 2 if failure else None,
            )
            result = HiveSimulation(cfg).run()
            results.append(result)
            histories.extend(result.history)
            final = result.final
            summaries.append(
                {
                    "policy": policy.value,
                    "seed": seed,
                    "failure_scenario": int(failure),
                    "final_coverage": final["coverage"],
                    "survival_rate": int(final["active_drones"]) / drones,
                    "mean_energy": final["mean_energy"],
                    "hives": final["hives"],
                    "connected_hive_fraction": final["connected_hive_fraction"],
                    "exploration_depth": final["exploration_depth"],
                }
            )
            if progress:
                progress(len(results), total, f"{policy.value} / seed {seed} / failure={failure}")

    aggregate: list[dict[str, object]] = []
    for policy, failure in conditions:
        group = [
            row
            for row in summaries
            if row["policy"] == policy.value and row["failure_scenario"] == int(failure)
        ]
        record: dict[str, object] = {
            "policy": policy.value,
            "failure_scenario": int(failure),
            "runs": len(group),
        }
        for metric in (
            "final_coverage",
            "survival_rate",
            "mean_energy",
            "hives",
            "connected_hive_fraction",
            "exploration_depth",
        ):
            values = np.asarray([float(row[metric]) for row in group])
            record[f"{metric}_mean"] = float(values.mean())
            record[f"{metric}_sd"] = float(values.std(ddof=1)) if len(values) > 1 else 0.0
        aggregate.append(record)

    _write_csv(output_dir / "step_metrics.csv", histories)
    _write_csv(output_dir / "run_summary.csv", summaries)
    _write_csv(output_dir / "aggregate_summary.csv", aggregate)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "study_type": "simulation",
        "stage": "Stage One computational validation",
        "seeds": list(seeds),
        "steps": steps,
        "drones": drones,
        "policies": [policy.value for policy in policies],
        "failure_scenarios": ["nominal", "single_relay_failure"],
        "python": platform.python_version(),
        "numpy": np.__version__,
        "claim_boundary": (
            "Results validate the simulator and policy comparison only; they do not establish "
            "RF feasibility, flight dynamics, hardware safety, or field performance."
        ),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    plot_comparison(summaries, output_dir / "policy_comparison.png")
    plot_trajectories(results, output_dir / "exploration_trajectories.png")
    return results
