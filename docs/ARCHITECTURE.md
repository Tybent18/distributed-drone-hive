# Architecture — Federated Drone Hive

![Colony webs and failover bridge](../assets/architecture/colony-web.svg)

## Overview
Drone Hive targets non-invasive exploration of dangerous and unstable terrain, including archaeologically sensitive sites. The present implementation is a **dimensionless 2-D software simulator**, not a physical system.

The network is a **web of independent Node 0-rooted colony systems**, never merely one linear sequence. Every colony has precisely **one Queen at its Node 1**, with **three Node 1 Handlers** responsible for delegated succession, construction, logistics and recovery. Every Node 2+ has **one Relay Handler and one Retriever Handler** plus mission-dependent Workers. There are no downstream Queens. Cross-colony links permit communication and rescue assistance, never command takeover.

## Distinct graphs

1. **Construction graph:** parent stations transport equipment and commission children, with arbitrary branching at each depth.
2. **Communication mesh:** geometric radio links, permitted cross-colony assistance, active micro-nest egg bridging and temporary routing after failures.
3. **Energy graph:** finite solar/backup supply, modules, storage and estimated lossy parent-to-child delivery. Communicating does not imply energy transfer.

## Hybrid modular nest
A foldable chassis carries interchangeable **energy, communications, local computing, docking, data storage, and contingency** modules. Commissioning requires stable placement, viable power and radios, checked docking and human-approved deployment. Each commissioned nest must stage midpoint reserve eggs between itself and its parent before onward expansion. Physical limits (mass, actuator capabilities, route feasibility) remain research questions.

## Drone roles and recording
| Role | Equipment / intent |
|---|---|
| Queen, N1 | local command, task assignment, diagnostics, communications |
| Three N1 Handlers | command succession, N2 construction, rescue and egg service |
| Relay Handler, N2+ | radio/telemetry relay, connectivity diagnosis, degraded operation |
| Retriever Handler, N2+ | carry foldable modules and eggs, retrieval, maintenance and emergency repair |
| Scout Worker | visual/depth reconnaissance of obstacles and candidate routes |
| Mapping Worker | proposed LiDAR/depth, odometry and geometric reconstruction |
| Structure Imaging Worker | calibrated photography and non-contact photogrammetry |
| Environmental Worker | proposed thermal, humidity and temperature observations |

The simulation tracks Worker sensor categories and aggregate *synthetic* recording quantities, not actual HD video, LiDAR or archaeological observations. The intended recording architecture includes source identity, timestamps, pose uncertainty, calibration, local buffering, integrity hashes and synchronization after link restoration.

## Contingency eggs
Eggs are **limited-capacity temporary micro-nests**, prepositioned halfway between adjacent permanent nodes. They support emergency communications, limited energy/docking/refuge, and data buffering. If N2 fails in **N1—E1—N2—E2—N3**, then, **only when links are in range and eggs have resources**, the alternative **N1↔E1↔E2↔N3** can preserve a reduced communications corridor. They do not create Queens, and they cannot replace the full physical capacity of a permanent nest.

## Fault model
Energy, structural hardware, destruction and blocked access trigger immediate affected-colony protective recall to reachable viable nests or activated eggs. Communications-only interruption is investigated before assuming structural damage; bounded timeout triggers failsafe. Multiple simultaneous node faults may overwhelm all available bridges. Restoring a node returns eligible eggs to standby; return/refuge and charge require finite energy. Other colonies provide communication/rescue only.

## Software map
- `colony_web.py`: physical/communications/energy distinctions, colony hierarchy, assigned bee sensors, egg bridge and node outage model.
- `colony_web_ui.py`: live tactical viewport, hierarchy inspector and fault injection.
- `web_demo.py`: model-driven animated demonstration.
- `colony.py` / `colony_ui.py`: previous isolated 2-D single-colony prototype.
- `simulation.py` / `experiment.py`: **frozen Stage One baseline**, not proof that this future architecture works.

## Limits and validation
Radio range, chassis mass, energy-transfer efficiency, docking, sensor bandwidth, motion, repair, rescue and hazards are **hypothetical**, not physically calibrated. Hardware operation would require component characterization, conservatively constrained flight recovery, ecological/cultural heritage permissions and qualified safety review.
