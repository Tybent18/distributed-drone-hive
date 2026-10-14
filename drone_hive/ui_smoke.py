"""Headless desktop smoke test + real Tkinter screenshots (run under Xvfb).

These screenshots show the actual executable mission console, not concept artwork.
Usage: xvfb-run -a python -m drone_hive.ui_smoke
"""
from __future__ import annotations

from pathlib import Path

from PIL import ImageGrab

from .colony_web_ui import ColonyWebConsole


def main() -> int:
    output = Path("demos/ui-smoke")
    output.mkdir(parents=True, exist_ok=True)
    ui = ColonyWebConsole()
    try:
        ui.geometry("1500x875+20+20")
        ui.update_idletasks()
        ui.update()
        if not ui.model.validate_architecture() is None:
            raise AssertionError("Invalid colony hierarchy")
        if ui.model.metrics()["colonies"] != 3:
            raise AssertionError("Expected three colonies")
        if ui.map.winfo_width() < 400:
            raise AssertionError("Tactical viewport failed to render")

        def capture(name: str) -> None:
            ui.update_idletasks()
            ui.update()
            x = ui.winfo_rootx()
            y = ui.winfo_rooty()
            width = ui.winfo_width()
            height = ui.winfo_height()
            ImageGrab.grab(bbox=(x, y, x + width, y + height)).save(
                output / name
            )

        capture("01-preflight.png")
        ui.demo_bridge()
        if ui.model.bridge_path("A:N2") != [
            "A:N1", "A:E1", "A:E2", "A:N3"
        ]:
            raise AssertionError("N2 failure did not form midpoint egg bridge")
        capture("02-n2-bridge.png")

        ui.model.inject_failure(["A:N3", "B:N2"], "destroyed")
        if ui.model.nests["A:N3"].health != "destroyed":
            raise AssertionError("Multi-failure injector did not respond")
        capture("03-multiple-failures.png")

        ui.reset()
        ui.demo_comms()
        if ui.model.nests["B:N2"].health != "operational":
            raise AssertionError("Comms issue incorrectly became physical fault")
        capture("04-comms-investigation.png")
        print(f"GUI launched, actions verified, 4 real Tk screenshots saved to {output}")
    finally:
        ui.destroy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
