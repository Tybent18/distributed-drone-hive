"""Federated colony invariants, midpoint egg continuity, and fault isolation."""

import pytest

from drone_hive.colony_web import ColonyWeb


def test_colonies_keep_independent_queens_and_staffing() -> None:
    network = ColonyWeb()
    network.validate_architecture()
    assert network.metrics()["colonies"] == 3
    for colony in "ABC":
        assert network.queen_for(colony).home == f"{colony}:N1"
        assert len([b for b in network.bees.values()
                    if b.colony == colony and b.role == "queen"]) == 1
        for level in range(2, 5):
            handlers = network.handlers_for(f"{colony}:N{level}")
            assert handlers["relay"] == 1
            assert handlers["retriever"] == 1


def test_midpoint_eggs_bridge_a_failed_middle_node() -> None:
    network = ColonyWeb(colonies=1)
    assert network.connected("A:N1", "A:N3")
    network.inject_failure(["A:N2"], "hardware")
    assert network.nests["A:N2"].health == "hardware"
    assert network.eggs["A:E1"].mode == "bridging"
    assert network.eggs["A:E2"].mode == "bridging"
    assert network.bridge_path("A:N2") == [
        "A:N1", "A:E1", "A:E2", "A:N3"
    ]
    assert network.connected("A:N1", "A:N3")
    assert any("BRIDGE RESTORED" in log for log in network.events)


def test_multi_node_failure_may_overwhelm_available_reserves() -> None:
    network = ColonyWeb(colonies=1)
    network.inject_failure(["A:N2", "A:N3"], "destroyed")
    assert network.metrics()["working_nodes"] == 3
    assert not network.connected("A:N1", "A:N3")
    assert network.eggs["A:E1"].mode == "bridging"
    assert any(bee.state in ("returning", "sheltering")
               for bee in network.bees.values() if bee.colony == "A")


def test_comms_only_failure_investigates_before_recall() -> None:
    network = ColonyWeb(colonies=1)
    network.inject_failure(["A:N2"], "communications")
    assert network.nests["A:N2"].health == "operational"
    assert network.nests["A:N2"].communications == "disconnected"
    assert network.metrics()["eggs_bridging"] == 0
    assert "neighbors" in network.investigate_comms("A:N2")
    assert not any(b.state == "returning" for b in network.bees.values())
    network.launch()
    network.step(8)
    assert any("comms timeout" in log for log in network.events)


def test_physical_failure_recalls_only_affected_colony() -> None:
    network = ColonyWeb(colonies=2)
    network.inject_failure(["A:N2"], "energy")
    assert network.nests["A:N2"].energy == 0
    assert all(b.state in ("docked", "surveying") for b in network.bees.values()
               if b.colony == "B")
    assert any(b.state == "returning" for b in network.bees.values()
               if b.colony == "A")


def test_assistance_is_not_command_takeover() -> None:
    network = ColonyWeb()
    assert network.request_assistance("A", "B")
    assert network.queen_for("A").colony == "A"
    assert network.queen_for("B").colony == "B"
    assert not network.request_assistance("A", "A")


def test_worker_payloads_are_configurable() -> None:
    network = ColonyWeb(colonies=1)
    network.assign_workers("A:N3", ["mapping", "structure_imaging", "environment"])
    network.validate_architecture()
    assert network.nests["A:N3"].workers == [
        "mapping", "structure_imaging", "environment"
    ]
    assert network.handlers_for("A:N3") == {"relay": 1, "retriever": 1}
    with pytest.raises(ValueError):
        network.assign_workers("A:N3", ["fictional_payload"])


def test_energy_conservation_and_depletion_in_abstract_model() -> None:
    network = ColonyWeb(colonies=1)
    network.solar_available = False
    network.launch()
    before = sum(n.energy for n in network.nests.values())
    before += sum(e.energy for e in network.eggs.values())
    before += sum(b.energy for b in network.bees.values())
    network.step(12)
    after = sum(n.energy for n in network.nests.values())
    after += sum(e.energy for e in network.eggs.values())
    after += sum(b.energy for b in network.bees.values())
    assert after <= before + 1e-7


def test_deterministic_network_after_identical_script() -> None:
    first, second = ColonyWeb(seed=5), ColonyWeb(seed=5)
    for network in (first, second):
        network.inject_failure(["A:N2", "B:N3"], "hardware")
        network.launch()
        network.step(10)
    assert first.metrics() == second.metrics()
    assert first.events == second.events


def test_repair_restores_node_and_returns_eggs_to_standby() -> None:
    network = ColonyWeb(colonies=1)
    network.inject_failure(["A:N2"], "hardware")
    network.queue_repair("A:N2")
    network.launch()
    network.step(18)
    assert network.nests["A:N2"].health == "operational"
    assert network.eggs["A:E1"].mode == "standby"
    assert network.eggs["A:E2"].mode == "standby"
