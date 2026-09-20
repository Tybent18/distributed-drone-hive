# Experimental data catalog

Committed evidence uses immutable dated run directories:

```text
data/<experiment_id>/runs/YYYY-MM-DD_<condition>-vN/
```

| UTC date | Run ID | Experiment | Status | Evidence |
|---|---|---|---|---|
| 2026-09-15 | `2026-09-15_relay-policy-v1` | Carrier, fixed-relay, and adaptive-frontier simulation | Frozen Stage One baseline | [Open run](stage_one_baseline/runs/2026-09-15_relay-policy-v1/) |

Dates come from the generated manifest. New replications, failure models, and physical-validation stages receive new run IDs; existing evidence is never overwritten. Development smoke runs remain under ignored `results/` paths.
