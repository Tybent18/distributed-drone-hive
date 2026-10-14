"""Cinematic, interactive multi-colony expedition command console.

This is a live 2-D tactical simulator GUI, not the photorealistic concept render.
Uses actual ColonyWeb network state for connections, faults, staffing and telemetry.
Run: python -m drone_hive.colony_web_ui
"""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk

from .colony_web import ColonyWeb, FAILURES

BG = "#06131f"
PANEL = "#0b2333"
EDGE = "#21556d"
CYAN = "#53e0ee"
GOLD = "#f6c75e"
PURPLE = "#d58afe"
RED = "#ff6373"
GREEN = "#4be9aa"
MUTED = "#9fbcc9"
COLORS = {"A": GOLD, "B": CYAN, "C": GREEN, "D": PURPLE, "E": "#faa772"}


class ColonyWebConsole(tk.Tk):
    """Live graph-based mission viewer with real simulation failure injection."""

    def __init__(self) -> None:
        super().__init__()
        self.title("DRONE HIVE // COLONY WEB OPERATIONS")
        self.geometry("1500x875")
        self.minsize(1100, 720)
        self.configure(bg=BG)
        self.model = ColonyWeb(seed=42, colonies=3)
        self.selected = tk.StringVar(value="A:N2")
        self.kind = tk.StringVar(value="hardware")
        self.fail_keys = tk.StringVar(value="A:N2")
        self.colony_sel = tk.StringVar(value="A")
        self.terrain = tk.BooleanVar(value=True)
        self.links = tk.BooleanVar(value=True)
        self.hazards = tk.BooleanVar(value=True)
        self.demo_mode = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="PRE-FLIGHT: select node; inspect colony hierarchy")
        self._layout()
        self.refresh()
        self.after(140, self._loop)

    def _label(self, host: tk.Widget, text: str, *, color: str = CYAN,
               size: int = 10, bold: bool = True) -> tk.Label:
        return tk.Label(host, text=text, bg=host.cget("bg"), fg=color,
                        font=("Arial", size, "bold" if bold else "normal"),
                        anchor="w", justify="left")

    def _button(self, parent: tk.Widget, text: str, command,
                color: str = EDGE) -> tk.Button:
        button = tk.Button(parent, text=text, command=command, bg=color, fg="white",
                           activebackground="#31758a", activeforeground="white",
                           relief="flat", bd=0, font=("Arial", 9, "bold"), padx=7, pady=7)
        return button

    def _layout(self) -> None:
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=12, pady=8)
        self._label(header, "⬡  DRONE HIVE   /   COLONY OPS",
                    color=GOLD, size=21).pack(side="left")
        self._label(
            header, "   FEDERATED EXPLORATION WEB   •   ONE QUEEN / COLONY   •   SIMULATION ONLY",
            color=CYAN, size=10,
        ).pack(side="left", padx=10)

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=10)
        left = tk.Frame(main, bg=PANEL, width=250)
        left.pack(side="left", fill="y", padx=(0, 6))
        left.pack_propagate(False)
        center = tk.Frame(main, bg=BG)
        center.pack(side="left", fill="both", expand=True)
        right = tk.Frame(main, bg=PANEL, width=275)
        right.pack(side="right", fill="y", padx=(6, 0))
        right.pack_propagate(False)

        self._label(left, "COLONY / NODE HIERARCHY", size=11).pack(
            anchor="w", padx=10, pady=(10, 4)
        )
        self.tree = ttk.Treeview(left, show="tree", selectmode="browse")
        self.tree.pack(fill="both", expand=True, padx=7, pady=4)
        self.tree.bind("<<TreeviewSelect>>", self._tree_select)
        self._label(left, "DRONE / SENSOR ROLES", color=GOLD, size=10).pack(
            anchor="w", padx=10, pady=(6, 4)
        )
        role_text = (
            "♛ QUEEN: N1 command / coordination\n"
            "⌁ RELAY: communication continuity\n"
            "↗ RETRIEVER: eggs, rescue, assembly\n"
            "⬡ WORKERS: survey / image / map\n"
            "◎ EGG: bridge micro-nest + refuge\n\n"
            "Cross-colony: assistance ONLY\n"
            "No inter-colony command takeover."
        )
        self._label(left, role_text, color=MUTED, bold=False, size=9).pack(
            anchor="w", padx=10, pady=(0, 9)
        )

        self.map = tk.Canvas(center, bg="#122a34", highlightthickness=1,
                             highlightbackground=EDGE)
        self.map.pack(fill="both", expand=True)
        self.map.bind("<Button-1>", self._map_click)

        self._label(right, "LIVE NODE INSPECTOR", size=11).pack(
            anchor="w", padx=10, pady=(11, 4)
        )
        self.node_picker = ttk.Combobox(right, textvariable=self.selected,
                                        values=list(self.model.nests), state="readonly")
        self.node_picker.pack(fill="x", padx=9)
        self.node_picker.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        self.info = tk.Text(right, bg=PANEL, fg="#d7eff4", height=19, width=32,
                            relief="flat", font=("Consolas", 10), wrap="word")
        self.info.pack(fill="x", padx=9, pady=7)
        self._label(right, "FAILURE INJECTION", color=RED, size=11).pack(
            anchor="w", padx=10, pady=(6, 4)
        )
        self._label(right, "Comma-separated IDs (e.g., A:N2,A:N3)",
                    color=MUTED, size=8, bold=False).pack(anchor="w", padx=10)
        tk.Entry(right, textvariable=self.fail_keys, bg="#173648", fg="white",
                 insertbackground="white", relief="flat").pack(fill="x", padx=9, pady=5)
        ttk.Combobox(right, textvariable=self.kind, values=FAILURES,
                     state="readonly").pack(fill="x", padx=9, pady=3)
        self._button(right, "INJECT ONE / MULTI-NODE FAILURE", self.inject, "#872b43").pack(
            fill="x", padx=9, pady=4
        )
        self._button(right, "DIAGNOSE COMMUNICATION LINK", self.diagnose).pack(
            fill="x", padx=9, pady=3
        )
        self._button(right, "AUTHORIZE RETRIEVER REPAIR", self.repair, "#714781").pack(
            fill="x", padx=9, pady=3
        )
        self._button(right, "RESTORE SELECTED NODE", self.restore, "#235c50").pack(
            fill="x", padx=9, pady=3
        )
        self._button(right, "RECALL SELECTED COLONY", self.recall, "#765320").pack(
            fill="x", padx=9, pady=3
        )
        toggles = tk.Frame(right, bg=PANEL)
        toggles.pack(fill="x", pady=7)
        for text, state in (("Terrain", self.terrain), ("Links", self.links),
                            ("Hazards", self.hazards)):
            tk.Checkbutton(toggles, text=text, variable=state, bg=PANEL, fg="white",
                           selectcolor="#17475b", command=self.refresh).pack(side="left")

        controls = tk.Frame(self, bg=BG)
        controls.pack(fill="x", padx=11, pady=(6, 3))
        self._button(controls, "▶ START EXPLORATION", self.launch, "#127354").pack(
            side="left", padx=3
        )
        self._button(controls, "Ⅱ PAUSE", self.pause).pack(side="left", padx=3)
        self._button(controls, "✦ DEMO: N2 BRIDGE", self.demo_bridge, "#72429c").pack(
            side="left", padx=3
        )
        self._button(controls, "⌁ COMMS FAILURE", self.demo_comms, "#785b25").pack(
            side="left", padx=3
        )
        self._button(controls, "↻ RESET", self.reset).pack(side="left", padx=3)
        self._label(controls, "NODE 0: ENERGY  |  NODE 1: QUEEN + 3 HANDLERS  |  N2+: RELAY + RETRIEVER + WORKERS",
                    color=MUTED, bold=False, size=9).pack(side="right", padx=5)

        bottom = tk.Frame(self, bg=PANEL)
        bottom.pack(fill="x", padx=11, pady=(0, 9))
        left_log = tk.Frame(bottom, bg=PANEL)
        left_log.pack(side="left", fill="both", expand=True, padx=8)
        self._label(left_log, "MISSION EVENTS / TELEMETRY").pack(anchor="w", pady=3)
        self.events_view = tk.Text(left_log, bg="#091a27", fg=CYAN,
                                   height=6, relief="flat", font=("Consolas", 9))
        self.events_view.pack(fill="both", expand=True, pady=(0, 6))
        self.summary = self._label(bottom, "", color=MUTED, bold=False, size=10)
        self.summary.pack(side="right", padx=15)
        self._label(self, "ENGINEERING PROTOTYPE • simulated terrain/range/power; not flight-certified",
                    color=MUTED, size=9, bold=False).pack(anchor="w", padx=14)

        for col in sorted({n.colony for n in self.model.nests.values()}):
            parent = self.tree.insert("", "end", iid=f"COL:{col}", text=f"◈ COLONY {col}", open=True)
            for nest in self.model.nests.values():
                if nest.colony == col:
                    icon = "☀" if nest.level == 0 else "♛" if nest.level == 1 else "⬡"
                    self.tree.insert(parent, "end", iid=nest.key,
                                     text=f"{icon} N{nest.level}  {nest.kind.replace('_', ' ')}")
            for egg in self.model.eggs.values():
                if egg.colony == col:
                    self.tree.insert(parent, "end", iid=egg.key,
                                     text=f"◉ {egg.key.split(':')[1]}  reserve micro-nest")

    def _tree_select(self, _: object) -> None:
        ids = self.tree.selection()
        if ids and ids[0] in self.model.nests:
            self.selected.set(ids[0])
            self.fail_keys.set(ids[0])
            self.refresh()

    def _map_click(self, event: tk.Event) -> None:
        w, h = max(1, self.map.winfo_width()), max(1, self.map.winfo_height())
        mx, my = event.x * 640 / w, event.y * 445 / h
        candidate = min(self.model.nests.values(),
                        key=lambda n: (n.x - mx) ** 2 + (n.y - my) ** 2)
        if math.hypot(candidate.x - mx, candidate.y - my) < 22:
            self.selected.set(candidate.key)
            self.fail_keys.set(candidate.key)
            self.refresh()

    def inject(self) -> None:
        try:
            keys = [part.strip().upper() for part in self.fail_keys.get().split(",")
                    if part.strip()]
            self.model.inject_failure(keys, self.kind.get())
            self.refresh()
        except ValueError as exc:
            self.status.set(str(exc))
            self.model._log(f"INPUT ERROR: {exc}")
            self.refresh()

    def diagnose(self) -> None:
        self.model.investigate_comms(self.selected.get())
        self.refresh()

    def repair(self) -> None:
        try:
            self.model.queue_repair(self.selected.get())
        except ValueError as exc:
            self.model._log(str(exc))
        self.refresh()

    def restore(self) -> None:
        self.model.restore(self.selected.get())
        self.refresh()

    def recall(self) -> None:
        self.model.recall(self.model.nests[self.selected.get()].colony)
        self.refresh()

    def launch(self) -> None:
        self.model.launch()
        self.refresh()

    def pause(self) -> None:
        self.model.pause()
        self.refresh()

    def reset(self) -> None:
        self.model = ColonyWeb(seed=42, colonies=3)
        self.refresh()

    def demo_bridge(self) -> None:
        self.model.inject_failure(["A:N2"], "hardware")
        self.selected.set("A:N2")
        self.refresh()

    def demo_comms(self) -> None:
        self.model.inject_failure(["B:N2"], "communications")
        self.selected.set("B:N2")
        self.refresh()

    def _loop(self) -> None:
        if self.model.running:
            self.model.step()
            self.refresh()
        self.after(150, self._loop)

    def _terrain(self, sx: float, sy: float) -> None:
        c = self.map
        c.create_rectangle(0, 0, 640 * sx, 445 * sy, fill="#172c36", outline="")
        # Deterministic terrain decoration: illustrative, not a survey/site model.
        for i in range(105):
            x = (i * 109 + 31) % 630
            y = (i * 157 + 47) % 430
            radius = 3 + (i % 6)
            c.create_oval((x-radius)*sx, (y-radius)*sy, (x+radius)*sx,
                          (y+radius)*sy, fill=("#31424a" if i % 3 else "#40504a"),
                          outline="")
        for cx, cy, radius in ((268, 208, 41), (323, 276, 48), (455, 104, 35)):
            c.create_oval((cx-radius)*sx, (cy-radius*.58)*sy,
                          (cx+radius)*sx, (cy+radius*.58)*sy,
                          outline="#a28a66", width=3, dash=(7, 5))
            for j in range(11):
                angle = j * math.pi * 2 / 11
                x = cx + radius * math.cos(angle)
                y = cy + radius * .58 * math.sin(angle)
                c.create_rectangle((x-4)*sx, (y-8)*sy, (x+4)*sx,
                                   (y+8)*sy, fill="#8a805f", outline="#d0ad73")
            for dx in (-9, 9):
                c.create_rectangle((cx+dx-3)*sx, (cy-13)*sy, (cx+dx+3)*sx,
                                   (cy+13)*sy, fill="#c1ac7e", outline="#e3c697")

    def refresh(self) -> None:
        m = self.model
        c = self.map
        c.delete("all")
        w, h = max(1, c.winfo_width()), max(1, c.winfo_height())
        sx, sy = w / 640, h / 445
        if self.terrain.get():
            self._terrain(sx, sy)
        else:
            c.configure(bg="#0f2331")
        if self.hazards.get():
            for x1, y1, x2, y2 in m.hazards:
                c.create_rectangle(x1*sx, y1*sy, x2*sx, y2*sy,
                                   fill="#4c2937", outline=RED, width=2, dash=(4, 5))
                c.create_text((x1+x2)/2*sx, (y1+9)*sy,
                              text="! HAZARD", fill=RED, font=("Arial", 10, "bold"))
        for egg in m.eggs.values():
            parent = m.nests[egg.left]
            target = m.nests[egg.right]
            c.create_line(parent.x*sx, parent.y*sy, target.x*sx, target.y*sy,
                          fill="#506a72", width=2, dash=(4, 5))
        if self.links.get():
            for one, two in m.communication_links():
                a = m.nests.get(one) or m.eggs[one]
                b = m.nests.get(two) or m.eggs[two]
                is_cross = a.colony != b.colony
                is_egg = one in m.eggs or two in m.eggs
                color = GOLD if is_cross else PURPLE if is_egg else CYAN
                c.create_line(a.x*sx, a.y*sy, b.x*sx, b.y*sy,
                              fill=color, width=3 if is_egg else 2,
                              dash=(3, 3) if is_cross else ())
        for egg in m.eggs.values():
            x, y = egg.x*sx, egg.y*sy
            active = egg.mode in ("bridging", "refuge")
            color = PURPLE if active else "#8b7aa4"
            c.create_oval(x-9, y-12, x+9, y+12, fill="#422d53",
                          outline=color, width=3 if active else 1)
            c.create_text(x, y+20, fill=color, text=egg.key.split(":")[1],
                          font=("Arial", 9, "bold"))
        selected = self.selected.get()
        for nest in m.nests.values():
            x, y = nest.x*sx, nest.y*sy
            failed = nest.health != "operational"
            selected_here = nest.key == selected
            color = RED if failed else GOLD if nest.level <= 1 else COLORS[nest.colony]
            radius = 13 if nest.level <= 1 else 10
            if selected_here:
                c.create_oval(x-25, y-25, x+25, y+25, outline="white", width=2)
            c.create_oval(x-radius, y-radius, x+radius, y+radius,
                          fill="#112d40" if not failed else "#511d2b",
                          outline=color, width=3)
            c.create_text(x, y, text="⚡" if nest.level == 0
                          else "Q" if nest.level == 1 else str(nest.level),
                          font=("Arial", 11, "bold"), fill=color)
            c.create_text(x, y+radius+12, text=nest.key,
                          font=("Arial", 10, "bold"), fill="white")
            if failed:
                c.create_text(x+17, y-18, text="FAILED", fill=RED,
                              font=("Arial", 9, "bold"))
            elif nest.communications == "disconnected":
                c.create_text(x+18, y-18, text="COMMS?", fill=GOLD,
                              font=("Arial", 9, "bold"))
        # Individual bees are visible in the simulated map near their assigned nest.
        for index, bee in enumerate(m.bees.values()):
            if bee.state == "disabled":
                continue
            dx = (index % 7 - 3) * 3.5
            dy = (index % 5 - 2) * 3.5
            x, y = (bee.x*sx + dx), (bee.y*sy + dy)
            color = GOLD if bee.role == "queen" else PURPLE if (
                bee.role == "handler") else CYAN
            c.create_oval(x-2.4, y-2.4, x+2.4, y+2.4, fill=color, outline="")
        c.create_rectangle(6, 6, 251, 68, fill="#071827", outline=EDGE)
        c.create_text(16, 19, text="GÖBEKLI TEPE–INSPIRED EXPEDITION",
                      anchor="w", fill=GOLD, font=("Arial", 10, "bold"))
        c.create_text(16, 39, text="3 COLONIES  •  REDUNDANT RADIO WEB",
                      anchor="w", fill=CYAN, font=("Arial", 9, "bold"))
        c.create_text(16, 58, text="Physical survey / energy transfer: NOT VALIDATED",
                      anchor="w", fill=MUTED, font=("Arial", 8))
        c.create_text(w-12, h-14,
                      text="● NORMAL LINK     ● EGG BRIDGE     ● CROSS-COLONY ASSIST",
                      anchor="e", fill=CYAN, font=("Arial", 9, "bold"))
        selected_node = m.nests[selected]
        drone_staff = [b for b in m.bees.values() if b.home == selected]
        self.info.config(state="normal")
        self.info.delete("1.0", "end")
        self.info.insert("end", (
            f"{selected_node.key}  {selected_node.kind.upper()}\n"
            f"COLONY {selected_node.colony}  •  LEVEL {selected_node.level}\n"
            f"STATUS: {selected_node.health.upper()}\n"
            f"LINK: {selected_node.communications.upper()}\n"
            f"ENERGY: {selected_node.energy:.1f}% (abstract)\n"
            f"PARENT: {selected_node.parent or 'Root'}\n"
            f"DOCKS: {selected_node.docking_slots}\n\n"
            f"QUEEN: {sum(b.role == 'queen' for b in drone_staff)}\n"
            f"RELAY HANDLER: {sum(b.mission == 'relay' for b in drone_staff)}\n"
            f"RETRIEVER: {sum(b.mission == 'retriever' for b in drone_staff)}\n"
            f"OTHER HANDLERS: "
            f"{sum(b.role == 'handler' and b.mission not in ('relay','retriever') for b in drone_staff)}\n"
            f"WORKERS: {sum(b.role == 'worker' for b in drone_staff)}\n"
            f"MISSIONS: {', '.join(selected_node.workers) or 'Energy operations'}\n\n"
            f"FOLDABLE NEST / MODULAR POWER\n"
            f"LOCAL BUFFER / DOCK / COMMS\n"
            f"RECORDED: {sum(b.recordings_mb for b in drone_staff):.1f} MB\n"
            f"NO INTER-COLONY COMMAND TAKEOVER"
        ))
        self.info.config(state="disabled")
        self.events_view.config(state="normal")
        self.events_view.delete("1.0", "end")
        self.events_view.insert("end", "\n".join(m.events[-6:]))
        self.events_view.config(state="disabled")
        summary = m.metrics()
        self.summary.configure(text=(
            f"TICK {summary['tick']}\n"
            f"NODES {summary['working_nodes']}/{summary['nodes']}\n"
            f"BRIDGE EGGS {summary['eggs_bridging']}\n"
            f"RADIO LINKS {summary['links']}\n"
            f"RECORDING {summary['recorded_mb']} MB"
        ))


def main() -> int:
    ColonyWebConsole().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
