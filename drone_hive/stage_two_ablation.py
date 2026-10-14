"""Exploratory C0-C6 policy ablation; not yet a controlled outcome study.

All arms share the same 3-colony geography, seed and simulated N2 fault.
C0 has no N2 and receives a "not applicable" infrastructure fault outcome.
Costs, construction and sensor utility are not calibrated; comparisons are
mechanism diagnostics ONLY, not measurements of true survivability gains.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .colony_web import ColonyWeb

ARMS = {
    "C0": "N0/N1 core only, no expansion",
    "C1": "linear expansion without eggs",
    "C2": "branched web, no eggs",
    "C3": "branched web, reserve eggs centralized at roots",
    "C4": "branched web, midpoint refuge eggs without radio relay",
    "C5": "branched web, midpoint relay/refuge eggs",
    "C6": "midpoint eggs plus explicit assistance routes",
}
SEEDS = (7, 21, 42, 84, 101, 202, 303, 404, 505, 606)


def configure(model: ColonyWeb, arm: str) -> None:
    if arm not in ARMS:
        raise ValueError(arm)
    model.assistance_radio = arm == "C6"
    model.egg_radio = arm in ("C5", "C6")
    if arm == "C0":
        for node in model.nests.values():
            if node.level >= 2:
                node.health = "blocked"
                node.communications = "disconnected"
        model.eggs.clear()
    elif arm == "C1":
        for node in model.nests.values():
            if node.level == 4:
                node.health = "blocked"
                node.communications = "disconnected"
        model.eggs.clear()
    elif arm == "C2":
        model.eggs.clear()
    elif arm == "C3":
        for egg in model.eggs.values():
            root = model.nests[f"{egg.colony}:N0"]
            egg.x, egg.y = root.x, root.y
    # C4 permits local refuge but no egg communication. C3 is a logistics
    # depot analog, NOT a validated mid-distance replacement response.


def evaluate(seed: int, arm: str, fault: str, *, ticks: int = 40) -> dict[str, object]:
    model = ColonyWeb(seed=seed, colonies=3, radio_range=90, layout_jitter=4)
    configure(model, arm)
    model.launch()
    model.step(5)
    baseline_energy = model.total_stored_energy()
    if fault == "n2_hardware" and arm != "C0":
        model.inject_failure(["A:N2"], "hardware")
    elif fault == "comms_only" and arm != "C0":
        model.inject_failure(["A:N2"], "communications")
    # nominal no incident; C0 cannot experience absent N2 failure.
    at_fault = model.connected("A:N1", "A:N3") if arm != "C0" else False
    egg_bridge = bool(model.bridge_path("A:N2")) if arm != "C0" else False
    model.step(ticks - 5)
    occupied = model.dock_occupancy()
    overbooked = sum(
        max(0, count - ({**model.nests, **model.eggs})[key].docking_slots)
        for key, count in occupied.items()
        if key in model.nests or key in model.eggs
    )
    records = sum(len(bee.sensor_records) for bee in model.bees.values())
    return {
        "seed": seed, "arm": arm, "fault": fault,
        "fault_applicable": int(not (arm == "C0" and fault != "nominal")),
        "nodes_present": sum(n.health != "blocked" for n in model.nests.values()),
        "egg_count": len(model.eggs),
        "relay_bridge_at_fault": int(egg_bridge),
        "n1_n3_radio_at_fault": int(at_fault),
        "a_colony_sheltering": sum(
            b.colony == "A" and b.state == "sheltering"
            for b in model.bees.values()
        ),
        "end_radio_links": len(model.communication_links()),
        "overbooked_docks": overbooked,
        "synthetic_sensor_records": records,
        "energy_remaining": round(model.total_stored_energy(), 6),
        "energy_delta_post_start": round(
            model.total_stored_energy() - baseline_energy, 6
        ),
        "energy_ledger_residual": round(model.energy_balance_residual(), 8),
    }


def run_matrix(seeds: tuple[int, ...] = SEEDS, ticks: int = 40) -> list[dict[str, object]]:
    return [
        evaluate(seed, arm, fault, ticks=ticks)
        for seed in seeds
        for arm in ARMS
        for fault in ("nominal", "n2_hardware", "comms_only")
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/stage_two_ablation"))
    parser.add_argument("--seeds", default=",".join(map(str, SEEDS)))
    parser.add_argument("--ticks", type=int, default=40)
    args = parser.parse_args()
    seeds = tuple(int(s) for s in args.seeds.split(","))
    rows = run_matrix(seeds, args.ticks)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "arm_metrics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "stage": "Stage Two policy ablation engineering smoke",
        "status": "diagnostic_not_publication_quality",
        "arms": ARMS,
        "seeds": seeds,
        "faults": ["nominal", "n2_hardware", "comms_only"],
        "rows": len(rows),
        "geography": "fixed template with paired random positional jitter",
        "major_limitations": [
            "C0 structurally lacks N2; that fault is inapplicable, not a zero score",
            "Different arms do not carry identical valid staff and equipment costs",
            "No calibrated line-of-sight attenuation, flight physics or physical assembly",
            "Antenna obstacles are optional simple rectangles and not field data",
            "The baseline drone fleet includes idle drones from deactivated hives",
            "Synthetic event counters cannot estimate scientific mapping quality",
            "Energy units, simulated time and deployable hardware are uncalibrated",
        ],
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Diagnostic ablation: {len(rows)} rows across {len(ARMS)} arms, "
          f"{len(seeds)} seeds, 3 scenarios. Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
