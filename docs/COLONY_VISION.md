# Drone Hive — Original Colony Vision and Evidence Alignment

## Mission
The intended physical system is a distributed colony for exploring dangerous or unstable environments, including collapsed structures, lost cities and fragile archaeological monuments, without requiring humans to enter unsafe terrain. This is a **long-term engineering goal**. Current implementations are abstract 2-D simulators, not demonstrated flight, radio-power transfer, or field-capable robots.

## Entities and operational roles
- Node 0 / carrier: protected root station, operator control, primary communication and proposed energy support.
- Hive nests (Nodes 1…N): local docking, communication relay, autonomous task organization, infrastructure expansion.
- Queens: colony coordination. During operator link loss, attempt to return to Node 0.
- Workers: survey and map non-invasively; return to an assigned nest when link is lost or energy reserve is reached.
- Handlers: emergency infrastructure placement and future recovery/repair roles. Temporary relay substitution is proposed, not yet implemented.
- Eggs: reserve batteries and relay packages placed ahead of time, to be activated/deployed by handlers with explicit operator approval.
- Human operator: oversees mission, approves emergency deployment and exceptional extended-range activity.

## Interactive simulation contract
1. Show animated bees, nests, eggs, communication links, hazards and map coverage.
2. Let the operator assign roles and home nest **before** beginning the simulation.
3. Expose pause, start, simulated failure, emergency approval, and link loss/restore commands.
4. Never auto-approve an egg activation. Dispatch a connected handler and record the result.
5. On loss of operator link, inhibit new deployments; direct Queens to Node 0 and others to nests, then stasis.
6. Display measured successes *and* failures, with comparable control experiments.

## Resource safety
The 30% battery reserve is a proposed operating threshold, **not proof of safe return**. Future implementations must include travel-distance estimation, consumed charge, finite charging/egg capacity, disconnected or damaged nests, inaccessible terrain, and inability to return. The simulator must not suggest that wireless energy, perpetual operation, or autonomy is physically validated.

## Evidence preservation
Keep the September 2026 frozen Stage One dataset, associated files, code, checksums and scientific conclusions **unchanged**. It measured carrier-only, fixed-relay and adaptive-frontier policies in a dimensionless environment, not role-specific recovery. The adaptive frontier result documents a failure mode useful for motivating new work, not evidence that eggs or handlers succeed.

All new results must use separately versioned protocols, paths under data/colony_recovery/runs/, fresh manifests and independently labeled plots. Never silently pool new colony results with Stage One.

## Next experimental sequence
- A. Visual, configurable and deterministic role/contingency prototype.
- B. Repeatable failure injection: node order, failure type and time, handler availability, placement and approval delays.
- C. Recovery policy comparison: no-egg control, strategically pre-placed eggs, operator-approved eggs; report latency, survival, coverage, successful reconnection, and cost.
- D. Resource realism: finite reserves, docking, capacity, charging energy budget, communication availability, and unreachable-home fail-safes.
- E. Hazardous terrain: obstacles, occlusion, unstable regions, collapse, non-invasive mapping, geofencing, and mission abort.
- F. Scaling/physical research: coordination, real sensor design, hardware feasibility, conservation of energy, appropriate regulatory and archaeological permissions, qualified safety review before any field work.

## Branch status
The colony mission engine and Tk desktop console are **initial prototypes** distinct from the established Stage One study. They presently simplify movement, terrain, energy, task planning, physical hazards, networking and fail-safe behavior. They are not a validated emergency recovery system.

Run desktop interactive UI: python -m drone_hive.colony_ui
Run prior frozen experiment UI: python -m drone_hive.dashboard
Run tests: pytest -q
