"""Command-line experiment runner."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from .experiment import run_suite


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument("--output", type=Path)
    command.add_argument("--seeds", default="7,21,42,84,101")
    command.add_argument("--steps", type=int, default=240)
    command.add_argument("--drones", type=int, default=24)
    command.add_argument("--quick", action="store_true")
    return command


def main() -> int:
    args = parser().parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output or Path("results/runs") / stamp
    seeds = (7, 42) if args.quick else tuple(int(seed) for seed in args.seeds.split(","))
    steps = min(args.steps, 80) if args.quick else args.steps

    def progress(done: int, total: int, label: str) -> None:
        print(f"[{done / total:6.1%}] {label}")

    run_suite(output, seeds=seeds, steps=steps, drones=args.drones, progress=progress)
    print(f"\nEvidence bundle written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
