"""Offline licensed backplates. Only the background layer can be replaced."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

from blinkpuzz2.core import require, write_json

from .worlds import WORLDS, set_art


def checksum(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def install(folder, worlds, pack=None):
    records = {}
    pack = Path(pack).resolve() if pack else None
    supplied = json.loads(pack.read_text()) if pack else {}
    require(isinstance(supplied, dict) and set(supplied) <= set(WORLDS), "Unknown scene pack world")
    for world in sorted(set(worlds)):
        rec = supplied.get(world)
        records[world] = {
            "kind": "procedural",
            "artist": "BlinkPuzz",
            "source": "blinkpuzz2/scenes/worlds.py",
        }
        if rec is None:
            continue
        require(
            isinstance(rec, dict)
            and set(rec) == {"file", "artist", "license", "source", "sha256"}
            and all(isinstance(v, str) and v.strip() for v in rec.values()),
            "Incomplete scene credit",
        )
        require(
            rec["license"] in ("original-owned", "CC0-1.0", "CC-BY-4.0"),
            "Unsupported reuse license",
        )
        path = (pack.parent / rec["file"]).resolve()
        require(path.is_relative_to(pack.parent), "Scene file outside pack")
        if not path.is_file():
            records[world]["fallback"] = "Declared image missing"
            continue
        require(checksum(path) == rec["sha256"], "Scene source hash mismatch")
        target = folder / "assets" / (world + ".png")
        target.parent.mkdir(exist_ok=True)
        with Image.open(path) as image:
            require(image.width * image.height <= 32_000_000, "Backplate exceeds 32 megapixels")
            pixels = ImageOps.fit(
                ImageOps.exif_transpose(image).convert("RGB"),
                (1080, 1920),
                Image.Resampling.LANCZOS,
            )
            pixels.info.clear()
            pixels.save(target, compress_level=6)
        records[world] = {
            "kind": "licensed",
            "artist": rec["artist"],
            "license": rec["license"],
            "source": rec["source"],
            "source_sha256": rec["sha256"],
            "backplate_sha256": checksum(target),
        }
    write_json(folder / "assets/credits.json", records)
    return records


def backdrop(folder, records, spec, world):
    rec = records[world]
    if rec["kind"] == "procedural":
        return set_art(WORLDS[world], spec.seed)
    require(
        rec["kind"] == "licensed"
        and rec.get("license") in ("original-owned", "CC0-1.0", "CC-BY-4.0")
        and rec.get("artist")
        and rec.get("source"),
        "Missing backplate provenance",
    )
    path = folder / "assets" / (world + ".png")
    require(checksum(path) == rec["backplate_sha256"], "Packaged backplate changed")
    with Image.open(path) as im:
        require(im.size == (1080, 1920), "Invalid backplate size")
        return im.convert("RGB")
