import numpy as np

from drone_hive import DeploymentPolicy, HiveSimulation, SimulationConfig


def run(policy: DeploymentPolicy, *, failure: int | None = None):
    return HiveSimulation(
        SimulationConfig(policy=policy, seed=7, steps=90, drones=12, hive_failure_step=failure)
    ).run()


def test_run_is_deterministic() -> None:
    first = run(DeploymentPolicy.ADAPTIVE_FRONTIER)
    second = run(DeploymentPolicy.ADAPTIVE_FRONTIER)
    assert first.history == second.history
    np.testing.assert_allclose(first.drone_positions, second.drone_positions)


def test_metrics_remain_bounded() -> None:
    result = run(DeploymentPolicy.FIXED_RELAY)
    for row in result.history:
        assert 0 <= row["coverage"] <= 1
        assert 0 <= row["active_drones"] <= result.config.drones
        assert 0 <= row["connected_hive_fraction"] <= 1


def test_carrier_only_never_deploys_relay() -> None:
    result = run(DeploymentPolicy.CARRIER_ONLY)
    assert result.final["hives"] == 1


def test_fixed_policy_deploys_infrastructure() -> None:
    result = run(DeploymentPolicy.FIXED_RELAY)
    assert result.final["hives"] >= 2


def test_relay_failure_is_recorded() -> None:
    result = run(DeploymentPolicy.FIXED_RELAY, failure=45)
    assert result.final["failure_scenario"] == 1
    assert not result.hive_active[1]
