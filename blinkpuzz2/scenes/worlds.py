"""Original procedural set pieces. Gameplay surfaces are flat and optically isolated."""

import math
import random
from dataclasses import dataclass

from PIL import Image, ImageDraw

from .drawing import cog, mix


@dataclass(frozen=True)
class World:
    name: str
    series: str
    base: str
    shadow: str
    paper: str
    ink: str
    accent: str
    face: str
    board_y: int
    title_y: int
    rules_y: int


WORLDS = {
    "lab": World(
        "lab",
        "OPTICS LAB",
        "#203b47",
        "#051622",
        "#102e38",
        "#e1f7e8",
        "#ffb85e",
        "mono",
        652,
        369,
        1450,
    ),
    "ruins": World(
        "ruins",
        "THE TIDAL ARCHIVE",
        "#a6c5c2",
        "#345f68",
        "#f3e5c4",
        "#173d43",
        "#903a21",
        "display",
        491,
        1320,
        300,
    ),
    "desk": World(
        "desk",
        "BUREAU OF EVIDENCE",
        "#78503f",
        "#382731",
        "#fff1d4",
        "#382635",
        "#91352d",
        "serif",
        787,
        359,
        615,
    ),
    "workshop": World(
        "workshop",
        "THE BRASS WORKS",
        "#30655c",
        "#102e30",
        "#193d3c",
        "#fff0c6",
        "#f7bb73",
        "cond",
        621,
        352,
        1430,
    ),
    "editorial": World(
        "editorial",
        "FORM STUDIES",
        "#ffb79e",
        "#cb745f",
        "#fff2d6",
        "#241d2d",
        "#943722",
        "display",
        420,
        1230,
        1510,
    ),
    "arcade": World(
        "arcade",
        "POCKET ARCADE",
        "#8d5596",
        "#35204e",
        "#402555",
        "#fff1bf",
        "#98f5cf",
        "cond",
        669,
        380,
        1442,
    ),
}


def iso(d, x, y, w, h, fill):
    top = [(x, y - w * 0.42), (x + w, y), (x, y + w * 0.42), (x - w, y)]
    d.polygon(top, fill=fill)
    d.polygon(
        [top[1], top[2], (x, y + w * 0.42 + h), (x + w, y + h)], fill=mix(fill, "#183b46", 0.45)
    )
    d.polygon(
        [top[2], top[3], (x - w, y + h), (x, y + w * 0.42 + h)], fill=mix(fill, "#183b46", 0.24)
    )
    d.line(top + [top[0]], fill=mix(fill, "#f7ebca", 0.5), width=2)


def set_art(w, seed):
    rng = random.Random(seed)
    im = Image.new("RGB", (1080, 1920))
    d = ImageDraw.Draw(im)
    for y in range(1920):
        d.line((0, y, 1080, y), fill=mix(w.base, w.shadow, 0.18 + 0.65 * (y / 1920) ** 1.5))
    if w.name == "lab":
        for x in (40, 850):
            for y in (88, 1680):
                d.rounded_rectangle(
                    (x - 90, y, x + 200, y + 196), 36, fill="#16313c", outline="#75978e", width=3
                )
                for j in range(8):
                    d.line(
                        (x - 48, y + 22 + j * 21, x + 158, y + 22 + j * 21), fill="#081b26", width=7
                    )
        for r in range(78, 500, 35):
            d.ellipse((540 - r, -75 - r, 540 + r, -75 + r), outline="#507880", width=3)
        for x in (30, 63, 1000, 1031):
            d.line((x, 60, x, 1860), fill="#61838a", width=4)
        for i in range(24):
            x = 140 + i * 35
            d.line((x, 1755, x, 1740 - (i % 4) * 8), fill="#b6c9ad", width=3)
    elif w.name == "ruins":
        for row in range(12):
            for col in range(-1, 9):
                x = col * 165 + (row % 2) * 82
                y = row * 196 + (col % 3) * 28
                iso(
                    d,
                    x,
                    y,
                    93,
                    rng.randint(28, 80),
                    rng.choice(["#9baea1", "#afbaa3", "#c5c3a3", "#97a9a0"]),
                )
        for x, y in [(120, 1750), (895, 225), (720, 1800)]:
            for i in range(7):
                iso(d, x + i * 12, y - i * 23, 82 - i * 5, 29, "#dbc69f")
    elif w.name == "desk":
        for i in range(95):
            y = rng.randrange(1920)
            pts = [(x, y + 6 * math.sin(x / 110 + i)) for x in range(0, 1120, 25)]
            d.line(pts, fill=mix(w.base, w.shadow, rng.random()), width=rng.randint(1, 3))
        for x, y in [(25, 106), (850, 1590), (88, 1530)]:
            d.polygon(
                [(x, y + 70), (x + 210, y), (x + 300, y + 220), (x + 70, y + 260)],
                fill="#b99b76",
                outline="#2d2224",
            )
            for j in range(6):
                d.line((x + 55, y + 96 + j * 18, x + 205, y + 48 + j * 18), fill="#7e6651", width=2)
        d.line([(38, 98), (940, 220), (993, 1774), (135, 1690)], fill="#b74437", width=6)
        for x, y in [(38, 98), (940, 220), (993, 1774), (135, 1690)]:
            d.ellipse((x - 12, y - 12, x + 12, y + 12), fill="#cd9568", outline="#301d22", width=4)
        d.ellipse((45, 1630, 282, 1867), outline="#241f28", width=24)
        d.ellipse((53, 1638, 274, 1859), outline="#ceaa70", width=6)
        d.line((235, 1832, 340, 1937), fill="#29212c", width=32)
    elif w.name == "workshop":
        for x in range(0, 1080, 42):
            d.line((x, 0, x, 1920), fill="#365955")
        for y in range(0, 1920, 42):
            d.line((0, y, 1080, y), fill="#365955")
        for x, y, r in [(95, 160, 168), (325, -32, 145), (982, 1721, 201), (712, 1860, 115)]:
            cog(d, x, y, r, 22, "#8e7956", "#cdb98c")
            for k in range(6):
                a = k * math.tau / 6
                xx, yy = x + r * 0.55 * math.cos(a), y + r * 0.55 * math.sin(a)
                d.ellipse(
                    (xx - r * 0.18, yy - r * 0.18, xx + r * 0.18, yy + r * 0.18), fill="#27433e"
                )
            d.ellipse(
                (x - r * 0.2, y - r * 0.2, x + r * 0.2, y + r * 0.2),
                fill="#263c39",
                outline="#d4b583",
                width=4,
            )
    elif w.name == "editorial":
        d.polygon([(0, 0), (885, 0), (0, 565)], fill="#f5c449")
        for i in range(8):
            d.arc(
                (-360 + i * 23, 1380 + i * 23, 940 - i * 23, 2640 - i * 23),
                185,
                350,
                fill="#462d66",
                width=11,
            )
        d.ellipse((786, 190, 1290, 694), fill="#534484")
        d.polygon([(860, 1580), (1080, 1315), (1080, 1920), (610, 1920)], fill="#ffcc63")
    else:
        for row in range(20):
            for col in range(12):
                if (row + col) % 2:
                    x, y = col * 102, row * 102
                    d.rectangle(
                        (x, y, x + 102, y + 102), fill=mix(w.base, w.shadow, 0.3 + row * 0.02)
                    )
        for x, y, col in [(166, 1703, "#fb846f"), (833, 1677, "#83d7be"), (942, 1745, "#f1c76d")]:
            d.ellipse((x - 65, y - 53, x + 65, y + 65), fill="#261a39", outline="#b8a6a8", width=6)
            d.ellipse((x - 53, y - 51, x + 53, y + 37), fill=col, outline="#faf0ce", width=4)
        for x in range(155, 960, 55):
            d.ellipse((x, 190, x + 18, 208), fill="#f1dc92")
    # Deterministic, low-amplitude print grain on the scenery only.
    noise = Image.frombytes("L", (270, 480), rng.randbytes(270 * 480)).resize(im.size)
    return Image.blend(im, noise.convert("RGB"), 0.035)


def plate(d, world, box, kind):
    x, y, z, b = box
    paper = world.paper
    shadow = mix(world.shadow, "#170f23", 0.45)
    if world.name == "lab":
        poly = [
            (x + 35, y),
            (z - 30, y),
            (z, y + 30),
            (z, b - 32),
            (z - 32, b),
            (x + 32, b),
            (x, b - 32),
            (x, y + 32),
        ]
        d.polygon([(u + 8, v + 10) for u, v in poly], fill=shadow)
        d.polygon(poly, fill=paper, outline="#86afa8", width=4)
        d.line((x + 40, y + 9, x + 180, y + 9), fill=world.accent, width=4)
    elif world.name == "ruins":
        d.rounded_rectangle((x + 8, y + 14, z + 8, b + 14), 28, fill=shadow)
        d.rounded_rectangle(box, 28, fill=paper, outline="#a58d68", width=5)
        d.rounded_rectangle((x + 12, y + 12, z - 12, b - 12), 20, outline="#c8b898", width=2)
    elif world.name == "desk":
        d.polygon(
            [(x + 12, y + 11), (z + 5, y - 5), (z + 12, b + 15), (x - 5, b + 22)], fill="#92755c"
        )
        d.rectangle(box, fill=paper)
        if kind == "board":
            for xx in (x + 46, z - 98):
                d.polygon(
                    [(xx, y - 9), (xx + 53, y - 14), (xx + 60, y + 21), (xx + 6, y + 28)],
                    fill="#d1bb92",
                )
    elif world.name == "workshop":
        d.rounded_rectangle((x + 7, y + 9, z + 7, b + 9), 15, fill=shadow)
        d.rounded_rectangle(box, 15, fill=paper, outline="#bfa779", width=5)
        for xx in (x + 17, z - 17):
            for yy in (y + 17, b - 17):
                d.ellipse((xx - 6, yy - 6, xx + 6, yy + 6), fill="#b5a485")
                d.line((xx - 3, yy + 3, xx + 3, yy - 3), fill=shadow, width=2)
    elif world.name == "editorial":
        d.rectangle((x + 12, y + 12, z + 12, b + 12), fill="#492e52")
        d.rectangle(box, fill=paper)
        d.rectangle((x, y, x + 11, b), fill="#a94635")
    else:
        d.rounded_rectangle((x + 5, y + 13, z + 5, b + 13), 48, fill=shadow)
        d.rounded_rectangle(box, 48, fill=paper, outline="#f6baba", width=8)
        d.rounded_rectangle((x + 12, y + 12, z - 12, b - 12), 38, outline="#965984", width=3)
