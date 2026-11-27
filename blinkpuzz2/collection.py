"""Stage outputs privately, validate delivered bytes, then install the collection."""

import hashlib
import json
import os
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path

from PIL import Image, ImageDraw

from .catalog import ENGINES
from .core import PuzzleSpec, require, validate, write_json
from .planning import Entry, fingerprint, handoff, insights_template, inventory
from .render.media import checked_image, compose, encode, frame_check, probe
from .render.storyboard import Storyboard, storyboard, validate_timeline
from .scenes import assets
from .scenes.drawing import font


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def paths(ordinal, spec):
    stem = f"{ordinal:02d}-{spec.engine}"
    return {
        "video": stem + ".mp4",
        "cover": "covers/" + stem + ".jpg",
        "spec": "specs/" + stem + ".json",
        "proof": "proofs/" + stem + ".json",
        "proof_frame": "proofs/" + stem + ".jpg",
    }


def dhash(path):
    with Image.open(path) as im:
        pixels = im.convert("L").resize((17, 16), Image.Resampling.LANCZOS).tobytes()
    return sum(
        (pixels[y * 17 + x] > pixels[y * 17 + x + 1]) << (y * 16 + x)
        for y in range(16)
        for x in range(16)
    )


def build_item(folder, i, entry, reveal, credits):
    s, w = entry.spec, entry.world
    validate(s, ENGINES)
    story = storyboard(s, reveal)
    validate_timeline(s, story)
    files = paths(i, s)
    s.save(folder / files["spec"])
    write_json(folder / files["proof"], s.proof)
    bg = assets.backdrop(folder, credits, s, w)
    cover, _, seq = compose(s, w, story, bg)
    cover.save(folder / files["cover"], quality=93, subsampling=0)
    if reveal:
        proof = seq[-1][0]
    else:
        _, _, review_seq = compose(s, w, storyboard(s, True), bg)
        proof = review_seq[-1][0]
    proof.save(folder / files["proof_frame"], quality=93, subsampling=0)
    with tempfile.TemporaryDirectory(dir=folder) as temp:
        encode(Path(temp), folder / files["video"], s, w, story, seq)
    return {
        **files,
        "puzzle_id": s.puzzle_id,
        "title": ENGINES[s.engine].title,
        "engine": s.engine,
        "seed": s.seed,
        "world": w,
        "duration": story.duration,
        "storyboard": asdict(story),
        "accessibility_text": s.accessibility_text,
        "sha256": {k: sha(folder / v) for k, v in files.items()},
    }


def sheet(folder, rows, field, path):
    cols = min(5, len(rows))
    tw, th = 216, 384
    sheet = Image.new("RGB", (cols * tw, ((len(rows) + cols - 1) // cols) * (th + 42)), "#21212b")
    d = ImageDraw.Draw(sheet)
    for i, row in enumerate(rows):
        x, y = (i % cols) * tw, (i // cols) * (th + 42)
        with Image.open(folder / row[field]) as im:
            sheet.paste(im.resize((tw, th), Image.Resampling.LANCZOS), (x, y))
        d.text(
            (x + 10, y + th + 8),
            f"{i + 1:02d}   {row['engine'].upper()}",
            font=font("mono", 18),
            fill="#fff2d6",
        )
    sheet.save(path, quality=92)


def check_item(folder, i, row, credits):
    require(row["engine"] in ENGINES, "Unknown indexed engine")
    # Derive the filenames before opening any manifest-supplied path.
    spec_path = f"specs/{i:02d}-{row['engine']}.json"
    s = PuzzleSpec.read(folder / spec_path)
    require(s.engine == row["engine"], "Wrong spec for pilot")
    files = paths(i, s)
    for k, v in files.items():
        require(row[k] == v and row["sha256"][k] == sha(folder / v), "File identity mismatch: " + v)
    validate(s, ENGINES)
    require(
        s.puzzle_id == row["puzzle_id"]
        and s.seed == row["seed"]
        and read(folder / row["proof"]) == s.proof
        and row["title"] == ENGINES[s.engine].title
        and row["accessibility_text"] == s.accessibility_text,
        "Manifest or proof differs from spec",
    )
    story = Storyboard(**row["storyboard"])
    validate_timeline(s, story)
    require(story.duration == row["duration"], "Unexpected timeline length")
    require(row["world"] in ENGINES[s.engine].worlds, "Incompatible scene")
    bg = assets.backdrop(folder, credits, s, row["world"])
    cover, cover_audit, seq = compose(s, row["world"], story, bg)
    checked_image(folder / row["cover"], cover)
    proof = (
        seq[-1][0]
        if story.reveal_seconds
        else compose(s, row["world"], storyboard(s, True), bg)[2][-1][0]
    )
    checked_image(folder / row["proof_frame"], proof)
    media = probe(folder / row["video"], story.duration)
    visual = frame_check(folder / row["video"], seq)
    return s, {
        "puzzle_id": s.puzzle_id,
        "unique_winners": 1,
        "seed": s.seed,
        "engine": s.engine,
        "world": row["world"],
        "duration": story.duration,
        "answer": s.solution,
        "ffprobe": media,
        "decoded_video": visual,
        "layout_by_phase": [cover_audit, *[a for _, a, _ in seq]],
        "timing_reason": story.timing_reason,
    }


def qa(folder, *, verify_saved_report=True):
    folder = Path(folder)
    index = read(folder / "index.json")
    rows = index["pilots"]
    credits = read(folder / "assets/credits.json")
    require(set(credits) == {r["world"] for r in rows}, "Invalid scene credits")
    require(
        len(rows) == index["count"] > 0 and index["mode"] in ("collection", "single"),
        "Incomplete pilot index",
    )
    report, seen, hashes, worlds = [], set(), [], []
    for i, row in enumerate(rows, 1):
        s, check = check_item(folder, i, row, credits)
        key = fingerprint(s)
        h = dhash(folder / row["cover"])
        require(key not in seen, "Duplicate game geometry")
        require(not hashes or min((h ^ q).bit_count() for q in hashes) >= 7, "Near-duplicate cover")
        require(not worlds or worlds[-1] != row["world"], "Adjacent repeated composition")
        seen.add(key)
        hashes.append(h)
        worlds.append(row["world"])
        report.append(check)
    extras = read(folder / "additional_specs.json")
    for obj in extras:
        spec = PuzzleSpec(**obj)
        validate(spec, ENGINES)
        key = fingerprint(spec)
        require(key not in seen, "Duplicate additional instance")
        seen.add(key)
    if index["mode"] == "collection":
        require(len(extras) >= 50, "Missing additional inventory")
        plan, planned_extras, statistics = inventory(
            index["request"]["count"], index["request"]["seed"]
        )
        require(
            [(r["puzzle_id"], r["world"]) for r in rows]
            == [(e.spec.puzzle_id, e.world) for e in plan]
            and extras == [asdict(s) for s in planned_extras]
            and index["generation"] == statistics,
            "Collection does not reproduce its declared generation run",
        )
        if len(rows) >= 20:
            require(
                len(set(worlds)) >= 6
                and all(sum(r["engine"] == e for r in rows) >= 2 for e in ENGINES),
                "Missing benchmark coverage",
            )
    for field, name in (("cover", "contact_sheet.jpg"), ("proof_frame", "proof_sheet.jpg")):
        with tempfile.TemporaryDirectory() as td:
            expected = Path(td) / name
            sheet(folder, rows, field, expected)
            require(sha(folder / name) == sha(expected), "Contact sheet mismatch")
    require(read(folder / "review_handoff.json") == handoff(rows), "Invalid review handoff")
    result = {
        "status": "passed",
        "credits_sha256": sha(folder / "assets/credits.json"),
        "count": len(rows),
        "additional_specs": len(extras),
        "unique_boards": len(seen),
        "world_count": len(set(worlds)),
        "mechanic_count": len({r["engine"] for r in rows}),
        "min_cover_dhash_distance": min(
            ((a ^ b).bit_count() for i, a in enumerate(hashes) for b in hashes[:i]), default=None
        ),
        "pilot_checks": report,
    }
    if verify_saved_report:
        require(
            read(folder / "quality.json") == result,
            "Saved quality report disagrees with verification",
        )
    return result


def archive(folder):
    dest = folder.with_name(folder.name + ".zip")
    with tempfile.NamedTemporaryFile(dir=folder.parent, suffix=".zip", delete=False) as temp:
        staged = Path(temp.name)
    try:
        with zipfile.ZipFile(staged, "w") as z:
            for f in sorted(folder.rglob("*")):
                if f.is_file():
                    compression = (
                        zipfile.ZIP_DEFLATED
                        if f.suffix in (".json", ".csv")
                        else zipfile.ZIP_STORED
                    )
                    z.write(f, str(f.relative_to(folder)), compress_type=compression)
        with zipfile.ZipFile(staged) as z:
            require(z.testzip() is None, "Archive CRC failure")
        os.replace(staged, dest)
    finally:
        staged.unlink(missing_ok=True)


def safe_output(path):
    path = Path(path).resolve()
    root = Path(__file__).resolve().parents[1]
    if path.is_relative_to(root):
        require(path.is_relative_to(root / "build/v2"), "Repository output belongs under build/v2")
    return path


def build(out, count=20, seed=20261127, single=None, world=None, reveal=True, scene_pack=None):
    out = safe_output(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    request = {
        "count": count if single is None else 1,
        "seed": seed if single is None else single.seed,
        "mode": "collection" if single is None else "single",
        "reveal": reveal,
        "single_id": single.puzzle_id if single else None,
        "single_world": world,
        "scene_pack_sha256": sha(scene_pack) if scene_pack else None,
    }
    if out.exists():
        require(
            (out / "index.json").is_file() and read(out / "index.json")["request"] == request,
            "Destination contains a different build",
        )
        result = qa(out)
        if single is None:
            archive(out)
        return result
    if single is None:
        entries, extras, stats = inventory(count, seed)
    else:
        validate(single, ENGINES)
        entries, extras, stats = (
            [Entry(single, world or ENGINES[single.engine].worlds[0], 0)],
            [],
            {},
        )
    with tempfile.TemporaryDirectory(prefix=".blinkpuzz-", dir=out.parent) as td:
        folder = Path(td) / "collection"
        for sub in ("specs", "proofs", "covers"):
            (folder / sub).mkdir(parents=True)
        credits = assets.install(folder, [e.world for e in entries], scene_pack)
        rows = []
        for i, entry in enumerate(entries, 1):
            print(f"Rendering {i}/{len(entries)}  {entry.spec.engine}  {entry.world}", flush=True)
            rows.append(build_item(folder, i, entry, reveal, credits))
        write_json(
            folder / "index.json",
            {
                "schema_version": 1,
                "mode": request["mode"],
                "count": len(rows),
                "request": request,
                "generation": stats,
                "pilots": rows,
            },
        )
        write_json(folder / "additional_specs.json", [asdict(s) for s in extras])
        write_json(folder / "review_handoff.json", handoff(rows))
        insights_template(folder / "insights.csv", [r["puzzle_id"] for r in rows])
        sheet(folder, rows, "cover", folder / "contact_sheet.jpg")
        sheet(folder, rows, "proof_frame", folder / "proof_sheet.jpg")
        print("Verifying delivered media and puzzle proofs", flush=True)
        result = qa(folder, verify_saved_report=False)
        write_json(folder / "quality.json", result)
        folder.rename(out)
    if single is None:
        archive(out)
    return result
