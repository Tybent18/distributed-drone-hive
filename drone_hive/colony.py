"""Interactive colony mission prototype; intentionally separate from frozen Stage One.

Dimensionless 2-D coordination model only. No physical RF power-transfer claims.
All contingency egg activations require an explicit operator command.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from random import Random


@dataclass
class Hive:
    id: int
    x: float
    y: float
    active: bool = True
    label: str = ""


@dataclass
class Egg:
    id: int
    x: float
    y: float
    active: bool = False
    deploying: bool = False


@dataclass
class Bee:
    id: int
    x: float
    y: float
    role: str = "unassigned"
    home: int = 0
    energy: float = 100.0
    state: str = "docked"
    target_egg: int | None = None


class ColonyMission:
    """Operator-directed reconnaissance in abstract hazardous terrain.

    A base station, satellite hives, drone roles, and emergency reserve relays
    are distinct model entities. 'Eggs' represent stored reserve resources;
    activation is an abstract repair of connectivity, not demonstrated energy
    harvesting or wireless charging. Old experiment evidence is not changed.
    """

    width = 120
    height = 72
    relay_range = 27.0
    reserve_fraction = 0.30
    bee_speed = 1.3
    hazard_zones = ((64, 16, 82, 38), (88, 41, 105, 58))

    def __init__(self, seed: int = 42, count: int = 12):
        self.seed = seed
        self.rng = Random(seed)
        self.tick = 0
        self.running = False
        self.operator_connected = True
        self.hives = [
            Hive(0, 12, 36, label="Node 0 · Carrier"),
            Hive(1, 32, 36, label="Node 1 · Nest"),
            Hive(2, 55, 36, label="Node 2 · Forward nest"),
        ]
        self.eggs = [Egg(0, 32, 41), Egg(1, 55, 41)]
        self.bees = [
            Bee(i, 12 + (i % 4) * 0.8, 36 + (i // 4) * 0.8)
            for i in range(count)
        ]
        self.mapped: set[tuple[int, int]] = set()
        self.pending_egg: int | None = None
        self.events: list[str] = []
        self._event("Mission setup: select bees, assign roles, then start reconnaissance")

    def _event(self, message: str) -> None:
        self.events.append(f"T{self.tick:04d}  {message}")
        self.events = self.events[-100:]

    def _distance(self, a: object, b: object) -> float:
        return hypot(a.x - b.x, a.y - b.y)

    def connected_ids(self) -> set[tuple[str, int]]:
        """Compute root-connected active infrastructure, independent of node order."""
        active = {("h", h.id): h for h in self.hives if h.active}
        active.update({("e", e.id): e for e in self.eggs if e.active})
        connected: set[tuple[str, int]] = {("h", 0)} if self.hives[0].active else set()
        while True:
            more = {key for key, obj in active.items()
                    if key not in connected and
                    any(self._distance(obj, active[parent]) <= self.relay_range
                        for parent in connected)}
            if not more:
                return connected
            connected |= more

    def is_hive_connected(self, hive_id: int) -> bool:
        return ("h", hive_id) in self.connected_ids()

    def assign_role(self, bee_id: int, role: str, home: int = 0) -> None:
        if self.running:
            raise ValueError("Pause the mission before assigning roles")
        if role not in {"queen", "worker", "handler", "unassigned"}:
            raise ValueError("Unknown bee role")
        if home < 0 or home >= len(self.hives) or not self.hives[home].active:
            raise ValueError("Select an active home hive")
        bee = self.bees[bee_id]
        if role == "queen" and any(b.id != bee_id and b.role == "queen" and b.home == home
                                    for b in self.bees):
            raise ValueError("Each nest supports one Queen")
        bee.role = role
        bee.home = home
        bee.x, bee.y = self.hives[home].x, self.hives[home].y
        bee.energy = 100.0
        bee.state = "docked" if role != "unassigned" else "unassigned"
        bee.target_egg = None
        self._event(f"Bee {bee_id} assigned {role} at Node {home}")

    def add_hive(self, x: float, y: float) -> int:
        if self.running:
            raise ValueError("Pause before placing infrastructure")
        node_id = len(self.hives)
        self.hives.append(Hive(node_id, float(x), float(y), label=f"Node {node_id} · Nest"))
        self._event(f"Placed Node {node_id}")
        return node_id

    def add_egg(self, x: float, y: float) -> int:
        if self.running:
            raise ValueError("Pause before placing reserve resources")
        egg_id = len(self.eggs)
        self.eggs.append(Egg(egg_id, float(x), float(y)))
        self._event(f"Placed standby egg {egg_id}")
        return egg_id

    def start(self) -> None:
        if not any(b.role == "worker" for b in self.bees):
            raise ValueError("Assign at least one worker before starting")
        self.running = True
        self._event("Reconnaissance started")

    def pause(self) -> None:
        self.running = False
        self._event("Mission paused")

    def _find_repair_egg(self) -> int | None:
        connected = self.connected_ids()
        disconnected = [h for h in self.hives if h.active and ("h", h.id) not in connected]
        roots = [h for h in self.hives if ("h", h.id) in connected]
        roots += [e for e in self.eggs if ("e", e.id) in connected]
        if not disconnected or not roots:
            return None
        for egg in self.eggs:
            if egg.active or egg.deploying:
                continue
            if any(self._distance(egg, root) <= self.relay_range for root in roots) and any(
                self._distance(egg, node) <= self.relay_range for node in disconnected
            ):
                return egg.id
        return None

    def fail_hive(self, hive_id: int) -> None:
        if hive_id < 0 or hive_id >= len(self.hives):
            raise ValueError("Invalid node")
        self.hives[hive_id].active = False
        self._event(f"ALERT: Node {hive_id} offline")
        self.pending_egg = self._find_repair_egg()
        if self.pending_egg is not None:
            self._event(f"Request operator approval for standby egg {self.pending_egg}")
        if hive_id == 0:
            self.lose_operator_link()

    def authorize_contingency(self) -> bool:
        """Authorization arms one egg; a connected handler must physically reach it."""
        if not self.operator_connected or self.pending_egg is None:
            return False
        egg = self.eggs[self.pending_egg]
        handlers = [b for b in self.bees if b.role == "handler"
                    and b.state != "inactive" and self.is_hive_connected(b.home)
                    and b.energy > self.reserve_fraction * 100]
        if not handlers:
            self._event("Recovery blocked: no connected handler above reserve")
            return False
        handler = min(handlers, key=lambda bee: self._distance(bee, egg))
        egg.deploying = True
        handler.target_egg = egg.id
        handler.state = "deploying"
        self.pending_egg = None
        self._event(f"Operator approved egg {egg.id}; handler {handler.id} dispatched")
        return True

    def lose_operator_link(self) -> None:
        self.operator_connected = False
        self.running = True  # permit bounded retreat to local shelters
        self.pending_egg = None
        for egg in self.eggs:
            if egg.deploying:
                egg.deploying = False
        for bee in self.bees:
            bee.target_egg = None
            if bee.role == "queen":
                bee.state = "return_root"
            elif bee.role in {"worker", "handler"}:
                bee.state = "return_home"
        self._event("OPERATOR LINK LOST: Queens to root; others to nests / stasis")

    def restore_operator_link(self) -> None:
        self.operator_connected = True
        self.pending_egg = self._find_repair_egg()
        self._event("Operator link restored; pending recovery requires new approval")

    def _move_toward(self, bee: Bee, x: float, y: float) -> None:
        dx, dy = x - bee.x, y - bee.y
        d = hypot(dx, dy)
        if d <= 1e-8:
            return
        speed = min(self.bee_speed, d)
        bee.x += dx / d * speed
        bee.y += dy / d * speed
        bee.energy = max(0.0, bee.energy - 0.65 * speed)
        if bee.energy <= 0:
            bee.state = "inactive"

    def _is_hazard(self, x: float, y: float) -> bool:
        return any(a <= x <= c and b <= y <= d for a, b, c, d in self.hazard_zones)

    def step(self) -> dict[str, float | int]:
        if not self.running:
            return self.metrics()
        self.tick += 1
        for bee in self.bees:
            if bee.state in {"inactive", "stasis", "unassigned"} or bee.role == "unassigned":
                continue
            home = self.hives[bee.home]
            if bee.state == "deploying":
                egg = self.eggs[bee.target_egg] if bee.target_egg is not None else None
                if egg is None or not egg.deploying:
                    bee.state = "return_home"
                    continue
                self._move_toward(bee, egg.x, egg.y)
                if self._distance(bee, egg) < 1.5 and bee.state != "inactive":
                    egg.deploying = False
                    egg.active = True
                    bee.target_egg = None
                    bee.state = "return_home"
                    self._event(f"Handler {bee.id} activated egg {egg.id}: relay restored if connected")
                continue
            if bee.state in {"return_home", "return_root"}:
                target = self.hives[0] if bee.state == "return_root" else home
                self._move_toward(bee, target.x, target.y)
                if self._distance(bee, target) < 1.5 and bee.state != "inactive":
                    bee.state = "stasis" if not self.operator_connected else "docked"
                continue
            if not self.operator_connected:
                continue
            if bee.role == "queen" or bee.role == "handler":
                bee.state = "docked"
                continue
            if bee.role == "worker":
                if bee.energy <= self.reserve_fraction * 100:
                    bee.state = "return_home"
                    continue
                if not self.is_hive_connected(bee.home):
                    bee.state = "return_home"
                    continue
                bee.state = "surveying"
                nx = max(0.0, min(self.width - 1, bee.x + self.rng.uniform(-0.2, 2.0)))
                ny = max(0.0, min(self.height - 1, bee.y + self.rng.uniform(-1.8, 1.8)))
                if self._is_hazard(nx, ny):
                    bee.state = "hazard_avoidance"
                    nx, ny = bee.x - 0.8, bee.y + self.rng.choice((-2.0, 2.0))
                self._move_toward(bee, nx, max(0.0, min(self.height - 1, ny)))
                if bee.state != "inactive":
                    self.mapped.add((int(bee.x), int(bee.y)))
            if bee.state == "docked" and self.is_hive_connected(bee.home):
                bee.energy = min(100.0, bee.energy + 0.5)
        if self.pending_egg is None and self.operator_connected and not any(e.deploying for e in self.eggs):
            found = self._find_repair_egg()
            if found is not None:
                self.pending_egg = found
                self._event(f"Recovery option: egg {found} awaiting operator approval")
        return self.metrics()

    def metrics(self) -> dict[str, float | int]:
        connected = self.connected_ids()
        return {
            "tick": self.tick,
            "workers": sum(b.role == "worker" for b in self.bees),
            "handlers": sum(b.role == "handler" for b in self.bees),
            "queens": sum(b.role == "queen" for b in self.bees),
            "connected_hives": sum(("h", h.id) in connected for h in self.hives),
            "active_hives": sum(h.active for h in self.hives),
            "active_eggs": sum(e.active for e in self.eggs),
            "pending_approval": int(self.pending_egg is not None),
            "mapped_cells": len(self.mapped),
            "disabled_bees": sum(b.state == "inactive" for b in self.bees),
        }
