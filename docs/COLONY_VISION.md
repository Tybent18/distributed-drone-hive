# Drone Hive — Founding Mission and Confirmed Colony Design

## Exploration mission

The objective is **non-invasive reconnaissance of dangerous, collapsed, unstable, or inaccessible terrain**, particularly lost cities, archaeological excavations and ancient monuments. The long-term goal is a coordinated physical fleet, not merely a graph-plotting experiment. The current repo implements an **abstract simulation**, not a real archaeological survey, physical UAV fleet or validated energy system.

## Federated construction web

- **Node 0:** independent energy root for each colony system, with proposed solar production, battery backup, and physically unvalidated wireless power distribution. Multiple independent roots and networks form a **web** with branching construction and lateral links.
- **Node 1:** exactly **one Queen** per independent colony; **three Handlers** capable of delegated command substitution, communication support, assembly, egg recovery and retrieval; Workers assigned by mission. A Queen governs only its own colony.
- **Node 2 onward:** **one dedicated Relay Handler**, **one dedicated Retriever Handler**, and mission-based Scouts/Mapping/Structure Imaging/Environmental Workers. **No other Queens.**
- **Cross-colony cooperation:** communication relay and authorized rescue logistics ONLY. Never control another colony's bees or override its Queen.
- **Hybrid nest assembly:** foldable self-deploying central chassis plus replaceable energy, radio, local control, docking, data and contingency modules, carried and commissioned by Handlers.
- **Contingency eggs:** **temporary micro-nests**, staged at the midpoint between successive permanent stations after the child is operational. They provide finite emergency data relaying, recording buffer, refuge and limited charging. They are not passive batteries.

## Signature failover case

Normal: `N1 — E1 — N2 — E2 — N3`.

After a physical N2 failure, if E1, E2, N1 and N3 have resources and geometrically valid radio links: `N1 ↔ E1 ↔ E2 ↔ N3`. The two midpoint reserve micro-nests **bridge the failed permanent nest** until a Retriever repairs or replaces it. If the eggs cannot interconnect or also fail, this corridor is marked broken. Eggs can later be repositioned when appropriate.

## Failure handling

- Communications-only failure: **investigate first** (telemetry, neighbors, alternative radio) with bounded timeouts and conservative retreat if safety cannot be verified.
- Energy failure, hardware degradation, destruction or impassable terrain: **immediate safety recall** for affected colony drones to assigned nests or the nearest viable operational egg; recharge within finite budgets, retain records and await authorized recovery. Shelter if no safe reachable destination exists.
- Multiple simultaneous failures are supported; a neighboring colony can assist recovery but is never promoted to command.
- Temporary micro-nest safety activation may be preauthorized for lost communication paths; invasive repairs and new expansion remain controlled by operating rules/human authorization.

## Recording and hardware target

Worker specialties: reconnaissance video, 3-D mapping, non-contact monument imaging and environmental monitoring. Retain origin, sensor, calibration, time, position uncertainty and checksums, with local store-and-forward during outages. All equipment remains subject to available mass, flight time, relay bandwidth and energy budgets.

## Scientific boundary

Radio range, charging efficiency, foldable assembly, stability, rescue manipulator, terrain, drones and all current performance numbers are **dimensionless and hypothetical**. The application does **not** yet control drones or ingest video/LiDAR. Do not interpret the frozen 2026-09-15 Stage One baseline as testing this full proposal. New papers need independent evaluations under separately registered experiment IDs.

[Live architecture](ARCHITECTURE.md) · [Failure protocol](FAILURE_RECOVERY.md) · [README](../README.md)
