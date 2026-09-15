import pytest

from drone_hive.config import DeploymentPolicy, SimulationConfig


def test_policy_serializes_as_string() -> None:
    config = SimulationConfig(policy="fixed_relay")
    assert config.policy is DeploymentPolicy.FIXED_RELAY
    assert config.to_dict()["policy"] == "fixed_relay"


@pytest.mark.parametrize("field,value", [("drones", 0), ("steps", 0), ("max_hives", 0)])
def test_invalid_positive_fields(field: str, value: int) -> None:
    with pytest.raises(ValueError):
        SimulationConfig(**{field: value})
