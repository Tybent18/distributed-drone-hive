"""Federated Drone Hive: graph-based physical colony architecture simulation.

Separate from the immutable September 2026 Stage One research experiment.
All lengths, energy, hazards, charging and links are dimensionless abstractions.
No claim of actual RF power transmission, flight or real drone autonomy.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import hypot
from random import Random

WORKER_TASKS = ("scout", "mapping", "structure_imaging", "environment")
SENSORS = {
    "scout": ("video", "depth", "telemetry"),
    "mapping": ("depth", "lidar", "telemetry"),
    "structure_imaging": ("video", "photogrammetry", "telemetry"),
    "environment": ("thermal", "environment", "telemetry"),
}
FAILURES = ("communications", "energy", "hardware", "destroyed", "blocked")
PHYSICAL_FAILURES = frozenset(FAILURES[1:])
COMM_RANGE = 90.0
RETURN_RESERVE = 30.0
TRANSFER_EFFICIENCY = 0.70  # EXPLICITLY hypothetical, not measured wireless transfer


@dataclass
class Nest:
    key: str
    colony: str
    level: int
    x: float
    y: float
    parent: str | None
    kind: str
    workers: list[str] = field(default_factory=list)
    health: str = "operational"
    communications: str = "online"
    energy: float = 100.0
    battery_capacity: float = 100.0
    docking_slots: int = 6
    inventory: dict[str, int] = field(default_factory=dict)
    deployment_state: str = "commissioned"
    recordings_mb: float = 0.0


@dataclass
class Bee:
    key: str
    colony: str
    home: str
    role: str
    mission: str
    sensors: tuple[str, ...]
    x: float
    y: float
    energy: float = 100.0
    state: str = "docked"
    destination: str | None = None
    recordings_mb: float = 0.0


@dataclass
class Egg:
    key: str
    colony: str
    left: str
    right: str
    x: float
    y: float
    energy: float = 45.0
    capacity: float = 45.0
    mode: str = "standby"
    docking_slots: int = 2
    buffered_mb: float = 0.0


class ColonyWeb:
    """Graph network with independent command authority and assistance-only links.

    Independent command: each colony has exactly one N1 Queen. N0 is an
    energy root. N2+ get one relay and one retriever Handler, mission-based
    Workers. Deployment parentage, radio reachability and power transfer
    are deliberately distinct relationships.
    """

    def __init__(self, seed: int = 42, colonies: int = 3) -> None:
        if colonies < 1 or colonies > 5:
            raise ValueError("Number of colonies must be between 1 and 5")
        self.rng = Random(seed)
        self.seed = seed
        self.tick = 0
        self.running = False
        self.operator_online = True
        self.solar_available = True
        self.nests: dict[str, Nest] = {}
        self.eggs: dict[str, Egg] = {}
        self.bees: dict[str, Bee] = {}
        self.events: list[str] = []
        self.assistance: set[tuple[str, str]] = set()
        self.hazards = ((260, 112, 360, 208), (65, 300, 177, 384))
        self.pending_repairs: dict[str, int] = {}
        self.communication_timeout = 7
        self._lost_since: dict[str, int] = {}
        for i in range(colonies):
            self._seed_colony(chr(65 + i), i)
        self._make_assistance_routes()
        self._log("Multi-colony expedition ready; each N1 has one independent Queen")

    def _log(self, description: str) -> None:
        self.events.append(f"T{self.tick:04d}  {description}")
        self.events = self.events[-300:]

    @staticmethod
    def distance(a: Nest | Egg | Bee, b: Nest | Egg | Bee) -> float:
        return hypot(a.x - b.x, a.y - b.y)

    def _seed_colony(self, colony: str, index: int) -> None:
        # Dense 2-D mission map with branching, not a single straight line.
        layouts = (
            ((62, 115), (135, 143), (216, 132), (303, 115), (242, 200)),
            ((62, 245), (135, 248), (216, 259), (303, 280), (232, 330)),
            ((390, 200), (451, 206), (513, 175), (573, 137), (525, 275)),
            ((390, 327), (451, 333), (517, 351), (578, 368), (521, 294)),
            ((344, 55), (411, 62), (471, 40), (531, 69), (479, 120)),
        )
        points = layouts[index]
        parents = (None, f"{colony}:N0", f"{colony}:N1", f"{colony}:N2", f"{colony}:N2")
        for level, (position, parent) in enumerate(zip(points, parents, strict=True)):
            key = f"{colony}:N{level}"
            kind = ("energy_root" if level == 0 else "queen_hive" if level == 1
                    else "expansion_hive")
            nest = Nest(
                key, colony, level, *position, parent, kind,
                inventory={"foldable_chassis": 1, "battery_module": 2,
                           "comms_module": 2, "contingency_module": 1},
                docking_slots=10 if level == 1 else 6,
            )
            self.nests[key] = nest
            if level == 1:
                self._add_bee(colony, key, "queen", "command", ("telemetry", "video"))
                for n in range(3):
                    self._add_bee(
                        colony, key, "handler",
                        ("acting_queen", "construction", "retrieval")[n],
                        ("video", "telemetry"),
                    )
            elif level > 1:
                self._add_bee(
                    colony, key, "handler", "relay", ("radio", "telemetry", "video")
                )
                self._add_bee(
                    colony, key, "handler", "retriever", ("video", "telemetry", "depth")
                )
            if level:
                assignments = ("scout", "mapping", "structure_imaging") if level < 3 else (
                    ("mapping", "environment") if level == 3 else ("scout",)
                )
                for task in assignments:
                    self._add_bee(colony, key, "worker", task, SENSORS[task])
                nest.workers = list(assignments)
            if level >= 2 and parent is not None:
                p = self.nests[parent]
                egg_key = f"{colony}:E{level-1}"
                self.eggs[egg_key] = Egg(
                    egg_key, colony, parent, key,
                    (p.x + nest.x) / 2, (p.y + nest.y) / 2,
                )

    def _add_bee(
        self, colony: str, home: str, role: str, mission: str, sensors: tuple[str, ...]
    ) -> None:
        number = sum(1 for bee in self.bees.values() if bee.colony == colony) + 1
        key = f"{colony}:B{number:02d}"
        nest = self.nests[home]
        self.bees[key] = Bee(key, colony, home, role, mission, sensors, nest.x, nest.y)

    def _make_assistance_routes(self) -> None:
        # Cross-colony links carry data and rescue requests, never command.
        for left, right in (("A:N3", "B:N3"), ("A:N4", "B:N2"),
                            ("A:N2", "C:N1"), ("B:N4", "C:N2")):
            if left in self.nests and right in self.nests:
                self.assistance.add(tuple(sorted((left, right))))

    def queen_for(self, colony: str) -> Bee:
        queens = [
            bee for bee in self.bees.values()
            if bee.colony == colony and bee.role == "queen"
        ]
        if len(queens) != 1 or queens[0].home != f"{colony}:N1":
            raise ValueError("Exactly one Queen is required at colony Node 1")
        return queens[0]

    def handlers_for(self, nest_key: str) -> dict[str, int]:
        handlers: dict[str, int] = {}
        for bee in self.bees.values():
            if bee.home == nest_key and bee.role == "handler":
                handlers[bee.mission] = handlers.get(bee.mission, 0) + 1
        return handlers

    def validate_architecture(self) -> None:
        for colony in {nest.colony for nest in self.nests.values()}:
            self.queen_for(colony)
            primary = self.handlers_for(f"{colony}:N1")
            if sum(primary.values()) != 3:
                raise ValueError(f"{colony} Node 1 requires three Handlers")
        for node in self.nests.values():
            if node.level >= 2:
                staff = self.handlers_for(node.key)
                if staff.get("relay") != 1 or staff.get("retriever") != 1:
                    raise ValueError(f"{node.key} requires relay + retriever Handlers")
                if any(bee.role == "queen" and bee.home == node.key
                       for bee in self.bees.values()):
                    raise ValueError("No Queens permitted downstream")

    def assign_workers(self, node_key: str, tasks: list[str]) -> None:
        node = self.nests[node_key]
        if self.running or node.level == 0:
            raise ValueError("Pause the simulation; workers belong to hive nests")
        if any(task not in WORKER_TASKS for task in tasks):
            raise ValueError("Unknown worker specialization")
        for key in list(self.bees):
            bee = self.bees[key]
            if bee.home == node_key and bee.role == "worker":
                del self.bees[key]
        node.workers = list(tasks)
        for task in tasks:
            self._add_bee(node.colony, node_key, "worker", task, SENSORS[task])
        self._log(f"{node_key}: worker payload configuration -> {tasks}")

    def _network_nodes(self) -> dict[str, Nest | Egg]:
        return {
            **{key: node for key, node in self.nests.items()
               if node.health not in PHYSICAL_FAILURES
               and node.communications == "online" and node.energy > 0},
            **{key: egg for key, egg in self.eggs.items()
               if egg.mode in ("bridging", "refuge") and egg.energy > 0},
        }

    def communication_links(self, include_assistance: bool = True) -> set[tuple[str, str]]:
        """Geometry-constrained radio mesh; assistance links never convey authority."""
        active = self._network_nodes()
        ids = sorted(active)
        links: set[tuple[str, str]] = set()
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if active[a].colony != active[b].colony:
                    if not include_assistance or (a, b) not in self.assistance:
                        continue
                if self.distance(active[a], active[b]) <= COMM_RANGE:
                    links.add((a, b))
        return links

    def connected(self, a: str, b: str) -> bool:
        active = self._network_nodes()
        if a not in active or b not in active:
            return False
        graph: dict[str, set[str]] = {key: set() for key in active}
        for left, right in self.communication_links():
            graph[left].add(right)
            graph[right].add(left)
        queue = deque([a])
        found = {a}
        while queue:
            node = queue.popleft()
            if node == b:
                return True
            for nxt in graph[node] - found:
                found.add(nxt)
                queue.append(nxt)
        return False

    def bridge_path(self, failed_node: str) -> list[str]:
        """A path around the failed node, through at least two active eggs."""
        failed = self.nests[failed_node]
        if failed.level < 2 or failed.parent is None:
            return []
        parent = failed.parent
        # Child needs at least one downstream descendant for a full bypass.
        children = [
            n.key for n in self.nests.values()
            if n.parent == failed_node and n.health == "operational"
        ]
        if not children:
            return []
        eggs = [
            egg for egg in self.eggs.values()
            if egg.colony == failed.colony and egg.mode in ("bridging", "refuge")
        ]
        active = self._network_nodes()
        for child in children:
            if parent not in active or child not in active:
                continue
            for one in eggs:
                if (one.left == parent and one.right == failed_node
                    and one.key in active):
                    for two in eggs:
                        if (two.left == failed_node and two.right == child
                            and two.key in active
                            and self.distance(one, two) <= COMM_RANGE
                            and self.distance(active[parent], one) <= COMM_RANGE
                            and self.distance(two, active[child]) <= COMM_RANGE):
                            return [parent, one.key, two.key, child]
        return []

    def _activate_neighbor_eggs(self, keys: set[str]) -> None:
        for egg in self.eggs.values():
            if egg.left in keys or egg.right in keys:
                if egg.mode == "standby" and egg.energy > 0:
                    egg.mode = "bridging"
                    self._log(f"{egg.key}: micro-nest safety activation (bridge/refuge)")
        for failed in sorted(keys):
            path = self.bridge_path(failed)
            if path:
                self._log(f"{failed}: BRIDGE RESTORED through {' ↔ '.join(path)}")
            else:
                self._log(f"{failed}: no verified egg bridge; safe retreat remains active")

    def inject_failure(self, keys: list[str], kind: str) -> None:
        if kind not in FAILURES:
            raise ValueError(f"Unknown failure type: {kind}")
        if not keys:
            raise ValueError("Select one or more permanent nodes")
        if any(key not in self.nests for key in keys):
            raise ValueError("Cannot fail an unknown node or egg")
        affected: set[str] = set()
        for key in sorted(set(keys)):
            nest = self.nests[key]
            if kind == "communications":
                nest.communications = "disconnected"
                self._lost_since[key] = self.tick
                self._log(f"{key}: communications anomaly; diagnostic investigation")
            else:
                nest.health = kind
                nest.communications = "disconnected"
                if kind == "energy":
                    nest.energy = 0
                affected.add(key)
                self._log(f"{key}: {kind.upper()} FAILURE; emergency recall")
        if affected:
            self._activate_neighbor_eggs(affected)
            for colony in sorted({self.nests[key].colony for key in affected}):
                self.recall(colony)
            for key in affected:
                self.pending_repairs[key] = 0

    def investigate_comms(self, key: str) -> str:
        nest = self.nests[key]
        if nest.communications != "disconnected" or nest.health != "operational":
            return "not-communications-only"
        nearby = [
            other.key for other in self.nests.values()
            if other.key != key and other.health == "operational"
            and other.communications == "online"
            and self.distance(nest, other) <= COMM_RANGE
        ]
        assessment = "neighbors=" + ",".join(nearby) if nearby else "no local neighbors"
        self._log(f"{key}: communications diagnostic: {assessment}")
        return assessment

    def restore(self, key: str) -> None:
        if key not in self.nests:
            raise ValueError(key)
        nest = self.nests[key]
        nest.health = "operational"
        nest.communications = "online"
        nest.energy = max(35.0, nest.energy)
        self.pending_repairs.pop(key, None)
        self._lost_since.pop(key, None)
        self._log(f"{key}: repair commissioned; local service restored")
        for egg in self.eggs.values():
            if egg.left == key or egg.right == key:
                if self.nests[egg.left].health == "operational" and (
                    self.nests[egg.right].health == "operational"
                ):
                    egg.mode = "standby"
                    self._log(f"{egg.key}: micro-nest returned to standby")

    def _safe_destinations(self, colony: str) -> list[tuple[str, Nest | Egg]]:
        destinations: list[tuple[str, Nest | Egg]] = [
            (key, node) for key, node in self.nests.items()
            if node.colony == colony and node.health == "operational"
            and node.energy >= 8 and node.docking_slots > 0
        ]
        destinations += [
            (key, egg) for key, egg in self.eggs.items()
            if egg.colony == colony and egg.mode in ("bridging", "refuge")
            and egg.energy >= 8 and egg.docking_slots > 0
        ]
        return destinations

    def recall(self, colony: str) -> None:
        destinations = self._safe_destinations(colony)
        for bee in self.bees.values():
            if bee.colony != colony or bee.state == "disabled":
                continue
            candidates = [
                (self.distance(bee, obj), key)
                for key, obj in destinations
                if self.distance(bee, obj) * 0.45 + RETURN_RESERVE <= bee.energy
            ]
            if candidates:
                bee.destination = min(candidates)[1]
                bee.state = "returning"
            else:
                bee.state = "sheltering"
                bee.destination = None
        self._log(f"Colony {colony}: recall to viable nest/egg or safe shelter")

    def request_assistance(self, from_colony: str, to_colony: str) -> bool:
        if from_colony == to_colony:
            return False
        if not any(
            self.nests[a].colony == from_colony
            and self.nests[b].colony == to_colony
            or self.nests[b].colony == from_colony
            and self.nests[a].colony == to_colony
            for a, b in self.assistance
        ):
            return False
        self._log(f"{from_colony} → {to_colony}: communication/rescue request ONLY")
        return True

    def queue_repair(self, key: str) -> None:
        if key not in self.pending_repairs:
            raise ValueError("No physical failure to repair")
        nest = self.nests[key]
        retrievers = [
            bee for bee in self.bees.values()
            if bee.colony == nest.colony and bee.role == "handler"
            and bee.mission in ("retriever", "retrieval")
            and bee.energy > RETURN_RESERVE + 15 and bee.state != "disabled"
        ]
        if not retrievers:
            self._log(f"{key}: repair unavailable: no eligible Retriever Handler")
            return
        if not self.operator_online:
            self._log(f"{key}: repair requires operator approval when connected")
            return
        self.pending_repairs[key] = max(1, self.pending_repairs[key])
        self._log(f"{key}: Retriever repair authorized; simulation timer started")

    def _update_energy(self) -> None:
        for node in self.nests.values():
            if node.health in PHYSICAL_FAILURES:
                continue
            if node.level == 0:
                generated = 0.65 if self.solar_available else 0.0
                node.energy = min(node.battery_capacity, node.energy + generated - 0.18)
            else:
                node.energy = max(0.0, node.energy - 0.07)
        # Nominal energy topology follows the construction parent and finite
        # stores; never assert successful energy transfer without a model.
        for node in sorted(self.nests.values(), key=lambda n: n.level):
            if node.level == 0 or not node.parent or node.health in PHYSICAL_FAILURES:
                continue
            source = self.nests[node.parent]
            if source.energy > 35 and node.energy < 75 and source.health == "operational":
                sent = min(0.4, source.energy - 35)
                source.energy -= sent
                node.energy = min(node.battery_capacity, node.energy + sent * TRANSFER_EFFICIENCY)
        for egg in self.eggs.values():
            if egg.mode != "standby":
                egg.energy = max(0.0, egg.energy - 0.10)
                if egg.energy <= 0:
                    egg.mode = "depleted"
                    self._log(f"{egg.key}: micro-nest reserve depleted")

    def _update_bees(self) -> None:
        destinations = {**self.nests, **self.eggs}
        for bee in self.bees.values():
            if bee.state in ("disabled", "sheltering"):
                continue
            if bee.state == "returning" and bee.destination in destinations:
                target = destinations[bee.destination]
                distance = self.distance(bee, target)
                step = min(3.5, distance)
                if distance > 0:
                    bee.x += (target.x - bee.x) * step / distance
                    bee.y += (target.y - bee.y) * step / distance
                bee.energy = max(0, bee.energy - step * 0.45)
                if distance <= 3.5:
                    bee.state = "docked"
                    if isinstance(target, Egg):
                        bee.state = "egg_refuge"
                    bee.recordings_mb = max(0.0, bee.recordings_mb - 0.5)
                continue
            if bee.state in ("docked", "egg_refuge"):
                home_obj = destinations.get(bee.destination or bee.home)
                if home_obj is not None and home_obj.energy > 10:
                    amount = min(0.25, (100.0 - bee.energy), home_obj.energy - 10)
                    if amount > 0:
                        bee.energy += amount * 0.8
                        home_obj.energy -= amount
                continue
            if bee.role != "worker" or bee.state != "surveying":
                continue
            bee.x += self.rng.uniform(-2.0, 2.0)
            bee.y += self.rng.uniform(-2.0, 2.0)
            bee.energy = max(0.0, bee.energy - 0.30)
            bee.recordings_mb += 0.8 if "video" in bee.sensors else 0.45
            if bee.energy <= RETURN_RESERVE:
                self.recall(bee.colony)

    def launch(self) -> None:
        self.validate_architecture()
        self.running = True
        for bee in self.bees.values():
            if bee.role == "worker" and bee.state == "docked":
                bee.state = "surveying"
        self._log("Reconnaissance started: mission-specific Worker payloads active")

    def pause(self) -> None:
        self.running = False
        self._log("Simulation paused")

    def step(self, count: int = 1) -> dict[str, int | float]:
        for _ in range(count):
            if not self.running:
                break
            self.tick += 1
            self._update_energy()
            self._update_bees()
            for key, start in list(self._lost_since.items()):
                if self.tick - start >= self.communication_timeout:
                    self._log(f"{key}: comms timeout; conservative colony recall")
                    self.recall(self.nests[key].colony)
                    del self._lost_since[key]
            for key, stage in list(self.pending_repairs.items()):
                if stage > 0:
                    self.pending_repairs[key] = stage + 1
                    if stage >= 15:
                        self.restore(key)
        return self.metrics()

    def metrics(self) -> dict[str, int | float]:
        return {
            "tick": self.tick,
            "colonies": len({n.colony for n in self.nests.values()}),
            "nodes": len(self.nests),
            "working_nodes": sum(n.health == "operational" for n in self.nests.values()),
            "eggs_staged": sum(e.mode == "standby" for e in self.eggs.values()),
            "eggs_bridging": sum(e.mode == "bridging" for e in self.eggs.values()),
            "drones": len(self.bees),
            "returning": sum(b.state == "returning" for b in self.bees.values()),
            "recorded_mb": round(sum(b.recordings_mb for b in self.bees.values()), 2),
            "links": len(self.communication_links()),
        }
