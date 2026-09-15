"""One-click desktop dashboard for experiments and evidence export."""

from __future__ import annotations

import queue
import threading
from datetime import datetime, timezone
from pathlib import Path
from tkinter import BOTH, END, LEFT, Button, Entry, Frame, Label, StringVar, Text, Tk, X, messagebox

from .experiment import run_suite


class HiveLab(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Drone Hive Systems — Stage One Laboratory")
        self.geometry("920x600")
        self.configure(bg="#07111f")
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.running = False
        self.latest_output: Path | None = None

        Label(
            self, text="DRONE HIVE SYSTEMS", font=("Arial", 22, "bold"), fg="#67e8f9", bg="#07111f"
        ).pack(anchor="w", padx=28, pady=(25, 2))
        Label(
            self,
            text="Infrastructure-driven swarm robotics • simulation-only Stage One",
            font=("Arial", 11),
            fg="#94a3b8",
            bg="#07111f",
        ).pack(anchor="w", padx=29, pady=(0, 20))

        controls = Frame(self, bg="#0f1c2e", padx=18, pady=16)
        controls.pack(fill=X, padx=28)
        self.seeds = StringVar(value="7,21,42,84,101")
        self.steps = StringVar(value="240")
        self.drones = StringVar(value="24")
        for label, variable in (
            ("Seeds", self.seeds),
            ("Steps", self.steps),
            ("Drones", self.drones),
        ):
            Label(controls, text=label, fg="#cbd5e1", bg="#0f1c2e").pack(side=LEFT, padx=(0, 6))
            Entry(
                controls,
                textvariable=variable,
                width=15,
                bg="#14243a",
                fg="white",
                insertbackground="white",
                relief="flat",
            ).pack(side=LEFT, padx=(0, 16), ipady=5)
        self.run_button = Button(
            controls,
            text="RUN + EXPORT",
            command=self.start,
            bg="#22c55e",
            fg="#04110a",
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=7,
        )
        self.run_button.pack(side=LEFT)
        Button(
            controls,
            text="OPEN RESULTS",
            command=self.open_results,
            bg="#1e3a5f",
            fg="white",
            relief="flat",
            padx=14,
            pady=7,
        ).pack(side=LEFT, padx=10)

        self.status = Label(
            self, text="Ready", anchor="w", fg="#67e8f9", bg="#07111f", font=("Arial", 11, "bold")
        )
        self.status.pack(fill=X, padx=28, pady=(22, 8))
        self.log = Text(
            self,
            bg="#091728",
            fg="#cbd5e1",
            insertbackground="white",
            relief="flat",
            font=("Courier", 10),
            padx=14,
            pady=14,
        )
        self.log.pack(fill=BOTH, expand=True, padx=28, pady=(0, 26))
        self.log.insert(
            END, "Ready to compare carrier-only, fixed-relay, and adaptive-frontier policies.\n"
        )
        self.after(100, self.poll)

    def start(self) -> None:
        if self.running:
            return
        try:
            seeds = tuple(int(item.strip()) for item in self.seeds.get().split(",") if item.strip())
            steps, drones = int(self.steps.get()), int(self.drones.get())
        except ValueError:
            messagebox.showerror("Invalid settings", "Seeds, steps, and drones must be integers.")
            return
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.latest_output = Path("results/runs") / stamp
        self.running = True
        self.run_button.configure(state="disabled")
        self.log.delete("1.0", END)
        threading.Thread(target=self._run, args=(seeds, steps, drones), daemon=True).start()

    def _run(self, seeds: tuple[int, ...], steps: int, drones: int) -> None:
        try:
            run_suite(
                self.latest_output,
                seeds=seeds,
                steps=steps,
                drones=drones,
                progress=lambda done, total, label: self.events.put(
                    ("progress", (done, total, label))
                ),
            )
            self.events.put(("done", self.latest_output))
        except Exception as exc:  # pragma: no cover - UI boundary
            self.events.put(("error", str(exc)))

    def poll(self) -> None:
        while not self.events.empty():
            kind, payload = self.events.get()
            if kind == "progress":
                done, total, label = payload
                self.status.configure(text=f"Running {done}/{total} — {label}")
                self.log.insert(END, f"[{done / total:6.1%}] {label}\n")
                self.log.see(END)
            elif kind == "done":
                self.running = False
                self.run_button.configure(state="normal")
                self.status.configure(text=f"Evidence exported: {payload}")
                self.log.insert(END, "\nComplete. CSV data, manifest, and charts are ready.\n")
            else:
                self.running = False
                self.run_button.configure(state="normal")
                self.status.configure(text="Run failed")
                messagebox.showerror("Experiment failed", str(payload))
        self.after(100, self.poll)

    def open_results(self) -> None:
        if not self.latest_output or not self.latest_output.exists():
            messagebox.showinfo("No results yet", "Run an experiment first.")
            return
        import os
        import subprocess
        import sys

        if sys.platform == "win32":
            os.startfile(self.latest_output)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", self.latest_output], check=False)
        else:
            subprocess.run(["xdg-open", self.latest_output], check=False)


def main() -> int:
    HiveLab().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
