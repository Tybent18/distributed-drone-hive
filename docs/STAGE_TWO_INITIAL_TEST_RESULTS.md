# Stage Two: Initial Engineering Smoke Results

**Status:** diagnostic-only simulation evidence; **not** comparative research findings or hardware validation.

## Verified GitHub Actions execution

- [Successful CI run — Python 3.10 and 3.12](https://github.com/Tybent18/distributed-drone-hive/actions/runs/38652332223)
- **34 tests passed** on the Python 3.10 job. The complete CI matrix passed on both Python versions.
- `ruff check .` passed.
- `python -m drone_hive.stage_two_smoke --output results/stage-two-diagnostic` completed for **10 deterministic seeds × 7 scenarios × 3 observation phases = 210 metric rows**.
- Both Python jobs uploaded a separate `stage-two-diagnostic-py3.10` / `stage-two-diagnostic-py3.12` artifact containing `scenario_metrics.csv` and `manifest.json`. These results are retained as CI artifacts, not permanently committed immutable evidence.

## Seven diagnostic scenarios

1. Nominal three-colony baseline.
2. One A:N2 hardware failure.
3. A:N2 and B:N2 destruction.
4. A:N2 communications-only anomaly.
5. A:N0 root energy failure.
6. A:N3 blocked access.
7. A:N2 failure with depleted E1/E2 reserves.

The matrix records per-run radio links, whether A:N2 had a verified egg bridge, functioning nests, returning/sheltering/egg-refuge counts, booked docking slots, synthetic sensor record count, stored abstract energy, and energy lost in energy faults, at pre-fault, post-fault, and end phases.

## Engineering changes in this iteration

- Recall now reserves finite berth capacity at dispatch and tracks both occupied and reserved locations.
- Repair no longer replenishes unaccounted battery charge. An energy-faulted node may be structurally recommissioned but remains communication-offline when unpowered.
- `queen_for` rejects disabled/unavailable Queens; explicit N1 Handler succession uses per-colony fencing epochs and requires operator presence. This is a software policy abstraction, not authenticated, network-partition-resistant consensus.
- Synthetic Worker observations now have source/drone ID, simulated tick, sensor type, task, position, sequence, byte count and a SHA-256 metadata checksum. **They are not calibrated readings, live video, physical data bytes or georeferenced surveys.**

## What this run does NOT establish

- There is no C0–C6 matched treatment comparison yet and thus **no estimated benefit of eggs or federation**.
- The procedural simulator uses fixed maps, crude geometric radio range without terrain propagation, hypothetical power transfer, timer-based Retriever repair without real cargo missions, and no calibrated mapping ground truth.
- Its synthetic observation checksums cover deterministic event metadata, not measured sensor payload bytes. Its docking algorithm handles reservation counts, but does not model dynamic charging queues and landing clearance.
- Ten deterministic debugging seeds are not sufficient for statistical generalization; the planned separate held-out evaluation set is at least 30 paired seeds plus a pilot precision assessment.
- The scripted Three.js README visualizations are illustration, not evidence from this matrix.

## Next gates before a new full dataset replaces current-facing reports

1. Full energy ledger with sources/sinks and battery replacement materials, plus actual charging capacity and time.
2. Radio LOS/interference/bandwidth graph and demonstrably conditional E1↔E2 bridging.
3. Time-stepped construction/repair journeys with Retrievers, materials and terrain/geofence limits.
4. Ground-truth synthetic mission maps and verified delivered sensor records.
5. Implement and test the seven matched study arms in [the preregistered protocol](STAGE_TWO_EXPERIMENT_PROTOCOL.md), then create a **new immutable `data/colony_recovery/runs/` evidence bundle**.

Do **not** overwrite the September 2026 Stage One dataset or use this smoke run to claim superiority over the historical infrastructure policies. The current-facing README and old evidence narratives should be replaced only when the Stage Two comparison is completed and reviewed.
