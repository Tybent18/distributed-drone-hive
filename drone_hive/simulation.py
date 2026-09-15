"""Energy-constrained swarm simulation and infrastructure policies."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import DeploymentPolicy, SimulationConfig


@dataclass(slots=True)
class SimulationResult:
    config: SimulationConfig
    history: list[dict[str, float | int | str]]
    drone_positions: np.ndarray
    drone_energy: np.ndarray
    active: np.ndarray
    hive_positions: np.ndarray
    hive_active: np.ndarray
    mapped: np.ndarray

    @property
    def final(self) -> dict[str, float | int | str]:
        return self.history[-1]


class HiveSimulation:
    """A deterministic 2-D abstraction of infrastructure-driven exploration."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        origin = np.array([8.0, config.height / 2])
        self.positions = origin + self.rng.normal(0, 1.2, (config.drones, 2))
        self.energy = np.full(config.drones, config.initial_energy, dtype=float)
        self.active = np.ones(config.drones, dtype=bool)
        self.hives = [origin.copy()]
        self.hive_active = [True]
        self.mapped = np.zeros((config.height, config.width), dtype=bool)
        self.history: list[dict[str, float | int | str]] = []
        self._failed_once = False

    def _connected_hives(self) -> np.ndarray:
        n = len(self.hives)
        connected = np.zeros(n, dtype=bool)
        connected[0] = bool(self.hive_active[0])
        changed = True
        while changed:
            changed = False
            for i in range(n):
                if connected[i] or not self.hive_active[i]:
                    continue
                if any(
                    connected[j]
                    and np.linalg.norm(self.hives[i] - self.hives[j]) <= self.config.relay_range
                    for j in range(n)
                ):
                    connected[i] = True
                    changed = True
        return connected

    def _energy_field(self, points: np.ndarray) -> np.ndarray:
        connected = self._connected_hives()
        live = np.asarray(self.hives)[connected]
        if not len(live):
            return np.zeros(len(points))
        distance = np.linalg.norm(points[:, None, :] - live[None, :, :], axis=2)
        contribution = np.exp(-((distance / self.config.energy_radius) ** 2))
        return contribution.max(axis=1) * self.config.transfer_rate

    def _mark_mapped(self) -> None:
        yy, xx = np.ogrid[: self.config.height, : self.config.width]
        for point in self.positions[self.active]:
            mask = (xx - point[0]) ** 2 + (yy - point[1]) ** 2 <= self.config.map_radius**2
            self.mapped[mask] = True

    def _frontier_direction(self, point: np.ndarray) -> np.ndarray:
        candidates = self.rng.normal(size=(12, 2))
        candidates[:, 0] = np.abs(candidates[:, 0]) + 0.25
        candidates /= np.maximum(np.linalg.norm(candidates, axis=1, keepdims=True), 1e-9)
        proposed = np.clip(
            point + candidates * 3.0, [0, 0], [self.config.width - 1, self.config.height - 1]
        )
        coords = proposed.astype(int)
        unexplored = ~self.mapped[coords[:, 1], coords[:, 0]]
        nearest_hive = np.min(
            np.linalg.norm(proposed[:, None, :] - np.asarray(self.hives)[None, :, :], axis=2),
            axis=1,
        )
        energy_safety = np.exp(-((nearest_hive / (self.config.energy_radius * 1.25)) ** 4))
        scores = unexplored.astype(float) * 1.8 + energy_safety + self.rng.uniform(0, 0.2, 12)
        return candidates[int(np.argmax(scores))]

    def _deploy_hive(self, step: int) -> None:
        cfg = self.config
        if cfg.policy is DeploymentPolicy.CARRIER_ONLY or len(self.hives) >= cfg.max_hives:
            return
        if step == 0 or step % cfg.deploy_interval:
            return
        if cfg.policy is DeploymentPolicy.FIXED_RELAY:
            x = min(8 + len(self.hives) * cfg.energy_radius * 0.82, cfg.width - 5)
            y = cfg.height / 2
            candidate = np.array([x, y])
        else:
            live = self.positions[self.active]
            if not len(live):
                return
            distance_from_origin = np.linalg.norm(live - self.hives[0], axis=1)
            frontier = live[np.argsort(distance_from_origin)[-max(2, len(live) // 4) :]]
            candidate = np.median(frontier, axis=0)
            parent = np.asarray(self.hives)[
                np.argmin(np.linalg.norm(np.asarray(self.hives) - candidate, axis=1))
            ]
            delta = candidate - parent
            distance = np.linalg.norm(delta)
            if distance < cfg.energy_radius * 0.55:
                return
            if distance > cfg.relay_range * 0.92:
                candidate = parent + delta / distance * cfg.relay_range * 0.9
        self.hives.append(np.clip(candidate, [1, 1], [cfg.width - 2, cfg.height - 2]))
        self.hive_active.append(True)

    def step(self, step: int) -> dict[str, float | int | str]:
        cfg = self.config
        self._deploy_hive(step)
        if (
            cfg.hive_failure_step is not None
            and step >= cfg.hive_failure_step
            and len(self.hives) > 1
            and not self._failed_once
        ):
            self.hive_active[1] = False
            self._failed_once = True

        indices = np.flatnonzero(self.active)
        if len(indices):
            directions = np.array([self._frontier_direction(self.positions[i]) for i in indices])
            speed = self.rng.uniform(0.65, 1.3, len(indices))
            self.positions[indices] += directions * speed[:, None]
            self.positions[indices] = np.clip(
                self.positions[indices], [0, 0], [cfg.width - 1, cfg.height - 1]
            )
            received = self._energy_field(self.positions[indices])
            cost = cfg.idle_cost + cfg.movement_cost * speed
            self.energy[indices] = np.minimum(
                cfg.initial_energy, self.energy[indices] + received - cost
            )
            self.active[indices[self.energy[indices] <= 0]] = False
        self._mark_mapped()

        connected = self._connected_hives()
        record: dict[str, float | int | str] = {
            "step": step,
            "policy": cfg.policy.value,
            "seed": cfg.seed,
            "failure_scenario": int(cfg.hive_failure_step is not None),
            "coverage": float(self.mapped.mean()),
            "active_drones": int(self.active.sum()),
            "mean_energy": float(self.energy[self.active].mean()) if self.active.any() else 0.0,
            "hives": len(self.hives),
            "connected_hive_fraction": float(connected.mean()),
            "exploration_depth": float(self.positions[:, 0].max()),
        }
        self.history.append(record)
        return record

    def run(self) -> SimulationResult:
        for step in range(self.config.steps):
            self.step(step)
        return SimulationResult(
            self.config,
            self.history,
            self.positions.copy(),
            self.energy.copy(),
            self.active.copy(),
            np.asarray(self.hives),
            np.asarray(self.hive_active),
            self.mapped.copy(),
        )
