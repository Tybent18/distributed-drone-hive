"""Stage Two research readiness.

Passing checks validate narrow invariants in today's 2-D simulator.
Strict xfail tests deliberately document missing experimental prerequisites.
An expected failure is NOT proof of a safe/field-ready system. Remove each
xfail only after implementing the required behavior and verified measurements.
"""
from __future__ import annotations

from math import isclose

from drone_hive.colony_web import ColonyWeb


def test_every_commissioned_parent_child_has_a_midpoint_reserve_egg() -> None:
    model = ColonyWeb(colonies=3)
    for node in model.nests.values():
        if node.level < 2:
            continue
        parent = model.nests[node.parent]
        reserves = [
            egg for egg in model.eggs.values()
            if egg.left == parent.key and egg.right == node.key
        ]
        assert len(reserves) == 1
        egg = reserves[0]
        assert isclose(egg.x, (node.x + parent.x) / 2)
        assert isclose(egg.y, (node.y + parent.y) / 2)


def test_depleted_midpoint_egg_cannot_announce_a_verified_bridge() -> None:
    model = ColonyWeb(colonies=1)
    model.eggs["A:E1"].energy = 0
    model.inject_failure(["A:N2"], "hardware")
    assert model.bridge_path("A:N2") == []
    assert not any("BRIDGE RESTORED" in event for event in model.events)


def test_recovery_has_no_intercolony_command_takeover() -> None:
    model = ColonyWeb(colonies=3)
    model.inject_failure(["A:N2", "B:N3"], "hardware")
    assert model.queen_for("A").colony == "A"
    assert model.queen_for("B").colony == "B"
    assert model.request_assistance("A", "B")
    assert model.queen_for("B").home == "B:N1"


def test_emergency_refuges_must_never_be_overbooked() -> None:
    model = ColonyWeb(colonies=1)
    for node in model.nests.values():
        node.health = "hardware"
        node.energy = 0
    for egg in model.eggs.values():
        egg.mode = "standby"
    refuge = model.eggs["A:E1"]
    refuge.mode = "refuge"
    refuge.docking_slots = 2
    for bee in model.bees.values():
        bee.x, bee.y, bee.energy = refuge.x, refuge.y, 100
    model.recall("A")
    arrivals = [bee for bee in model.bees.values() if bee.destination == refuge.key]
    assert len(arrivals) <= refuge.docking_slots


def test_physical_repair_must_not_create_energy() -> None:
    model = ColonyWeb(colonies=1)
    model.inject_failure(["A:N2"], "energy")
    before = sum(node.energy for node in model.nests.values())
    before += sum(egg.energy for egg in model.eggs.values())
    before += sum(bee.energy for bee in model.bees.values())
    model.restore("A:N2")
    after = sum(node.energy for node in model.nests.values())
    after += sum(egg.energy for egg in model.eggs.values())
    after += sum(bee.energy for bee in model.bees.values())
    assert after <= before


def test_disabled_queen_must_not_retain_live_authority() -> None:
    model = ColonyWeb(colonies=1)
    model.queen_for("A").state = "disabled"
    with pytest.raises(ValueError, match="Queen|unavailable|authority"):
        model.queen_for("A")


def test_sensor_measurements_require_traceable_records() -> None:
    model = ColonyWeb(colonies=1)
    model.launch()
    model.step(5)
    bee = next(bee for bee in model.bees.values() if bee.mission == "mapping")
    assert bee.sensor_records
    assert all(row.synthetic and not row.calibrated for row in bee.sensor_records)
    assert all(
        getattr(row, "sensor_id", None)
        and getattr(row, "timestamp", None)
        and getattr(row, "checksum", None)
        for row in bee.sensor_records
    )
