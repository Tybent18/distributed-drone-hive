"""Stage Two ledger, obstacle path, and pre-publication ablation checks."""

from math import isclose

from drone_hive.colony_web import ColonyWeb
from drone_hive.stage_two_ablation import ARMS, evaluate


def test_solar_budget_and_dissipation_are_balanced() -> None:
    model = ColonyWeb(colonies=2)
    model.launch()
    model.step(20)
    assert abs(model.energy_balance_residual()) < 1e-6
    assert any(event.kind == "solar" for event in model.energy_ledger)
    assert all(
        isclose(event.debited, event.credited + event.dissipated, abs_tol=1e-7)
        for event in model.energy_ledger if event.kind != "solar"
    )


def test_fault_loss_energy_is_accounted() -> None:
    model = ColonyWeb(colonies=1)
    model.inject_failure(["A:N2"], "energy")
    assert abs(model.energy_balance_residual()) < 1e-6
    assert any(event.kind == "fault_loss" for event in model.energy_ledger)
    model.restore("A:N2")
    assert abs(model.energy_balance_residual()) < 1e-6


def test_radio_obstacle_blocks_line_of_sight() -> None:
    clear = ColonyWeb(colonies=1, radio_range=90)
    blocked = ColonyWeb(colonies=1, radio_range=90,
                        obstacles=((160, 125, 180, 145),))
    # The line joining A:N1 (135,143) and A:N2 (216,132)
    # crosses the opaque rectangular test obstacle.
    assert clear.radio_reachable(clear.nests["A:N1"], clear.nests["A:N2"])
    assert not blocked.radio_reachable(blocked.nests["A:N1"], blocked.nests["A:N2"])


def test_short_radio_range_blocks_egg_bridge() -> None:
    model = ColonyWeb(colonies=1, radio_range=10)
    model.inject_failure(["A:N2"], "hardware")
    assert model.bridge_path("A:N2") == []


def test_all_ablation_arms_run_and_preserve_energy() -> None:
    for arm in ARMS:
        row = evaluate(7, arm, "n2_hardware", ticks=12)
        assert row["overbooked_docks"] == 0
        assert abs(row["energy_ledger_residual"]) < 1e-6
        if arm == "C0":
            assert row["fault_applicable"] == 0
        else:
            assert row["fault_applicable"] == 1
