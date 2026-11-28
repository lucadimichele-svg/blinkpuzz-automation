"""Build, independently inspect and package the development-only creative benchmark."""

import argparse
import csv
import hashlib
import itertools
import json
import os
import shutil
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path

from PIL import Image, ImageDraw

from blinkpuzz2.catalog import ENGINES
from blinkpuzz2.core import digest, require, write_json
from blinkpuzz2.scenes.drawing import font

from .bake import bake
from .experience import FAMILIES, SAFE, collection, signature
from .film import Shot
from .media import render

ROOT = Path("build/v2/phase2")
SHEETS = ("covers", "gameplay", "reveals", "families")
REQUIRED = (
    "reel.mp4",
    "cover.jpg",
    "gameplay.jpg",
    "reveal.jpg",
    "experience.json",
    "proof.json",
    "qa.json",
    "projection.json",
)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def source_hash():
    base = Path(__file__).parent
    return digest({p.name: sha(p) for p in sorted(base.glob("*.py"))})


def episode(spec, cache, version):
    stage, model, geom = bake(spec, cache)
    key = digest([asdict(spec), model.name, version])
    pool = cache / "episodes"
    pool.mkdir(exist_ok=True)
    dest = pool / key
    if dest.is_dir():
        inventory = read(dest / "checksums.json")
        require(all(inventory[f] == sha(dest / f) for f in REQUIRED), "Damaged episode cache")
        return dest
    with tempfile.TemporaryDirectory(dir=pool) as tmp:
        part = Path(tmp) / "episode"
        part.mkdir()
        shot = Shot(spec, stage, model)
        info = render(shot, part)
        x, y, z, w = geom["anchor_bounds"]
        info.update(
            geometry=geom,
            puzzle_id=spec.puzzle_id,
            explanatory_words=len((spec.objective + " " + spec.instruction).split()),
            visible_words_including_labels=sum(
                len(t["text"].split()) for t in info["persistent_type"]
            )
            + int(spec.family == "pipes"),
            anchor_extent_fraction_of_safe_zone=round(
                (z - x) * (w - y) / ((SAFE[2] - SAFE[0]) * (SAFE[3] - SAFE[1])), 3
            ),
            composition_signature=signature(spec),
            rig_tilt_degrees=stage.tilt,
        )
        write_json(part / "qa.json", info)
        write_json(part / "experience.json", asdict(spec))
        write_json(
            part / "proof.json",
            {
                "input": "experience.json / board",
                "family": spec.family,
                "demonstration": spec.demonstration,
                **spec.proof,
            },
        )
        shutil.copyfile(model / "projection.json", part / "projection.json")
        write_json(part / "checksums.json", {f: sha(part / f) for f in REQUIRED})
        try:
            part.rename(dest)
        except OSError:
            if not dest.is_dir():
                raise
    return dest


def sheet(paths, labels, width, cols, path):
    height = round(width * 16 / 9)
    gap = 12
    label_height = 37
    rows = (len(paths) + cols - 1) // cols
    page = Image.new(
        "RGB", (cols * (width + gap) + gap, rows * (height + label_height + gap) + gap), "#15252c"
    )
    draw = ImageDraw.Draw(page)
    for i, (photo, label) in enumerate(zip(paths, labels, strict=True)):
        x = gap + i % cols * (width + gap)
        y = gap + i // cols * (height + label_height + gap)
        with Image.open(photo) as src:
            page.paste(src.resize((width, height), Image.Resampling.LANCZOS), (x, y))
        draw.text((x + 2, y + height + 6), label, font=font("cond", 20), fill="#fff4df")
    page.save(path, quality=89, optimize=True)


def fingerprint(path):
    # 576-bit gradient fingerprint of gameplay only; exclude the headline and watermark.
    with Image.open(path) as im:
        grey = im.crop((65, 505, 950, 1495)).convert("L").resize((25, 24), Image.Resampling.LANCZOS)
        p = list(grey.getdata())
    return sum(
        (p[y * 25 + x] < p[y * 25 + x + 1]) << (24 * y + x) for y in range(24) for x in range(24)
    )


def selector():
    rating = {
        "laser": (3, 3, 2, 3),
        "maze": (3, 2, 3, 3),
        "pipes": (3, 2, 3, 3),
        "gears": (2, 2, 3, 3),
        "circuit": (1, 2, 2, 2),
        "nonogram": (1, 1, 3, 2),
        "lock": (1, 2, 3, 1),
        "balance": (2, 2, 2, 2),
        "routes": (2, 2, 2, 2),
        "pattern": (3, 3, 2, 2),
    }
    return {
        k: {
            "status": "mainstream ready"
            if k in ("laser", "maze")
            else "requires redesign"
            if k in ("gears", "pipes")
            else "niche/parked",
            "entry_space_decoys_payoff": rating[k],
            "question_plus_rule_words": len(" ".join([e.title, *e.rules]).split()),
            "explicit_rules": len(e.rules),
            "simultaneous_fields": list(e.fields),
            "solution_contract": "exactly one",
        }
        for k, e in ENGINES.items()
    }


def build(archive=ROOT / "pilots.zip", cache=Path("build/v2/phase2-cache")):
    pilots, extra = collection()
    version = source_hash()
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=archive.parent) as tmp:
        dest = Path(tmp) / "pilots"
        dest.mkdir()
        folders = []
        entries = []
        hashes = []
        for i, s in enumerate(pilots, 1):
            name = f"{i:02}-{s.family}"
            print(f"Render {name} / seed {s.seed}", flush=True)
            folder = dest / "episodes" / name
            shutil.copytree(episode(s, cache, version), folder)
            folders.append(folder)
            entries.append(
                {
                    "episode": name,
                    "puzzle_id": s.puzzle_id,
                    "family": s.family,
                    "grammar": s.grammar,
                    "mp4": f"episodes/{name}/reel.mp4",
                    "proof": f"episodes/{name}/proof.json",
                }
            )
            hashes.append(fingerprint(folder / "gameplay.jpg"))
        distances = [
            {
                "a": entries[a]["episode"],
                "b": entries[b]["episode"],
                "bits": (hashes[a] ^ hashes[b]).bit_count(),
                "same_family": pilots[a].family == pilots[b].family,
            }
            for a, b in itertools.combinations(range(24), 2)
        ]
        require(min(p["bits"] for p in distances) > 4, "Near-identical gameplay")
        for f in FAMILIES:
            require(
                len({digest(signature(s)) for s in pilots if s.family == f}) == 3,
                "Repeated play structure",
            )
        labels = [e["episode"].replace("-", "  ").upper() for e in entries]
        for group, item in [("covers", "cover"), ("gameplay", "gameplay"), ("reveals", "reveal")]:
            sheet(
                [p / (item + ".jpg") for p in folders],
                labels,
                216,
                6,
                dest / f"contact_sheet_{group}.jpg",
            )
        order = sorted(
            range(24), key=lambda i: (FAMILIES.index(pilots[i].family), pilots[i].edition)
        )
        sheet(
            [folders[i] / "gameplay.jpg" for i in order],
            [labels[i] for i in order],
            216,
            3,
            dest / "contact_sheet_families.jpg",
        )
        write_json(dest / "index.json", entries)
        write_json(dest / "editorial_catalog.json", selector())
        write_json(
            dest / "additional_specs.json",
            {
                "boundary_case_ids": [s.puzzle_id for s in extra[:8]],
                "experiences": [asdict(s) for s in extra],
            },
        )
        reports = [read(p / "qa.json") for p in folders]
        write_json(
            dest / "quality.json",
            {
                "pilots": 24,
                "additional_valid": len(extra),
                "grammars": 8,
                "family_counts": {f: 3 for f in FAMILIES},
                "total_decoded_frames": sum(r["decoded_frames"] for r in reports),
                "worst_frame_mae": max(r["worst_luma_mae"] for r in reports),
                "smallest_critical_feature_at_360px": min(
                    r["geometry"]["feature_at_360px"] for r in reports
                ),
                "min_type_contrast": min(
                    t["contrast"]
                    for r in reports
                    for t in [*r["persistent_type"], *r["cover_type"]]
                ),
                "max_explanatory_words": max(r["explanatory_words"] for r in reports),
                "max_total_visible_words": max(
                    r["visible_words_including_labels"] for r in reports
                ),
                "minimum_perceptual_distance_bits": min(p["bits"] for p in distances),
                "perceptual_comparisons": distances,
                "episode_reports": [e["mp4"].replace("reel.mp4", "qa.json") for e in entries],
            },
        )
        with (dest / "editor_review.csv").open("w", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(
                [
                    "episode",
                    "understood_after_two_seconds",
                    "perceived_difficulty",
                    "reveal_delight",
                    "reviewer_notes",
                ]
            )
            writer.writerows([e["episode"], "UNRATED", "UNRATED", "UNRATED", ""] for e in entries)
        (dest / "REVIEW.txt").write_text(
            "Open contact_sheet_gameplay.jpg, then compare the three boards in each row of contact_sheet_families.jpg. "
            "Watch each reel muted first. After two seconds, state the task. Solve from one still. Replay with sound, "
            "check the demonstration against proof.json, and fill in editor_review.csv.\n"
            "Each episode includes a 1080x1920 H.264/AAC reel, cover, two decoded video stills, public board and independent proof. "
            "Every delivered frame is compared to its pose at 135x240. Geometry audits record a representative distinguishing feature at 360px width. "
            "Those measurements do not establish comprehension or enjoyment.\n"
            "Asset credits: original procedural meshes, materials, motions and synthesized sound in blinkpuzz2/phase2. "
            "DejaVu typefaces from the Debian fonts-dejavu packages, Bitstream Vera/DejaVu license. Fonts are rasterized.\n"
        )
        write_json(
            dest / "manifest.json",
            {
                p.relative_to(dest).as_posix(): sha(p)
                for p in sorted(dest.rglob("*"))
                if p.is_file()
            },
        )
        zipped = Path(tmp) / "release.zip"
        with zipfile.ZipFile(zipped, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3) as out:
            for p in sorted(dest.rglob("*")):
                if p.is_file():
                    out.write(
                        p,
                        p.relative_to(dest),
                        compress_type=zipfile.ZIP_STORED
                        if p.suffix in (".mp4", ".jpg")
                        else zipfile.ZIP_DEFLATED,
                    )
        verify(zipped)
        os.replace(zipped, archive)
    print(f"Verified {archive} ({archive.stat().st_size:,} bytes)", flush=True)


def verify(archive):
    with zipfile.ZipFile(archive) as z:
        names = set(z.namelist())
        require(
            len(names) == len(z.namelist()) and z.testzip() is None,
            "Archive CRC or duplicate names",
        )
        manifest = json.loads(z.read("manifest.json"))
        require(set(manifest) == names - {"manifest.json"}, "Inventory mismatch")
        require(
            all(hashlib.sha256(z.read(k)).hexdigest() == v for k, v in manifest.items()),
            "Archive digest mismatch",
        )
        entries = json.loads(z.read("index.json"))
        require(
            len(entries) == 24 and {e["family"] for e in entries} == set(FAMILIES),
            "Invalid family collection",
        )
        for f in FAMILIES:
            require(sum(e["family"] == f for e in entries) == 3, "Missing episode")
        for e in entries:
            prefix = "episodes/" + e["episode"] + "/"
            require(all(prefix + f in names for f in REQUIRED), "Incomplete episode")
        require(
            all("contact_sheet_" + kind + ".jpg" in names for kind in SHEETS),
            "Missing contact overview",
        )
        require(sum(n.endswith(".mp4") for n in names) == 24, "Wrong MP4 count")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        verify(args.verify)
    else:
        build()


if __name__ == "__main__":
    main()
