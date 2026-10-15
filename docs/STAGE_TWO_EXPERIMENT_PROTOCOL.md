# Stage Two Research Protocol — Federated Colony Operations

**Status:** preregistration / engineering-readiness protocol, not a completed experiment.
**Supersedes for new experiments:** Stage One's infrastructure-only research questions; **does not overwrite or invalidate** the immutable September 15, 2026 Stage One records.
**Evidence location (only after model verification):** \`data/colony_recovery/runs/<dated_run_id>/\`.

## 1. The question we are actually trying to answer

Can independent, Node 0-rooted, Queen-led drone colonies **expand, gather traceable non-contact survey data, protect drones when infrastructure fails, and restore connectivity using finite, physically positioned contingency micro-nests**—more effectively than credible simpler alternatives, without relying on impossible power, infinite capacity, or unauthorized command transfers?

Our target architecture, not just a relay chain:

- Each colony has its own **N0 energy root**; **one N1 Queen and precisely three N1 Handlers**; every commissioned N2+ nest needs one dedicated **Relay Handler** and one **Retriever Handler**, plus mission-dependent survey Workers.
- **Construction parent graph**, **communications mesh**, **energy/power transfer graph**, and **authorized logistics routes** are different networks. Successful radio delivery never proves electrical power delivery.
- Eggs are finite, physical **temporary micro-nests at the midpoint of adjacent commissioned permanent nests**, offering conditional communications bridging, limited refuge, charging, and buffering. With N2 disabled, \`N1-E1-E2-N3\` is a **hypothesis**, not an assured outcome.
- Structural / energy / docking / blocked-access failures trigger conservative, colony-scoped recall to truly reachable and available refuges. A comms-only loss triggers bounded investigation before retreat. Foreign colonies may assist communication and rescue but cannot assume command.
- Data claims must distinguish **generated observations** from **delivered, uniquely attributable, calibrated and verified observations**, with explicit gaps and losses.

## 2. Pre-experiment engineering validation (must pass first)

Existing \`tests/test_colony_web.py\` validates a narrow selection of happy-path cases. Before we publish a comparative effectiveness claim, require automated properties below under randomized states. The three actively **xfail**-marked regression tests in \`tests/test_research_readiness.py\` document defects until fixed.

| Gate | Mandatory property | Why it matters |
|---|---|---|
| R0-A: identity | Exactly one live authorized N1 Queen, three N1 Handlers, relay/retriever staffing; fenced temporary succession (no split brain) | Proves colony authority hierarchy |
| R0-B: energy | Energy source/sink ledger (solar, storage, charging, transfer loss, flight and failed modules). No magical repair energy; reserves never negative | Stage One's radial power field is not a physical charging claim |
| R0-C: refuge | Assign **unique dock slots** and available reserve energy atomically; drones unable to return safely land/shelter; no occupancy overflow | Current recall chooses destinations without reserving a dock |
| R0-D: comms | Valid range/LoS/interference, capacity and active power; no path over broken/unauthorized segments; eggs are not full-power hives | Connectivity must be demonstrated, not drawn |
| R0-E: construction | Geofenced site survey, physical movement, finite payload mass and module inventory, staged assembly, commissioning, explicit parent, failure during assembly | A hive cannot appear for free |
| R0-F: mission evidence | Unique source/drone/sensor ID, UTC capture time, task/node, pose uncertainty and sensor calibration, hashes, local buffer, later sync, duplicate and lost packets | Synthetic MB counters are not survey datasets |
| R0-G: reproducibility | A seed + identical config + fault schedule + software commit reproduces the same event sequence and output hashes | Supports research integrity |
| R0-H: scenario parity | React/Three.js demo scripts either replay serialized \`ColonyWeb\` traces or are clearly separated as scripted visualizations | Animated GIFs cannot be used as experimental evidence |
| R0-I: human control | Authorized repair and expansion; no cross-colony Queen takeover; audit log; conservative behavior when N1 and its delegates are lost | Ensures autonomy stays within specified boundaries |

**Known implementation shortcuts from source audit, not new experimental results:**

- \`colony_web.py\` sets \`COMM_RANGE = 90\` independent of LOS/interference/bandwidth and connects any same-colony active points inside range. Hazard rectangles are illustrative, not RF obstacles.
- \`recall\` checks \`docking_slots > 0\` but does **not reserve/decrement slots** when multiple drones select a refuge.
- \`restore\` raises node energy to at least 35 abstract units without modeled material/energy sourcing. The 70% nominal parent transfer efficiency is explicitly hypothetical.
- \`queue_repair\` advances a repair timer without an actual Retriever voyage, replacement modules consumed, cargo/energy budget, or commissioning survey.
- The Python model tracks only synthetic recording counters. The React frontend is a **separate scripted timeline**, not a live simulation viewer. Current metrics have no calibrated map coverage, delivered data integrity, end-to-end communications, actual mission cost, or confidence intervals.
- The current architecture produces a preconfigured, mostly fixed graph; it does not yet test feasible construction of **new** branched nodes under finite inventories.

Fix these before computing research-grade effectiveness metrics. A property test may remain a documented \`xfail\`, but a comparative research release must record it as **not ready**, not simply count a green CI run as validation.

## 3. Controlled comparison: baseline policies (same environment & failures)

All trials must match initial drone count, payloads, energy budget, terrain, radio parameters, time horizon, mission difficulty, and random seed. Count egg and replacement hardware cost; otherwise the best supplied architecture trivially wins.

| Arm | Infrastructure architecture | Scientific role |
|---|---|---|
| C0 | N0/N1 colony with no expansions or eggs | Low-cost baseline |
| C1 | Permanent expansion hives with single-parent chain, no reserve eggs | Conventional extension baseline |
| C2 | Permanent **branched web with redundant radio links**, no eggs | Measures value of topology by itself |
| C3 | Branched web + reserve eggs staged **at N0 / depot** | Controls for same extra equipment without midpoint placement |
| C4 | Branched web + midpoint eggs used as **replacement/logistics-only** pods | Controls for egg location without radio bridge |
| C5 | Branched web + **midpoint relay/refuge micro-nests** (proposed) | Tests distinctive egg-bridge hypothesis |
| C6 | C5 plus authorized **cross-colony assistance**, no command takeover | Tests federation benefit separately |

**Do not report superiority until C0–C6 are actually implemented.** Stage One's \`carrier_only\`, \`fixed_relay\`, and \`adaptive_frontier\` are informative *historical* references using a different model; do not directly pool their effect sizes with this new simulation.

## 4. Test suites, prioritized

### P0 — Fault tolerance, safety, energy (first experiment)

Paired healthy and faulted conditions for a fixed, commissioned 3-colony map, including single N2 outage and two failures in the same colony, N0 energy loss, blocked docking pads, zero solar, low/empty egg reserves, egg-to-egg radio isolation, degraded RF, and simultaneous failures across colonies. Run **comms-only** silence separately from physical destruction.

Metrics: **fraction of active drones that return to a safe viable refuge** (including refuge slot assignment), stranded/unsafe rate, achieved communications reachability before/during/after fault, detection and isolation delay, fractional mission downtime, egg activation energy and burn rate, recharge/queue delays, actual repair latency, and unserved rescue requests.

### P1 — Engineering of colony construction and expansion

Evaluate safe root-to-N1 commissioning, finite modular chassis/component inventory, carrier payload and multiple trips, expansion N2+, tree vs branching web, placement with obstacles, egg staging at exact physical midpoints, geofence/terrain rejection, construction interrupted midway, and failure of the transporting Retriever.

Metrics: commissioned hives per 100 normalized work/energy units, unsuccessful placement rate, time to commission, equipment consumption, redundancy created, successful return of construction crews, and onward service radius. Count the initial N0 root and the cost of each egg.

### P2 — Mission data and specialization

Matched terrain seeds with scouts, mappers, structure-imaging workers and environmental workers under restricted weight/compute/bandwidth; optionally mix tasks. Provide a synthetic ground-truth map distinct from worker observations. Inject sensor dropouts, pose/calibration noise, communications outages and buffer saturation.

Metrics: **verified unique environment coverage** rather than distance traveled, obstacle false negatives, reconstruction error vs ground truth, quality-adjusted structure documentation, capture-to-delivery latency, provenance completeness, lost/duplicated bytes, bandwidth use, and energy per useful observation. No claims about actual archaeology until instruments are calibrated.

### P3 — Federation, scalability and malicious or ambiguous failures

Increase colonies (1–5 in current code, then extend), nests, eggs, drone load and concurrent emergencies; test Queen unavailable, acting-Queen delegation and fencing, compromised/spoofed commands, delayed partitions, rescue across colony boundaries, return-to-base under lost authority, and computational performance under network partitions.

Metrics: unauthorized-command count **must be zero**, split-brain events **must be zero**, bounded incident response, rescued drones, communication fairness, throughput vs network load, control-message volume, and time/memory complexity.

### P4 — Physically calibrated research (not enabled by Stage Two simulation alone)

Replace abstract energy/radio assumptions with sourced battery Wh, hover W, payload mass, efficiency, charging rate, LoS/path-loss and actual station construction budgets. Compare local solar, docked conductive charging, battery swaps, cable/power links, and **wireless RF transfer as an explicitly unproven exploratory condition**. Hardware-in-loop and site-licensed operations require separate review. Never imply equipment will operate at an archaeological site without permission.

## 5. Study design and acceptance rules

1. **Engineering gates first**, and log every failing invariant; publish no favorable nominal-only figures as comparative outcomes.
2. Develop using ~**10 deterministic debugging seeds**, then select **at least 30 paired evaluation seeds** not used to tune algorithms. This is an initial design choice; enlarge sample size using pilot variance/power analysis and correct for multiple comparisons as needed.
3. Use predeclared variation blocks: radio distance/attenuation, solar availability, egg energy/dock count, workload, mission size, topology, obstacle severity, failure type/severity/timing. Full factorial sweeps can be too large; staged designs and sensitivity analysis are acceptable if preregistered.
4. Keep exogenous random factors paired across arms: **common terrain, initial drones, task assignments, failure schedule and seeds**. Faults must sometimes be unrecoverable. Unsuccessful trajectories remain in all summaries.
5. Report **median + interquartile range**, and **95% bootstrap confidence intervals of per-seed paired differences** for key performance outcomes; show per-seed results, not just averages or a hero GIF.
6. Primary endpoints (preregister): **safe-refuge success** and **verified task coverage under failure**. Secondary: communication uptime, verified-data delivery, energy/cost, recovery latency. Include equipment and dock capacities in normalization.
7. Include an **ablation**: C5 minus egg refuge, minus egg relay, minus redundant links, minus cross-colony support. It reveals which features drive improvement.
8. Parameter uncertainty must be explicit: dimensionless experiments establish behavior **within the model only**. Physical feasibility is a later, separately calibrated stage.

## 6. Reproducible evidence contract

Each completed run receives a new immutable ID. Minimum bundle:

\`\`\`text
data/colony_recovery/runs/<run-id>/
  manifest.json          # schema, code commit, seed list, config, units, constraints
  run_summary.csv        # one row per policy × seed × scenario
  step_metrics.csv       # state changes, energy, docks, links, safe drones over time
  failures.csv           # actual fault events, detection and safety response
  drone_events.csv       # validated missions, destinations, refueling, safe-land
  node_events.csv        # commissioning, energy transfers, egg activation/repair
  sensor_records.csv     # provenance + hashes (synthetic source clearly flagged)
  aggregate_summary.csv  # intervals/effect sizes, including failed runs
  validation.json        # invariant outcomes, warnings, unsupported claims
  plots/                 # survival, delivered data, downtime, cost, failure curves
  REPORT.md              # design, outcomes, limitations, no unsupported physics claims
\`\`\`

A smoke run in ignored \`results/\` is **not** publishable evidence. Never overwrite \`data/stage_one_baseline/\`; it is the original audit trail. Record whether the evidence came from **Python**, **scripted frontend**, or **hardware** (only Python simulation should power Stage Two numerical claims).

## 7. Publication and document replacement gate

Only after (1) gates pass, (2) the preregistered suite runs, and (3) result quality is reviewed:

- Rewrite the current-facing \`README.md\` with a visual summary and links to newly **verified** Stage Two experiments and demonstrations.
- Replace outdated content in \`docs/ARCHITECTURE.md\`, \`docs/FAILURE_RECOVERY.md\`, \`docs/METHODS.md\`, \`docs/EVIDENCE.md\`, \`docs/ROADMAP.md\`, and \`docs/SAFETY.md\` to match what is actually implemented and tested.
- Create \`docs/STAGE_TWO_RESULTS.md\`, \`docs/POWER_AND_RF_ASSUMPTIONS.md\`, \`docs/SENSOR_PROVENANCE.md\` and \`docs/DEPLOYMENT_VALIDATION.md\` where supported.
- Keep \`docs/COLONY_VISION.md\` as design intent with a clear **vision vs implementation vs validated evidence** ledger.
- Preserve immutable \`data/stage_one_baseline\` bundles and their original \`RUN.md\`. Update navigation and mark earlier methods/results as **historical**, not false or deleted.

**Gate to start now:** R0-B energy ledger, R0-C physical refuge capacity, R0-D realistic connectivity, and an exportable fault-trace mechanism. These prevent the most misleading early results.
