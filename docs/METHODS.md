# Stage One methods

[← Project home](../README.md) · [Architecture](ARCHITECTURE.md) · [Evidence](EVIDENCE.md) · [Safety](SAFETY.md)

Stage One is a deterministic, two-dimensional computational abstraction. It evaluates whether persistent energy infrastructure changes exploration and survivability relative to a single carrier-linked source.

## Conditions

| Policy | Operational definition |
|---|---|
| Carrier only | One root hive; no relay deployment |
| Fixed relay | New hives are placed along a precomputed centerline at fixed intervals |
| Adaptive frontier | New hives follow the active swarm frontier while respecting relay range |

Each policy is evaluated under nominal operation and a single-relay failure at the midpoint. The default matrix uses five independent seeds, 24 drones, and 240 time steps.

## Energy abstraction

A connected hive contributes a radial field proportional to `exp(-(distance / radius)^2)`. A drone receives the strongest connected field contribution, pays idle and movement costs, and becomes inactive when stored energy reaches zero. This model is deliberately dimensionless. It does not estimate antenna gain, frequency-specific path loss, rectenna conversion, thermal load, or flight aerodynamics.

## Outcomes

- mapped environment fraction;
- active-drone survival rate;
- mean remaining energy;
- exploration depth;
- deployed hive count;
- root-connected hive fraction;
- degradation after a relay failure.
