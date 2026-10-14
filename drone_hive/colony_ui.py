"""Interactive 2-D colony mission console, with role setup before deployment.

Launch with: python -m drone_hive.colony_ui
Uses only the Python standard library and the isolated colony simulation core.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .colony import ColonyMission


class ColonyConsole(tk.Tk):
    SCALE = 6

    def __init__(self) -> None:
        super().__init__()
        self.title("DRONE HIVE // Expedition Colony Simulator")
        self.geometry("1120x710")
        self.configure(bg="#101722")
        self.mission = ColonyMission()
        self.selected_bee = tk.IntVar(value=0)
        self.role = tk.StringVar(value="worker")
        self.home = tk.IntVar(value=0)
        self.node_failure = tk.IntVar(value=1)
        self.mode = tk.StringVar(value="select")
        self.status = tk.StringVar(value="Configure the colony and launch reconnaissance")
        self.speed = tk.IntVar(value=1)
        self._build()
        self.render()
        self.after(100, self.loop)

    def _build(self) -> None:
        top = tk.Frame(self, bg="#101722")
        top.pack(fill="x", padx=18, pady=(14, 8))
        tk.Label(top, text="DRONE HIVE  /  COLONY OPS", fg="#8de6ff",
                 bg="#101722", font=("Arial", 19, "bold")).pack(anchor="w")
        tk.Label(
            top,
            text="Hazardous terrain reconnaissance • abstract simulation; no physical drone control",
                 fg="#a8b7ce", bg="#101722").pack(anchor="w")

        body = tk.Frame(self, bg="#101722")
        body.pack(fill="both", expand=True, padx=18, pady=8)
        self.canvas = tk.Canvas(body, width=720, height=432, bg="#112435",
                                highlightthickness=1, highlightbackground="#4c667b")
        self.canvas.pack(side="left", anchor="n")
        self.canvas.bind("<Button-1>", self.click_map)
        side = tk.Frame(body, bg="#182536", padx=12, pady=12)
        side.pack(side="left", fill="both", expand=True, padx=(12, 0))

        def heading(text: str) -> None:
            tk.Label(side, text=text, bg="#182536", fg="#8de6ff",
                     font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 3))

        def row(label: str, values: list[str], variable: tk.Variable) -> None:
            frame = tk.Frame(side, bg="#182536")
            frame.pack(fill="x", pady=2)
            tk.Label(frame, text=label, width=10, anchor="w",
                     fg="#d9e2f0", bg="#182536").pack(side="left")
            ttk.Combobox(frame, values=values, textvariable=variable,
                         width=17, state="readonly").pack(side="left")

        heading("ASSIGN DRONE FUNCTIONS")
        row("Bee ID", [str(i) for i in range(len(self.mission.bees))], self.selected_bee)
        row("Role", ["unassigned", "queen", "worker", "handler"], self.role)
        row("Nest", [str(i) for i in range(len(self.mission.hives))], self.home)
        self._button(side, "Assign selected bee", self.assign)
        self._button(side, "Quick assign standard crew", self.quick_assign)

        heading("PLACE INFRASTRUCTURE")
        for label, value in [("Place new hive (click map)", "hive"),
                             ("Place reserve egg (click map)", "egg"),
                             ("Inspect map (click)", "select")]:
            self._button(side, label, lambda v=value: self.mode.set(v))
        tk.Label(side, text="Map click mode: ", fg="#d9e2f0", bg="#182536").pack(anchor="w")
        tk.Label(side, textvariable=self.mode, fg="#fdd67d", bg="#182536").pack(anchor="w")

        heading("MISSION & CONTINGENCY")
        self._button(side, "START MISSION", self.start)
        self._button(side, "PAUSE", self.pause)
        row("Fail node", [str(i) for i in range(len(self.mission.hives))], self.node_failure)
        self._button(side, "Inject relay failure", self.fail_node)
        self._button(side, "AUTHORIZE EMERGENCY EGG", self.authorize)
        self._button(side, "Simulate operator link loss", self.link_loss)
        self._button(side, "Restore operator link", self.link_restore)
        heading("TELEMETRY")
        self.info = tk.Label(side, text="", justify="left", anchor="w",
                             bg="#182536", fg="#d9e2f0", font=("Consolas", 10))
        self.info.pack(fill="x")
        tk.Label(self, textvariable=self.status, fg="#fdd67d", bg="#101722",
                 anchor="w").pack(fill="x", padx=18)
        self.log = tk.Text(self, height=6, bg="#0d1925", fg="#bfd8eb",
                           font=("Consolas", 9))
        self.log.pack(fill="x", padx=18, pady=(4, 15))

    def _button(self, parent: tk.Widget, text: str, command) -> None:
        tk.Button(parent, text=text, command=command, bg="#28455f",
                  fg="white", activebackground="#336882", relief="flat",
                  padx=8, pady=4).pack(fill="x", pady=2)

    def assign(self) -> None:
        try:
            self.mission.assign_role(self.selected_bee.get(), self.role.get(), self.home.get())
        except (ValueError, IndexError) as exc:
            messagebox.showerror("Cannot assign role", str(exc))
        self.render()

    def quick_assign(self) -> None:
        try:
            for bee in self.mission.bees:
                role, home = ("queen", 1) if bee.id == 0 else (
                    ("handler", 0) if bee.id in (1, 2) else ("worker", 1)
                )
                self.mission.assign_role(bee.id, role, home)
        except ValueError as exc:
            messagebox.showerror("Crew setup", str(exc))
        self.render()

    def click_map(self, event) -> None:
        x, y = event.x / self.SCALE, (432 - event.y) / self.SCALE
        if not 0 <= x <= self.mission.width or not 0 <= y <= self.mission.height:
            return
        try:
            if self.mode.get() == "hive":
                node = self.mission.add_hive(x, y)
                self.node_failure.set(node)
                self.home.set(node)
            elif self.mode.get() == "egg":
                self.mission.add_egg(x, y)
            else:
                self.status.set(f"Terrain position x={x:.1f}, y={y:.1f}")
        except ValueError as exc:
            messagebox.showerror("Placement blocked", str(exc))
        self.render()

    def start(self) -> None:
        try:
            self.mission.start()
        except ValueError as exc:
            messagebox.showerror("Launch blocked", str(exc))
        self.render()

    def pause(self) -> None:
        self.mission.pause()
        self.render()

    def fail_node(self) -> None:
        self.mission.fail_hive(self.node_failure.get())
        self.render()

    def authorize(self) -> None:
        if not self.mission.authorize_contingency():
            messagebox.showinfo(
                "Cannot deploy",
                "A pending egg, operator link, and connected handler above reserve are required.",
            )
        self.render()

    def link_loss(self) -> None:
        self.mission.lose_operator_link()
        self.render()

    def link_restore(self) -> None:
        self.mission.restore_operator_link()
        self.render()

    def loop(self) -> None:
        if self.mission.running:
            for _ in range(self.speed.get()):
                self.mission.step()
            self.render()
        self.after(120, self.loop)

    def render(self) -> None:
        m = self.mission
        c = self.canvas
        s = self.SCALE
        c.delete("all")
        c.create_rectangle(0, 0, 720, 432, fill="#142738", outline="")
        for a, b, d, e in m.hazard_zones:
            c.create_rectangle(a*s, (m.height-e)*s, d*s, (m.height-b)*s,
                               fill="#58393d", outline="#bd7468", dash=(5, 3))
        for x, y in m.mapped:
            c.create_rectangle(x*s, (m.height-y)*s, (x+1)*s, (m.height-y-1)*s,
                               fill="#2d6a69", outline="")
        linked = m.connected_ids()
        infra = [(("h", h.id), h) for h in m.hives if h.active] + [
            (("e", e.id), e) for e in m.eggs if e.active]
        for i, (key, obj) in enumerate(infra):
            for other_key, other in infra[:i]:
                if m._distance(obj, other) <= m.relay_range:
                    color = "#7dd3a9" if key in linked and other_key in linked else "#76505b"
                    c.create_line(obj.x*s, (m.height-obj.y)*s,
                                  other.x*s, (m.height-other.y)*s,
                                  fill=color, width=2, dash=(3, 4))
        for h in m.hives:
            x, y = h.x*s, (m.height-h.y)*s
            color = "#eeb56c" if ("h", h.id) in linked else "#ec7474" if h.active else "#6f7781"
            c.create_polygon(x-12, y, x-6, y-10, x+6, y-10,
                             x+12, y, x+6, y+10, x-6, y+10,
                             fill=color, outline="white")
            c.create_text(x, y-19, text=f"NODE {h.id}", fill="white")
        for e in m.eggs:
            x, y = e.x*s, (m.height-e.y)*s
            color = "#8bf3b9" if e.active else "#ffcd75" if e.deploying else "#88a4c4"
            c.create_oval(x-7, y-9, x+7, y+9, fill=color, outline="white")
            c.create_text(x, y+17, text=f"EGG {e.id}", fill="#d7e4ee")
        colors = {"queen": "#f6d06c", "worker": "#86e7ff",
                  "handler": "#c7a5ff", "unassigned": "#8995a6"}
        for bee in m.bees:
            x, y = bee.x*s, (m.height-bee.y)*s
            color = "#707783" if bee.state == "inactive" else colors[bee.role]
            c.create_oval(x-4, y-4, x+4, y+4, fill=color, outline="")
            if bee.role == "queen":
                c.create_text(x, y-12, text="Q", fill="#f6d06c")
        t = m.metrics()
        self.info.config(text=(
            f"TICK {t['tick']}   MAPPED {t['mapped_cells']} cells\n"
            f"HIVES {t['connected_hives']}/{t['active_hives']} connected\n"
            f"EGGS {t['active_eggs']} active  APPROVAL {t['pending_approval']}\n"
            f"QUEENS {t['queens']}  WORKERS {t['workers']}  HANDLERS {t['handlers']}\n"
            f"DISABLED {t['disabled_bees']}  LINK {'ONLINE' if m.operator_connected else 'LOST'}"
        ))
        self.log.delete("1.0", "end")
        self.log.insert("end", "\n".join(m.events[-6:]))
        if m.pending_egg is not None:
            self.status.set(f"Authorization needed for emergency egg {m.pending_egg}")
        elif not m.operator_connected:
            self.status.set("LINK LOST — returning agents to nests")
        elif m.running:
            self.status.set("Reconnaissance active — role-based mission")
        else:
            self.status.set("Mission paused / configuration mode")


def main() -> int:
    ColonyConsole().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
