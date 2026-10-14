"""Generate a real model-driven animated visual demo (not a mock screenshot).

Run: python -m drone_hive.web_demo
The frames are generated from the same ColonyWeb implementation as the GUI.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from .colony_web import ColonyWeb

BACKGROUND = "#071824"
COLORS = {"A": "#f6c75e", "B": "#52dbed", "C": "#42db9c"}


def generate(path: Path = Path("demos/colony-web-operational.gif")) -> Path:
    model = ColonyWeb(seed=42, colonies=3)
    steps = []
    for frame in range(68):
        if frame == 15:
            model.inject_failure(["A:N2"], "hardware")
        if frame == 35:
            model.queue_repair("A:N2")
        if frame == 50:
            model.restore("A:N2")
        if frame == 56:
            model.inject_failure(["B:N2"], "communications")
        if frame == 0:
            model.launch()
        model.step()
        steps.append({
            "tick": model.tick,
            "nests": [
                (n.key, n.colony, n.level, n.x, n.y, n.health, n.communications)
                for n in model.nests.values()
            ],
            "eggs": [(e.key, e.x, e.y, e.mode) for e in model.eggs.values()],
            "links": [
                (a, b, "assistance" if model._network_nodes()[a].colony
                 != model._network_nodes()[b].colony else "bridge" if
                 a in model.eggs or b in model.eggs else "radio")
                for a, b in sorted(model.communication_links())
            ],
            "positions": {
                **{k: (n.x, n.y) for k, n in model.nests.items()},
                **{k: (e.x, e.y) for k, e in model.eggs.items()},
            },
            "events": model.events[-4:],
            "metrics": model.metrics(),
        })

    fig, ax = plt.subplots(figsize=(13, 7.4), facecolor=BACKGROUND)
    fig.subplots_adjust(left=.04, right=.96, top=.90, bottom=.15)

    def draw(index: int):
        step = steps[index]
        ax.clear()
        ax.set_facecolor("#19303a")
        ax.set_xlim(20, 615)
        ax.set_ylim(418, 20)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal", adjustable="box")
        for x, y, radius in ((268, 208, 39), (323, 276, 47), (455, 104, 35)):
            ax.add_patch(plt.Circle((x, y), radius, fill=False,
                                    linewidth=3, color="#8e7963", alpha=.8))
            for i in range(10):
                from math import sin, cos, pi
                xp = x + radius * cos(i * 2 * pi / 10)
                yp = y + radius * sin(i * 2 * pi / 10)
                ax.add_patch(plt.Rectangle((xp-3, yp-6), 6, 12,
                                           color="#b49a6d", alpha=.85))
        for a, b, kind in step["links"]:
            x1, y1 = step["positions"][a]
            x2, y2 = step["positions"][b]
            color = ("#d58afe" if kind == "bridge" else
                     "#f6c75e" if kind == "assistance" else "#52dbed")
            ax.plot((x1, x2), (y1, y2), color=color, linewidth=2.4,
                    alpha=.9, linestyle="--" if kind == "assistance" else "-")
        for key, colony, level, x, y, health, communications in step["nests"]:
            color = "#ff6373" if health != "operational" else (
                "#f6c75e" if level <= 1 else COLORS[colony])
            marker = "X" if health != "operational" else (
                "h" if level <= 1 else "o"
            )
            ax.scatter((x,), (y,), s=240 if level <= 1 else 170,
                       marker=marker, c=color, edgecolors="white",
                       linewidths=.8, zorder=5)
            name = key.split(":")[1]
            ax.text(x, y - 19, f"{colony}:{name}", ha="center", color="white",
                    fontsize=9, fontweight="bold")
            if communications == "disconnected" and health == "operational":
                ax.text(x, y+21, "COMMS?", ha="center", color="#f6c75e", fontsize=7)
        for key, x, y, mode in step["eggs"]:
            color = "#d58afe" if mode == "bridging" else "#797487"
            ax.scatter((x,), (y,), s=190, c=color, marker="d",
                       edgecolors="white", linewidths=.8, zorder=7)
            ax.text(x, y + 20, key, color=color, ha="center", fontsize=8)
        ax.set_title(
            "DRONE HIVE  /  FEDERATED COLONY OPS   •   SIMULATOR",
            color="#f6c75e", loc="left", fontsize=19, fontweight="bold", pad=20,
        )
        phase = ("EXPLORATION" if index < 15 else "PHYSICAL NODE FAILURE" if index < 35
                 else "RETRIEVER REPAIR" if index < 50 else "NODE RESTORED" if index < 56
                 else "COMMS DIAGNOSTICS")
        fig.text(.07, .895, f"PHASE: {phase}    |    TICK {step['tick']}",
                 color="#53e0ee", fontsize=11)
        metrics = step["metrics"]
        fig.text(
            .06, .05,
            f"NODES {metrics['working_nodes']}/{metrics['nodes']}    "
            f"MICRO-NEST BRIDGES {metrics['eggs_bridging']}    "
            f"RADIO LINKS {metrics['links']}    "
            f"DRONES {metrics['drones']}    "
            f"RECORDING {metrics['recorded_mb']} MB",
            color="white", fontsize=11,
        )
        return ()

    animation = FuncAnimation(fig, draw, frames=len(steps), interval=120, blit=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    animation.save(path, writer=PillowWriter(fps=8), dpi=80)
    plt.close(fig)
    return path


def main() -> int:
    print(generate())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
