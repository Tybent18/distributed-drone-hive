"""Publication-ready static figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .simulation import SimulationResult

COLORS = {
    "carrier_only": "#64748b",
    "fixed_relay": "#f59e0b",
    "adaptive_frontier": "#22c55e",
}


def plot_comparison(rows: list[dict[str, object]], path: Path) -> None:
    policies = list(COLORS)
    metrics = [("final_coverage", "Mapped fraction"), ("survival_rate", "Survival rate")]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for ax, (metric, title) in zip(axes, metrics, strict=True):
        for failure, offset, hatch in ((0, -0.16, ""), (1, 0.16, "//")):
            label_used = False
            for index, policy in enumerate(policies):
                values = [
                    float(row[metric])
                    for row in rows
                    if row["policy"] == policy and row["failure_scenario"] == failure
                ]
                if not values:
                    continue
                ax.bar(
                    index + offset,
                    np.mean(values),
                    0.3,
                    yerr=np.std(values, ddof=1) if len(values) > 1 else 0,
                    color=COLORS[policy],
                    alpha=1 if not failure else 0.55,
                    hatch=hatch,
                    capsize=3,
                    label=("Nominal" if not failure else "Relay failure")
                    if not label_used
                    else None,
                )
                label_used = True
        ax.set_title(title)
        ax.set_xticks(range(len(policies)), [p.replace("_", "\n") for p in policies])
        ax.grid(axis="y", alpha=0.2)
    axes[0].legend(frameon=False)
    fig.suptitle(
        "Infrastructure policies under nominal and relay-failure conditions", weight="bold"
    )
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)


def plot_trajectories(results: list[SimulationResult], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for result in results:
        if result.config.hive_failure_step is not None:
            continue
        policy = result.config.policy.value
        axes[0].plot(
            [float(row["step"]) for row in result.history],
            [float(row["coverage"]) for row in result.history],
            color=COLORS[policy],
            alpha=0.25,
        )
        axes[1].plot(
            [float(row["step"]) for row in result.history],
            [float(row["active_drones"]) / result.config.drones for row in result.history],
            color=COLORS[policy],
            alpha=0.25,
        )
    axes[0].set(title="Exploration coverage", xlabel="Step", ylabel="Mapped fraction")
    axes[1].set(title="Drone survival", xlabel="Step", ylabel="Active fraction")
    for ax in axes:
        ax.grid(alpha=0.2)
    fig.suptitle("Five-seed Stage One trajectories", weight="bold")
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)


def draw_world(result: SimulationResult, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    ax.imshow(
        result.mapped,
        origin="lower",
        cmap="Blues",
        alpha=0.45,
        extent=(0, result.config.width, 0, result.config.height),
    )
    live = result.active
    ax.scatter(
        result.drone_positions[~live, 0],
        result.drone_positions[~live, 1],
        s=14,
        c="#ef4444",
        marker="x",
        label="Inactive drone",
    )
    ax.scatter(
        result.drone_positions[live, 0],
        result.drone_positions[live, 1],
        s=18,
        c="#38bdf8",
        label="Active drone",
    )
    ax.scatter(
        result.hive_positions[:, 0],
        result.hive_positions[:, 1],
        s=150,
        c="#f59e0b",
        marker="h",
        edgecolors="black",
        label="Hive",
    )
    ax.set(
        xlim=(0, result.config.width),
        ylim=(0, result.config.height),
        title=f"{result.config.policy.value.replace('_', ' ').title()} — final state",
        xlabel="Environment x",
        ylabel="Environment y",
    )
    ax.legend(frameon=False, ncols=3, loc="upper center")
    fig.savefig(path, dpi=160, facecolor="#07111f")
    plt.close(fig)
