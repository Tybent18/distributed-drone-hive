"""Diagnostic Stage Two smoke matrix; NOT a controlled effectiveness comparison.

Usage: python -m drone_hive.stage_two_smoke --output results/stage_two_smoke
Runs are deterministic and record scenario-wise individual metrics. No historical
Stage One data is overwritten, no empirical hardware claims are made.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .colony_web import ColonyWeb

SCENARIOS: dict[str, tuple[tuple[str, ...], str | None]] = {
    "nominal": ((), None),
    "single_n2_hardware": (("A:N2",), "hardware"),
    "dual_n2_destroyed": (("A:N2", "B:N2"), "destroyed"),
    "communications_only": (("A:N2",), "communications"),
    "root_energy_failure": (("A:N0",), "energy"),
    "blocked_access": (("A:N3",), "blocked"),
    "low_egg_reserves": (("A:N2",), "hardware"),
}
DEFAULT_SEEDS = (7, 21, 42, 84, 101, 202, 303, 404, 505, 606)


def _metrics(model: ColonyWeb, seed: int, scenario: str, phase: str) -> dict[str, object]:
    counts = model.dock_occupancy()
    capacity = {**model.nests, **model.eggs}
    overbooked = sum(
        max(0, occupied - capacity[key].docking_slots)
        for key, occupied in counts.items()
        if key in capacity
    )
    return {
        "seed": seed,
        "scenario": scenario,
        "phase": phase,
        "tick": model.tick,
        "working_nodes": sum(n.health == "operational" for n in model.nests.values()),
        "radio_links": len(model.communication_links()),
        "bridge_a_n2": int(bool(model.bridge_path("A:N2"))),
        "drones": len(model.bees),
        "returning": sum(b.state == "returning" for b in model.bees.values()),
        "sheltering": sum(b.state == "sheltering" for b in model.bees.values()),
        "egg_refuge": sum(b.state == "egg_refuge" for b in model.bees.values()),
        "overbooked_docks": overbooked,
        "record_count": sum(len(b.sensor_records) for b in model.bees.values()),
        "recorded_mb": round(sum(b.recordings_mb for b in model.bees.values()), 5),
        "stored_energy": round(
            sum(n.energy for n in model.nests.values())
            + sum(e.energy for e in model.eggs.values())
            + sum(b.energy for b in model.bees.values()), 5
        ),
        "fault_discarded_energy": round(model.energy_failure_losses, 5),
    }


def run_matrix(*, seeds: tuple[int, ...], ticks: int) -> list[dict[str, object]]:
    if not seeds or ticks < 8:
        raise ValueError("Provide one or more seeds and at least 8 ticks")
    rows: list[dict[str, object]] = []
    for seed in seeds:
        for scenario, (targets, failure) in SCENARIOS.items():
            model = ColonyWeb(seed=seed, colonies=3)
            model.validate_architecture()
            if scenario == "low_egg_reserves":
                model.eggs["A:E1"].energy = 0
                model.eggs["A:E2"].energy = 0
            model.launch()
            model.step(5)
            rows.append(_metrics(model, seed, scenario, "pre_fault"))
            if failure:
                model.inject_failure(list(targets), failure)
            rows.append(_metrics(model, seed, scenario, "post_fault"))
            model.step(ticks - 5)
            rows.append(_metrics(model, seed, scenario, "end"))
            assert all(row >= 0 for row in [
                *(n.energy for n in model.nests.values()),
                *(e.energy for e in model.eggs.values()),
                *(b.energy for b in model.bees.values()),
            ])
            assert _metrics(model, seed, scenario, "audit")["overbooked_docks"] == 0
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/stage_two_smoke"))
    parser.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    parser.add_argument("--ticks", type=int, default=35)
    args = parser.parse_args()
    seeds = tuple(int(value) for value in args.seeds.split(","))
    rows = run_matrix(seeds=seeds, ticks=args.ticks)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "scenario_metrics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "stage": "Stage Two engineering smoke validation",
        "evidence_status": "diagnostic_only_not_comparative",
        "source": "ColonyWeb Python simulation",
        "seeds": list(seeds),
        "ticks": args.ticks,
        "scenarios": list(SCENARIOS),
        "rows": len(rows),
        "units": "dimensionless_synthetic",
        "limits": [
            "No physical line-of-sight, measured RF, or actual docking queue durations",
            "No fully modeled Retriever travel and modular construction",
            "No calibrated sensor payload or completed C0-C6 controlled arms",
            "Programmed fixed geography; no randomized terrain or failure timing",
        ],
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Stage Two DIAGNOSTIC: {len(seeds)} seeds × {len(SCENARIOS)} scenarios "
        f"× 3 observations = {len(rows)} metrics rows; output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
