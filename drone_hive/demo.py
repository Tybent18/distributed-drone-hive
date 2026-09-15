"""Generate a deterministic repository demo GIF."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

from .config import DeploymentPolicy, SimulationConfig
from .simulation import HiveSimulation


def generate(path: Path = Path("demos/drone-hive-stage-one.gif")) -> Path:
    cfg = SimulationConfig(policy=DeploymentPolicy.ADAPTIVE_FRONTIER, seed=42, steps=180, drones=28)
    sim = HiveSimulation(cfg)
    snapshots = []
    for step in range(cfg.steps):
        sim.step(step)
        if step % 6 == 0 or step == cfg.steps - 1:
            snapshots.append(
                (
                    step,
                    sim.positions.copy(),
                    sim.active.copy(),
                    np.asarray(sim.hives).copy(),
                    sim.mapped.copy(),
                )
            )

    fig, ax = plt.subplots(figsize=(9.6, 5.6), facecolor="#07111f")
    ax.set_facecolor("#07111f")

    def frame(i: int):
        ax.clear()
        step, positions, active, hives, mapped = snapshots[i]
        ax.set_facecolor("#07111f")
        ax.imshow(
            mapped, origin="lower", cmap="Blues", alpha=0.35, extent=(0, cfg.width, 0, cfg.height)
        )
        for hive in hives:
            circle = plt.Circle(hive, cfg.energy_radius, fill=False, color="#22c55e", alpha=0.18)
            ax.add_patch(circle)
        if len(hives) > 1:
            ax.plot(hives[:, 0], hives[:, 1], color="#f59e0b", linewidth=1.2, alpha=0.7)
        ax.scatter(positions[active, 0], positions[active, 1], s=18, c="#67e8f9", edgecolors="none")
        ax.scatter(
            hives[:, 0],
            hives[:, 1],
            s=150,
            c="#f59e0b",
            marker="h",
            edgecolors="white",
            linewidths=0.7,
        )
        ax.set(
            xlim=(0, cfg.width),
            ylim=(0, cfg.height),
            xlabel="Environment x",
            ylabel="Environment y",
        )
        ax.set_title(
            f"ADAPTIVE FRONTIER • STEP {step:03d} • HIVE NODES {len(hives)}",
            color="white",
            weight="bold",
        )
        ax.tick_params(colors="#94a3b8")
        for spine in ax.spines.values():
            spine.set_color("#334155")
        return ()

    animation = FuncAnimation(fig, frame, frames=len(snapshots), interval=110, blit=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    animation.save(path, writer=PillowWriter(fps=9), dpi=90)
    plt.close(fig)
    return path


def main() -> int:
    print(generate())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
