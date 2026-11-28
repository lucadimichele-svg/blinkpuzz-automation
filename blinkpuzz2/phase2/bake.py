"""Reproducible, content-addressed Cycles beauty passes and rigid moving parts."""

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from blinkpuzz2.core import digest, require, write_json

from .geometry import build_scene, check_camera, check_scene

BACKEND = Path(__file__).with_name("blender_render.py")


def bake(s, cache):
    stage = build_scene(s)
    audit = check_scene(s, stage)
    model = stage.export()
    key = digest([model, hashlib.sha256(BACKEND.read_bytes()).hexdigest()])
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / key
    if not dest.exists():
        with tempfile.TemporaryDirectory(dir=cache) as tmp:
            folder = Path(tmp) / "result"
            folder.mkdir()
            write_json(folder / "model.json", model)
            with (folder / "blender.log").open("w") as log:
                cmd = [
                    "blender",
                    "-b",
                    "-t",
                    "2",
                    "--factory-startup",
                    "--python-exit-code",
                    "1",
                    "--python",
                    str(BACKEND),
                    "--",
                    str(folder / "model.json"),
                    str(folder),
                ]
                done = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
            if done.returncode:
                raise RuntimeError((folder / "blender.log").read_text()[-2200:])
            check_camera(stage, json.loads((folder / "projection.json").read_text()))
            try:
                folder.rename(dest)
            except OSError:
                if not dest.is_dir():
                    raise
    check_camera(stage, json.loads((dest / "projection.json").read_text()))
    require((dest / "stage.png").is_file(), "Incomplete beauty pass")
    return stage, dest, audit


def passes(folder):
    def full(name, mode):
        with Image.open(folder / name) as src:
            return src.convert(mode).resize((1080, 1920), Image.Resampling.LANCZOS)

    beauty = full("stage.png", "RGB")
    marks = json.loads((folder / "sprites.json").read_text())
    sprites = {}
    if marks:
        atlas = full("atlas.png", "RGBA")
        for k, rec in marks.items():
            x, y = rec["atlas"]
            r = rec["radius"]
            tile = atlas.crop((x - r, y - r, x + r + 1, y + r + 1))
            require(tile.getchannel("A").getbbox() is not None, "Invisible moving part")
            sprites[k] = tile
    return beauty, sprites
