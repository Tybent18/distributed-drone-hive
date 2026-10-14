"""Assemble six genuine WebGL stage captures into independently animated README GIFs."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

INPUT = Path("demos/webgl-frames")
OUTPUT = Path("assets/readme")
SCENARIOS = ("overview", "bridge", "multi", "comms", "energy", "recovery")
for scenario in SCENARIOS:
    frames = []
    signatures = set()
    for step in range(6):
        path = INPUT / f"{scenario}-{step}.png"
        with Image.open(path) as image:
            frame = image.convert("RGB").resize((960, 540), Image.Resampling.LANCZOS)
        signatures.add(frame.tobytes())
        # Full frames, explicit duration; no repeated stills or concept art.
        canvas = frame.quantize(colors=160, method=Image.Quantize.FASTOCTREE)
        frames.append(canvas)
    if len(signatures) != 6:
        raise AssertionError(f"{scenario}: event frames were duplicated")
    target = OUTPUT / f"colony-{scenario}.gif"
    frames[0].save(target, save_all=True, append_images=frames[1:],
                   duration=[1200, 1250, 1300, 1300, 1400, 1700],
                   loop=0, optimize=False, disposal=2)
    with Image.open(target) as check:
        if check.n_frames != 6:
            raise AssertionError(f"{target}: only {check.n_frames} frames")
    print(f"Verified GIF {target}, 6 unique visible stages, {target.stat().st_size} bytes")
