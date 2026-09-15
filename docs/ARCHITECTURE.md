# Architecture

[← Project home](../README.md) · [Methods](METHODS.md) · [Evidence](EVIDENCE.md) · [Roadmap](ROADMAP.md)

The Stage One system separates the research question from any specific hardware stack.

| Layer | Responsibility |
|---|---|
| `config.py` | Declares policies, environment dimensions, energy constraints, seeds, and failure conditions |
| `simulation.py` | Advances drone state, energy fields, mapped area, hive connectivity, deployment, and failure |
| `experiment.py` | Executes the policy × seed × failure matrix and writes immutable evidence bundles |
| `visualization.py` | Produces comparison and trajectory figures from measured output |
| `dashboard.py` | Provides a one-click local operator interface for running and opening evidence bundles |
| `demo.py` | Replays a deterministic adaptive-frontier scenario as a repository GIF |

The carrier is represented by the root hive. Relay reachability is computed from that root at every step, so an isolated hive cannot supply energy merely because it exists. Drone behavior remains decentralized: each agent selects a locally scored direction using unexplored area and energy safety.
