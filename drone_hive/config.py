"""Configuration and experimental conditions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


class StringEnum(str, Enum):
    """Python 3.10-compatible string enumeration."""

    def __str__(self) -> str:
        return self.value


class DeploymentPolicy(StringEnum):
    CARRIER_ONLY = "carrier_only"
    FIXED_RELAY = "fixed_relay"
    ADAPTIVE_FRONTIER = "adaptive_frontier"


@dataclass(slots=True)
class SimulationConfig:
    width: int = 120
    height: int = 72
    drones: int = 24
    steps: int = 240
    seed: int = 42
    policy: DeploymentPolicy = DeploymentPolicy.ADAPTIVE_FRONTIER
    initial_energy: float = 32.0
    movement_cost: float = 0.34
    idle_cost: float = 0.08
    transfer_rate: float = 1.3
    energy_radius: float = 24.0
    relay_range: float = 45.0
    map_radius: float = 2.8
    max_hives: int = 6
    deploy_interval: int = 40
    hive_failure_step: int | None = None

    def __post_init__(self) -> None:
        self.policy = DeploymentPolicy(self.policy)
        if self.width < 30 or self.height < 20:
            raise ValueError("environment is too small")
        if self.drones < 1 or self.steps < 1:
            raise ValueError("drones and steps must be positive")
        if self.energy_radius <= 0 or self.relay_range <= 0:
            raise ValueError("energy and relay radii must be positive")
        if self.max_hives < 1:
            raise ValueError("max_hives must be positive")

    def to_dict(self) -> dict[str, object]:
        values = asdict(self)
        values["policy"] = self.policy.value
        return values
