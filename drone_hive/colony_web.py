"""Federated Drone Hive: graph-based physical colony architecture simulation.

Separate from the immutable September 2026 Stage One research experiment.
All lengths, energy, hazards, charging and links are dimensionless abstractions.
No claim of actual RF power transmission, flight or real drone autonomy.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from hashlib import sha256
from math import hypot, isclose
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


@dataclass(frozen=True)
class EnergyEvent:
    """An abstract energy source, sink, or conserved exchange."""

    tick: int
    kind: str
    source: str
    destination: str
    debited: float
    credited: float
    dissipated: float


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


@dataclass(frozen=True)
class SensorRecord:
    """Traceable synthetic observation metadata, NOT a calibrated sensor reading."""

    sensor_id: str
    timestamp: str  # deterministic simulation tick, not wall-clock UTC
    checksum: str  # SHA-256 of synthetic event metadata, not physical sensor bytes
    bee_id: str
    colony: str
    node: str
    task: str
    sensor_type: str
    sequence: int
    x: float
    y: float
    payload_bytes: int
    synthetic: bool = True
    calibrated: bool = False


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
    sensor_records: list[SensorRecord] = field(default_factory=list)


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

    def __init__(
        self, seed: int = 42, colonies: int = 3, *,
        radio_range: float = COMM_RANGE,
        obstacles: tuple[tuple[float, float, float, float], ...] = (),
        layout_jitter: float = 0.0,
        egg_radio: bool = True,
        assistance_radio: bool = True,
    ) -> None:
        if colonies < 1 or colonies > 5:
            raise ValueError("Number of colonies must be between 1 and 5")
        if radio_range <= 0 or layout_jitter < 0:
            raise ValueError("Radio range must be positive and jitter nonnegative")
        self.rng = Random(seed)
        self.seed = seed
        self.tick = 0
        self.running = False
        self.operator_online = True
        self.solar_available = True
        self.radio_range = radio_range
        self.radio_obstacles = obstacles
        self.layout_jitter = layout_jitter
        self.egg_radio = egg_radio
        self.assistance_radio = assistance_radio
        self.energy_ledger: list[EnergyEvent] = []
        self._energy_initial: float = 0.0
        self.nests: dict[str, Nest] = {}
        self.eggs: dict[str, Egg] = {}
        self.bees: dict[str, Bee] = {}
        self.events: list[str] = []
        self.assistance: set[tuple[str, str]] = set()
        self.hazards = ((260, 112, 360, 208), (65, 300, 177, 384))
        self.pending_repairs: dict[str, int] = {}
        self.communication_timeout = 7
        self._lost_since: dict[str, int] = {}
        self.authority_epoch: dict[str, int] = {}
        self.authority_delegates: dict[str, tuple[str, int]] = {}
        self.energy_failure_losses: float = 0.0
        for i in range(colonies):
            self._seed_colony(chr(65 + i), i)
        self._make_assistance_routes()
        self._energy_initial = self.total_stored_energy()
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
            coordinates = (
                position[0] + self.rng.uniform(-self.layout_jitter, self.layout_jitter),
                position[1] + self.rng.uniform(-self.layout_jitter, self.layout_jitter),
            ) if self.layout_jitter else position
            nest = Nest(
                key, colony, level, *coordinates, parent, kind,
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
        number = max(
            (int(bee.key.split("B")[-1]) for bee in self.bees.values()
             if bee.colony == colony),
            default=0,
        ) + 1
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
        node = self.nests[queens[0].home]
        if (queens[0].state == "disabled"
            or node.health != "operational"
            or node.energy <= 0
            or node.communications != "online"):
            raise ValueError(f"Queen unavailable for colony {colony}")
        return queens[0]

    def command_authority(self, colony: str) -> tuple[str, int] | None:
        """Current local command identity and fencing epoch; never a foreign colony."""
        epoch = self.authority_epoch.get(colony, 0)
        try:
            queen = self.queen_for(colony)
            if epoch == 0 or colony not in self.authority_delegates:
                return (queen.key, epoch)
        except ValueError:
            pass
        delegate = self.authority_delegates.get(colony)
        if delegate and delegate[1] == epoch:
            bee = self.bees.get(delegate[0])
            if bee and bee.colony == colony and bee.home == f"{colony}:N1" and (
                bee.role == "handler" and bee.state != "disabled"
            ):
                node = self.nests[bee.home]
                if node.health == "operational" and node.energy > 0:
                    return delegate
        return None

    def authorize_delegate(self, colony: str, handler_key: str) -> tuple[str, int]:
        """Explicit human-authorized local succession; previous epoch is fenced."""
        if not self.operator_online:
            raise PermissionError("Human authorization required")
        candidate = self.bees.get(handler_key)
        if not candidate or candidate.colony != colony or (
            candidate.home != f"{colony}:N1" or candidate.role != "handler"
            or candidate.state == "disabled"
        ):
            raise ValueError("Only an available local Node 1 Handler can be delegated")
        if self.nests[candidate.home].health != "operational":
            raise ValueError("The delegation station is unavailable")
        self.authority_epoch[colony] = self.authority_epoch.get(colony, 0) + 1
        token = (handler_key, self.authority_epoch[colony])
        self.authority_delegates[colony] = token
        self._log(f"Colony {colony}: authorized local Handler {handler_key} "
                  f"for fenced epoch {token[1]}")
        return token

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

    @staticmethod
    def _segment_hits_box(
        x1: float, y1: float, x2: float, y2: float,
        rect: tuple[float, float, float, float],
    ) -> bool:
        """Liang–Barsky line segment / opaque rectangular obstruction test."""
        left, bottom, right, top = rect
        dx, dy = x2 - x1, y2 - y1
        edges = (-dx, dx, -dy, dy)
        limits = (x1 - left, right - x1, y1 - bottom, top - y1)
        u0, u1 = 0.0, 1.0
        for p, q in zip(edges, limits, strict=True):
            if abs(p) < 1e-12:
                if q < 0:
                    return False
            else:
                t = q / p
                if p < 0:
                    u0 = max(u0, t)
                else:
                    u1 = min(u1, t)
                if u0 > u1:
                    return False
        return True

    def radio_reachable(self, a: Nest | Egg, b: Nest | Egg) -> bool:
        """Simplified isotropic geometric LOS, not measured RF propagation."""
        if self.distance(a, b) > self.radio_range:
            return False
        return not any(
            self._segment_hits_box(a.x, a.y, b.x, b.y, box)
            for box in self.radio_obstacles
        )

    def _network_nodes(self) -> dict[str, Nest | Egg]:
        return {
            **{key: node for key, node in self.nests.items()
               if node.health not in PHYSICAL_FAILURES
               and node.communications == "online" and node.energy > 0},
            **{key: egg for key, egg in self.eggs.items()
               if self.egg_radio and egg.mode in ("bridging", "refuge")
               and egg.energy > 0},
        }

    def communication_links(self, include_assistance: bool = True) -> set[tuple[str, str]]:
        """Range/opaque-obstacle-constrained links; foreign authority never passes."""
        active = self._network_nodes()
        ids = sorted(active)
        links: set[tuple[str, str]] = set()
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if active[a].colony != active[b].colony:
                    if not include_assistance or not self.assistance_radio or (
                        (a, b) not in self.assistance
                    ):
                        continue
                if self.radio_reachable(active[a], active[b]):
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
                            and self.radio_reachable(one, two)
                            and self.radio_reachable(active[parent], one)
                            and self.radio_reachable(two, active[child])):
                            return [parent, one.key, two.key, child]
        return []

    def _activate_neighbor_eggs(self, keys: set[str]) -> None:
        for egg in self.eggs.values():
            if egg.left in keys or egg.right in keys:
                if egg.mode == "standby" and egg.energy > 0:
                    egg.mode = "bridging" if self.egg_radio else "refuge"
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
                    self.energy_failure_losses += nest.energy
                    self._energy_event("fault_loss", key, "damaged", nest.energy, 0, nest.energy)
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
            and self.radio_reachable(nest, other)
        ]
        assessment = "neighbors=" + ",".join(nearby) if nearby else "no local neighbors"
        self._log(f"{key}: communications diagnostic: {assessment}")
        return assessment

    def restore(self, key: str) -> None:
        if key not in self.nests:
            raise ValueError(key)
        nest = self.nests[key]
        nest.health = "operational"
        # Physical restoration is not a source of stored battery energy.
        # In particular, a power-failed nest remains dark until charged from
        # a separately accounted supply or replaced with charged modules.
        nest.communications = "online" if nest.energy > 0 else "disconnected"
        self.pending_repairs.pop(key, None)
        self._lost_since.pop(key, None)
        self._log(
            f"{key}: hardware serviced; "
            + ("powered service restored" if nest.energy > 0 else "awaiting finite power")
        )
        for egg in self.eggs.values():
            if egg.left == key or egg.right == key:
                if all(
                    self.nests[end].health == "operational"
                    and self.nests[end].energy > 0
                    for end in (egg.left, egg.right)
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

    def dock_occupancy(self) -> dict[str, int]:
        """Reservations include both arrived drones and those assigned en route."""
        counts: dict[str, int] = {}
        for bee in self.bees.values():
            if bee.state not in ("docked", "egg_refuge", "returning"):
                continue
            key = bee.destination or bee.home
            counts[key] = counts.get(key, 0) + 1
        return counts

    def recall(self, colony: str) -> None:
        """Allocate finite refuge/docking slots without overbooking.

        A stationary drone occupying a viable nest takes one slot. A returning
        drone reserves a slot at dispatch time; other colonies' reservations
        remain in force. Overflow units shelter rather than inventing a pad.
        """
        destinations = dict(self._safe_destinations(colony))
        reserved: dict[str, int] = {key: 0 for key in destinations}
        pending: list[Bee] = []
        for bee in sorted(self.bees.values(), key=lambda item: item.key):
            key = bee.destination or bee.home
            if bee.colony != colony:
                if bee.state in ("docked", "egg_refuge", "returning") and key in reserved:
                    reserved[key] += 1
                continue
            if bee.state == "disabled":
                continue
            if bee.state in ("docked", "egg_refuge") and key in destinations and (
                self.distance(bee, destinations[key]) <= 3.5
            ) and reserved[key] < destinations[key].docking_slots:
                reserved[key] += 1
                continue
            pending.append(bee)

        for bee in sorted(pending, key=lambda item: (item.energy, item.key)):
            choices = [
                (self.distance(bee, obj), key)
                for key, obj in destinations.items()
                if reserved[key] < obj.docking_slots and (
                    self.distance(bee, obj) * 0.45 + RETURN_RESERVE <= bee.energy
                )
            ]
            if choices:
                _, key = min(choices)
                reserved[key] += 1
                bee.destination = key
                bee.state = "returning"
            else:
                bee.destination = None
                bee.state = "sheltering"
        self._log(f"Colony {colony}: reserved viable dock slots; "
                  "overflow units sheltered")

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

    def total_stored_energy(self) -> float:
        return (
            sum(node.energy for node in self.nests.values())
            + sum(egg.energy for egg in self.eggs.values())
            + sum(bee.energy for bee in self.bees.values())
        )

    def _energy_event(
        self, kind: str, source: str, destination: str,
        debited: float, credited: float, dissipated: float = 0,
    ) -> None:
        if min(debited, credited, dissipated) < -1e-9:
            raise AssertionError("Negative energy transfer")
        if kind == "solar":
            if not isclose(debited, 0, abs_tol=1e-9):
                raise AssertionError("Solar is a bounded external input")
        elif not isclose(debited, credited + dissipated, abs_tol=1e-7):
            raise AssertionError("Energy ledger exchange does not balance")
        self.energy_ledger.append(EnergyEvent(
            self.tick, kind, source, destination, debited, credited, dissipated
        ))

    def energy_balance_residual(self) -> float:
        """Storage must equal initial + solar - irreversible losses."""
        generated = sum(e.credited for e in self.energy_ledger if e.kind == "solar")
        losses = sum(e.dissipated for e in self.energy_ledger)
        return self.total_stored_energy() - (self._energy_initial + generated - losses)

    def _update_energy(self) -> None:
        for node in self.nests.values():
            if node.health in PHYSICAL_FAILURES:
                continue
            idle = 0.18 if node.level == 0 else 0.07
            used = min(idle, node.energy)
            node.energy -= used
            self._energy_event("nest_idle", node.key, "heat", used, 0, used)
            if node.level == 0 and self.solar_available:
                generated = min(0.65, node.battery_capacity - node.energy)
                node.energy += generated
                self._energy_event("solar", "sun", node.key, 0, generated)
        # Abstract energy links follow construction parentage. Their existence is
        # NOT a radio link and does not imply practical remote RF charging.
        for node in sorted(self.nests.values(), key=lambda n: n.level):
            if node.level == 0 or not node.parent or node.health in PHYSICAL_FAILURES:
                continue
            source = self.nests[node.parent]
            if source.energy > 35 and node.energy < 75 and source.health == "operational":
                sent = min(0.4, source.energy - 35,
                           (node.battery_capacity - node.energy) / TRANSFER_EFFICIENCY)
                source.energy -= sent
                delivered = sent * TRANSFER_EFFICIENCY
                node.energy += delivered
                self._energy_event(
                    "hypothetical_parent_transfer", source.key, node.key,
                    sent, delivered, sent - delivered
                )
        for egg in self.eggs.values():
            if egg.mode != "standby":
                used = min(0.10, egg.energy)
                egg.energy -= used
                self._energy_event("egg_idle", egg.key, "heat", used, 0, used)
                if egg.energy <= 0 and egg.mode != "depleted":
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
                used = min(bee.energy, step * 0.45)
                bee.energy -= used
                self._energy_event("return_flight", bee.key, "flight", used, 0, used)
                if distance <= 3.5:
                    if isinstance(target, Egg):
                        valid = target.mode in ("bridging", "refuge") and target.energy >= 8
                    else:
                        valid = target.health == "operational" and target.energy >= 8
                    bee.state = ("egg_refuge" if isinstance(target, Egg) else "docked"
                                 ) if valid else "sheltering"
                    if not valid:
                        bee.destination = None
                continue
            if bee.state in ("docked", "egg_refuge"):
                home_obj = destinations.get(bee.destination or bee.home)
                if home_obj is not None and home_obj.energy > 10:
                    amount = min(0.25, (100.0 - bee.energy), home_obj.energy - 10)
                    if amount > 0:
                        received = amount * 0.8
                        bee.energy += received
                        home_obj.energy -= amount
                        self._energy_event(
                            "docked_charge", bee.destination or bee.home, bee.key,
                            amount, received, amount - received
                        )
                continue
            if bee.role != "worker" or bee.state != "surveying":
                continue
            bee.x += self.rng.uniform(-2.0, 2.0)
            bee.y += self.rng.uniform(-2.0, 2.0)
            used = min(0.30, bee.energy)
            bee.energy -= used
            self._energy_event("survey_flight", bee.key, "flight", used, 0, used)
            sensor = next((s for s in bee.sensors if s != "telemetry"), bee.sensors[0])
            size = 800_000 if "video" in bee.sensors else 450_000
            sequence = len(bee.sensor_records) + 1
            x, y = round(bee.x, 5), round(bee.y, 5)
            stamp = f"sim-tick-{self.tick:06d}"
            content = (f"{bee.key}|{bee.home}|{bee.mission}|{sensor}|"
                       f"{sequence}|{stamp}|{x:.5f}|{y:.5f}|{size}")
            bee.sensor_records.append(SensorRecord(
                sensor_id=f"{bee.key}:{sensor}",
                timestamp=stamp,
                checksum=sha256(content.encode("utf-8")).hexdigest(),
                bee_id=bee.key, colony=bee.colony, node=bee.home, task=bee.mission,
                sensor_type=sensor, sequence=sequence, x=x, y=y,
                payload_bytes=size,
            ))
            bee.recordings_mb += size / 1_000_000
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
            "sheltering": sum(b.state == "sheltering" for b in self.bees.values()),
            "sensor_records": sum(len(b.sensor_records) for b in self.bees.values()),
            "energy_failure_losses": round(self.energy_failure_losses, 3),
            "energy_balance_error": round(self.energy_balance_residual(), 8),
            "recorded_mb": round(sum(b.recordings_mb for b in self.bees.values()), 2),
            "links": len(self.communication_links()),
        }
