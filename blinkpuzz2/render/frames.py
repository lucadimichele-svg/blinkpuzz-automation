import itertools

from PIL import Image

from blinkpuzz2.catalog import ENGINES
from blinkpuzz2.core import require
from blinkpuzz2.scenes.architecture import cabinet, folio, ruin_maze
from blinkpuzz2.scenes.drawing import Surface, font
from blinkpuzz2.scenes.games import DIAGRAMS, H, W
from blinkpuzz2.scenes.worlds import WORLDS, plate, set_art

# Layout order and title treatment differ by set. Native gameplay pixels stay fixed.
ALIGN = {
    "lab": "left",
    "desk": "left",
    "ruins": "center",
    "arcade": "center",
    "workshop": "left",
    "editorial": "left",
}


def split_title(title, face, max_width):
    words = title.split()
    # Prefer balanced lines even with short titles, leaving generous negative space.
    options = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
    return min(options, key=lambda pair: max(font(face, 80).getlength(line) for line in pair))


def title_block(s, w, title, cy, cover):
    if w.name in ("editorial", "desk"):
        x, z = 54, 976
    elif w.name == "workshop":
        x, z = 65, 934
    else:
        x, z = 75, 984
    height = 110 if cover else 107
    if w.name == "editorial":
        s.d.rectangle((x - 14, cy - height, z + 25, cy + height), fill=w.paper)
        s.d.line((x + 30, cy - height + 7, z - 23, cy - height + 7), fill=w.ink, width=7)
    elif w.name == "desk":
        s.d.polygon(
            [(x, cy - height), (z, cy - height + 7), (z - 8, cy + height), (x, cy + height - 6)],
            fill=w.paper,
        )
    else:
        plate(s.d, w, (x, cy - height, z, cy + height), "title")
    left = ALIGN[w.name] == "left"
    for i, line in enumerate(split_title(title, w.face, z - x - 92)):
        s.text(
            x + 42 if left else (x + z) // 2,
            cy - 46 + i * 87,
            line,
            84 if cover else 80,
            w.face,
            anchor="lm" if left else "mm",
            maxw=z - x - 90,
            minimum=49,
        )


def fit_lines(text, face, size, width):
    words = text.split()
    lines = [""]
    for word in words:
        candidate = (lines[-1] + " " + word).strip()
        if lines[-1] and font(face, size).getlength(candidate) > width:
            lines.append(word)
        else:
            lines[-1] = candidate
    return lines


def scene(spec, world, background, phase="solve", progress=0):
    e, w = ENGINES[spec.engine], WORLDS[world]
    require(world in e.worlds, "Incompatible scene")
    cover, reveal = phase == "cover", phase == "proof"
    require(
        phase in ("cover", "solve", "proof") and (0 < progress <= 1 if reveal else progress == 0),
        "Invalid frame phase",
    )
    im = background.copy()
    s = Surface(im, w.ink, w.paper, w.accent)
    if world == "arcade":
        cabinet(s.d, w, cover)
    elif world == "desk":
        folio(s.d, w)
    elif world == "editorial":
        s.d.rectangle((55, 273, 984, 1620), fill=w.paper)
        s.d.line((79, 326, 949, 326), fill=w.ink, width=8)
    # Cast identity as an instrument strip, a bookplate, a cabinet marquee or a byline.
    sx = {"desk": 95, "workshop": 188, "ruins": 196, "editorial": 65, "lab": 95, "arcade": 155}[
        world
    ]
    bx = {"desk": 684, "workshop": 783, "ruins": 866, "editorial": 654, "lab": 834, "arcade": 909}[
        world
    ]
    plate(s.d, w, (sx, 138, bx, 220), "mark")
    s.text(
        (sx + bx) // 2,
        179,
        "BLINKPUZZ   /   " + w.series,
        32,
        "mono",
        maxw=bx - sx - 50,
        minimum=26,
    )
    by, ty = w.board_y, w.title_y
    if cover:
        by, ty = {
            "lab": (736, 558),
            "ruins": (498, 1308),
            "desk": (760, 571),
            "workshop": (489, 1274),
            "editorial": (446, 1248),
            "arcade": (698, 553),
        }[world]
    title_block(s, w, e.title, ty, cover)
    payload = Image.new("RGB", (W, H), w.paper)
    game = Surface(payload, w.ink, w.paper, w.accent)
    diagram = ruin_maze if world == "ruins" and spec.engine == "maze" else DIAGRAMS[spec.engine]
    diagram(game, spec.board, spec.proof["witness"], spec.solution, progress)
    bx = {"ruins": 107, "editorial": 76, "workshop": 92, "desk": 104, "arcade": 108, "lab": 96}[
        world
    ]
    plate(s.d, w, (bx - 22, by - 18, bx + W + 22, by + H + 18), "board")
    im.paste(payload, (bx, by))
    for rec in game.records:
        a, b, c, d = rec["box"]
        s.records.append({**rec, "box": [a + bx, b + by, c + bx, d + by]})
    if not cover:
        cy = w.rules_y
        if reveal:
            lines = fit_lines(spec.proof["reason"], "bold", 38, 800)
            lines = [f"Solution   /   {spec.solution}", *lines]
        else:
            lines = spec.rules
        plate(s.d, w, (70, cy - 81, 982, cy + 81), "rule")
        for i, line in enumerate(lines):
            yy = cy + (i - (len(lines) - 1) / 2) * 46
            s.text(
                526,
                yy,
                line,
                39 if not reveal else 38,
                "bold" if (i == 0 or not reveal) else "sans",
                color=w.accent if reveal and i == 0 else w.ink,
                maxw=829,
                minimum=31,
            )
    else:
        # A cover uses a crop-safe poster composition and a separate edition imprint.
        yy = 1530
        plate(s.d, w, (220, yy - 37, 857, yy + 37), "mark")
        s.text(
            538, yy, w.series + "   •   " + spec.engine.upper(), 31, "mono", maxw=576, minimum=26
        )

    half_title = 110 if cover else 107
    regions = {
        "objective": [54, ty - half_title, 984, ty + half_title],
        "board": [bx - 22, by - 18, bx + W + 22, by + H + 18],
    }
    if not cover:
        regions["rules"] = [70, w.rules_y - 81, 982, w.rules_y + 81]
    ordered = sorted(regions.values(), key=lambda box: box[1])
    require(
        all(a[3] < z[1] for a, z in itertools.pairwise(ordered)), "Overlapping gameplay surfaces"
    )
    require(
        all(0 <= x < z <= 1080 and 0 <= y < b <= 1920 for x, y, z, b in ordered), "Clipped surface"
    )
    # Verify separation after translating board labels into the full frame.
    for i, a in enumerate(s.records):
        x, y, z, b = a["box"]
        for prev in s.records[:i]:
            xx, yy, zz, bb = prev["box"]
            require(
                min(z, zz) <= max(x, xx) or min(b, bb) <= max(y, yy), "Composited text collision"
            )
    return im, {
        "phase": phase,
        "board": [bx, by, bx + W, by + H],
        "labels": s.records,
        "regions": regions,
        "min_contrast": min(r["contrast"] for r in s.records),
        "min_type_px": min(r["px"] for r in s.records),
        "clipped": 0,
        "text_collisions": 0,
    }


def background(spec, world):
    return set_art(WORLDS[world], spec.seed)
