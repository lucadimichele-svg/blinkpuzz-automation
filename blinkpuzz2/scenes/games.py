"""Game diagrams share model coordinates with the oracle. No background supplies clues."""

import math

from blinkpuzz2.core import LETTERS
from blinkpuzz2.engines.lock import describe
from blinkpuzz2.engines.pipes import PORTS

from .drawing import cog, mix

W, H = 840, 650


def trace(s, cells, center, progress):
    count = max(2, math.ceil(len(cells) * progress))
    s.path([center(*p) for p in cells[:count]], s.accent, 10)


def laser(s, b, proof, winner, p):
    n = b["size"]
    pitch = min(107, 550 // n)
    x0, y0 = (W - n * pitch) // 2, (H - n * pitch) // 2

    def center(x, y):
        return x0 + (x + 0.5) * pitch, y0 + (y + 0.5) * pitch

    for i in range(n + 1):
        s.path([(x0 + i * pitch, y0), (x0 + i * pitch, y0 + n * pitch)], s.soft, 2)
        s.path([(x0, y0 + i * pitch), (x0 + n * pitch, y0 + i * pitch)], s.soft, 2)
    x, y = center(0, b["emitter_row"])
    s.path([(x0 - 52, y), (x - 11, y)], s.accent, 12)
    s.arrow(x - 15, y, 1, 0, 19, s.accent)
    if p:
        trace(s, proof["path"], center, p)
    for a, z, slope in b["mirrors"]:
        x, y = center(a, z)
        r = pitch * 0.34
        dy = -r if slope == "/" else r
        s.path([(x - r, y - dy), (x + r, y + dy)], s.ink, 11)
        s.disc(x - r, y - dy, 6, s.accent)
    for label, pt in zip(LETTERS, b["receivers"]):
        x, y = center(*pt)
        c = s.accent if p and label == winner else s.ink
        r = pitch * 0.39
        s.d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=c)
        s.text(x, y, label, 34, color=s.paper, bg=c)


def maze(s, b, proof, winner, p):
    n = b["size"]
    pitch = 540 // n
    x0, y0 = (W - n * pitch) // 2, 53

    def center(x, y):
        return x0 + (x + 0.5) * pitch, y0 + (y + 0.5) * pitch

    paths = {frozenset((tuple(a), tuple(z))) for a, z in b["passages"]}
    starts = {tuple(v) for v in b["entrances"]}
    end = tuple(b["exit"])
    if p:
        trace(s, proof["path"], center, p)
    for y in range(n):
        for x in range(n):
            xx, yy = x0 + x * pitch, y0 + y * pitch
            sides = [
                ((x, y - 1), (xx, yy), (xx + pitch, yy)),
                ((x - 1, y), (xx, yy), (xx, yy + pitch)),
            ]
            if y == n - 1:
                sides.append(((x, y + 1), (xx, yy + pitch), (xx + pitch, yy + pitch)))
            if x == n - 1 and (x, y) != end:
                sides.append(((x + 1, y), (xx + pitch, yy), (xx + pitch, yy + pitch)))
            for nb, a, z in sides:
                if (nb[0] < 0 and (x, y) in starts) or frozenset(((x, y), nb)) in paths:
                    continue
                s.path([(a[0] + 3, a[1] + 4), (z[0] + 3, z[1] + 4)], s.soft, 10)
                s.path([a, z], s.ink, 7)
    for label, pt in zip(LETTERS, b["entrances"]):
        s.label(x0 - 37, center(*pt)[1], label, bool(p and label == winner))
    x, y = center(*end)
    x += pitch * 0.7
    s.path([(x, y + 24), (x, y - 30)], s.ink, 5)
    s.d.polygon([(x, y - 30), (x + 36, y - 23), (x, y - 7)], fill=s.accent)


def pipe_piece(s, x, y, tile, r, color):
    for d in tile:
        dx, dy = PORTS[d]
        s.path([(x, y), (x + r * dx, y + r * dy)], color, 19)
    s.disc(x, y, 9, color)


def pipes(s, b, proof, winner, p):
    n = len(b["grid"])
    pitch = 420 // n
    x0, y0 = (W - n * pitch) // 2, 28

    def center(x, y):
        return x0 + (x + 0.5) * pitch, y0 + (y + 0.5) * pitch

    for y, row in enumerate(b["grid"]):
        for x, tile in enumerate(row):
            xx, yy = center(x, y)
            s.d.rectangle(
                (xx - pitch / 2, yy - pitch / 2, xx + pitch / 2, yy + pitch / 2),
                outline=s.soft,
                width=2,
            )
            if tile == "?" and not p:
                s.text(xx, yy, "?", 56, "display", s.accent)
            else:
                pipe_piece(
                    s,
                    xx,
                    yy,
                    b["pieces"][LETTERS.index(winner)] if tile == "?" else tile,
                    pitch / 2,
                    s.ink,
                )
    if p:
        trace(s, proof["traces"][winner], center, p)
    s.text(x0 - 55, center(0, b["inlet"])[1], "IN", 36, "mono")
    s.text(x0 + pitch * n + 56, center(0, b["outlet"])[1], "OUT", 36, "mono")
    for i, tile in enumerate(b["pieces"]):
        x = 179 + i * 242
        s.label(x - 64, 548, LETTERS[i], bool(p and winner == LETTERS[i]))
        s.d.rounded_rectangle((x - 17, 497, x + 83, 597), 12, outline=s.soft, width=3)
        pipe_piece(s, x + 33, 547, tile, 43, s.ink)


def circuit(s, b, proof, winner, p):
    d = s.d
    active = proof["truth_table"][winner if p else "initial"]
    ys = [133, 318, 512]
    for i, (label, bit, y) in enumerate(zip(b["inputs"], b["states"], ys)):
        changed = bool(p and label == winner)
        c = s.accent if changed else s.ink
        d.rounded_rectangle((26, y - 40, 155, y + 40), 36, fill=c)
        s.text(90, y, f"{label}  {bit ^ int(changed)}", 39, "mono", s.paper, c)
        xends = [309, 309, 570]
        elbow = [276, 276, 527][i]
        endy = [190, 245, 397][i]
        s.path(
            [(156, y), (elbow, y), (elbow, endy), (xends[i], endy)],
            s.accent if p and active[i] else s.ink,
            6,
        )
        if label in b["inverted"]:
            d.rectangle((174, y - 25, 257, y + 25), fill=s.paper, outline=s.ink, width=3)
            s.text(215, y, "NOT", 31, "mono")
    for i, (x, y) in enumerate([(308, 160), (566, 310)]):
        d.rounded_rectangle((x, y, x + 118, y + 115), 22, fill=s.paper, outline=s.ink, width=6)
        s.text(x + 59, y + 56, b["gates"][i], 39, "cond")
    s.path(
        [(426, 218), (482, 218), (482, 341), (566, 341)], s.accent if p and active[3] else s.ink, 6
    )
    s.path([(684, 368), (730, 368)], s.ink, 6)
    s.disc(766, 368, 38, s.accent if p else s.paper, s.ink, 6)
    s.path([(749, 350), (782, 385)], s.ink, 4)
    s.path([(782, 350), (749, 385)], s.ink, 4)
    if p:
        for a in range(0, 360, 45):
            co, si = math.cos(math.radians(a)), math.sin(math.radians(a))
            s.path([(766 + 48 * co, 368 + 48 * si), (766 + 62 * co, 368 + 62 * si)], s.accent, 5)


def gears(s, b, proof, winner, p):
    cells = [tuple(q) for q in b["wheels"]]
    minx, maxx = min(x for x, y in cells), max(x for x, y in cells)
    miny, maxy = min(y for x, y in cells), max(y for x, y in cells)
    pitch = 112
    marks = {tuple(pt): label for pt, label in zip(b["marked"], LETTERS)}
    directions = {(x, y): (sign, depth) for x, y, sign, depth in proof["directions"]}
    for x, y in cells:
        xx = W / 2 + (x - (minx + maxx) / 2) * pitch
        yy = H / 2 + (y - (miny + maxy) / 2) * pitch
        sign, depth = directions[x, y]
        lit = p and depth <= math.ceil(6 * p)
        c = s.accent if lit and sign == 1 else mix(s.paper, s.ink, 0.25)
        phase = (math.pi / 12 if sign < 0 else 0) + sign * p * 0.38
        cog(s.d, xx, yy, 60, 12, c, s.ink, phase)
        s.disc(xx, yy, 33, s.paper, s.ink, 3)
        if (x, y) in marks:
            s.text(xx, yy, marks[x, y], 38)
        elif [x, y] == b["drive"]:
            s.text(xx, yy, "↻", 48, "bold", s.accent)
        else:
            s.disc(xx, yy, 10, s.ink)


def routes(s, b, proof, winner, p):
    pts = {
        "S": (61, b["heights"][0]),
        "A": (302, 84),
        "B": (302, 315),
        "C": (302, 546),
        "U": (555, 190),
        "V": (555, 455),
        "X": (782, b["heights"][1]),
    }
    best = proof["best"][0]
    for edge, cost in b["roads"].items():
        a, z = (pts[v] for v in edge)
        chosen = bool(p and edge in best[: 1 + math.ceil(3 * p)])
        s.path([a, z], s.accent if chosen else s.ink, 10 if chosen else 5)
        x, y = (a[0] + z[0]) / 2, (a[1] + z[1]) / 2
        s.disc(x, y, 26, s.paper, s.soft, 2)
        s.text(x, y, cost, 35, "mono")
    for k, (x, y) in pts.items():
        if k in "UV":
            s.disc(x, y, 13, s.ink)
        else:
            s.label(x, y, k, bool(p and k in best), 30)


def bitmap(s, x, y, bits, n, tile, marked=False):
    unit = tile / n
    for i, bit in enumerate(bits):
        a = x + i % n * unit
        b = y + i // n * unit
        s.d.rectangle(
            (a, b, a + unit, b + unit),
            fill=s.ink if bit == "1" else s.paper,
            outline=s.soft,
            width=2,
        )
    if marked:
        s.d.rectangle((x - 5, y - 5, x + tile + 5, y + tile + 5), outline=s.accent, width=5)


def pattern(s, b, proof, winner, p):
    for i in range(3):
        x = 75 + i * 264
        if i < 2 or p:
            bitmap(s, x, 61, proof["sequence"][i] if i == 2 else b["sequence"][i], 3, 160, i == 2)
        else:
            s.d.rectangle((x, 61, x + 160, 221), outline=s.soft, width=4)
            s.text(x + 80, 141, "?", 90, "display", s.accent)
        if i < 2:
            s.text(x + 210, 144, "→", 45)
    s.path([(56, 290), (784, 290)], s.soft, 2)
    for i, bits in enumerate(b["tiles"]):
        x = 85 + i * 260
        bitmap(s, x, 361, bits, 3, 147, bool(p and winner == LETTERS[i]))
        s.label(x + 74, 565, LETTERS[i], bool(p and winner == LETTERS[i]))


def nonogram(s, b, proof, winner, p):
    unit = 62
    x0, y0 = 325, 83
    for i in range(4):
        x, y = x0 + i * unit, y0 + i * unit
        col = b["columns"][i]
        for j, k in enumerate(col):
            s.text(x + unit / 2, y0 - 22 - (len(col) - j - 1) * 34, k, 32, "mono")
        s.text(x0 - 50, y + unit / 2, " ".join(map(str, b["rows"][i])), 34, "mono")
    bits = proof["bitmap"] if p else "0" * 16
    bitmap(s, x0, y0, bits, 4, unit * 4)
    for i, bits in enumerate(b["prints"]):
        x = 98 + i * 251
        bitmap(s, x, 397, bits, 4, 140, bool(p and winner == LETTERS[i]))
        s.label(x + 70, 592, LETTERS[i], bool(p and winner == LETTERS[i]))


def token(s, x, y, name, r):
    if name == "K":
        s.disc(x - r * 0.36, y - r * 0.28, r * 0.49, None, s.ink, max(4, int(r * 0.24)))
        s.path(
            [(x - r * 0.1, y), (x + r * 0.68, y + r * 0.72), (x + r * 0.94, y + r * 0.43)],
            s.ink,
            max(4, int(r * 0.25)),
        )
    elif name == "M":
        s.disc(x, y, r, s.ink)
        s.disc(x + r * 0.45, y - r * 0.33, r * 0.86, s.paper)
    elif name == "S":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.43
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        s.d.polygon(pts, fill=s.ink)
    elif name == "F":
        s.d.ellipse((x - r * 0.9, y - r * 0.59, x + r * 0.45, y + r * 0.59), fill=s.ink)
        s.d.polygon([(x + r * 0.20, y), (x + r, y - r * 0.63), (x + r, y + r * 0.63)], fill=s.ink)
        s.disc(x - r * 0.48, y - r * 0.1, r * 0.09, s.paper)
    elif name == "C":
        s.disc(x, y, r, s.ink)
    elif name == "D":
        s.d.polygon([(x - r, y), (x, y - r), (x + r, y), (x, y + r)], fill=s.ink)
    else:
        s.d.polygon([(x, y - r), (x + r, y + r * 0.8), (x - r, y + r * 0.8)], fill=s.ink)


def lock(s, b, proof, winner, p):
    for i, c in enumerate(b["clues"]):
        y = 63 + i * 65
        s.disc(111, y, 7, s.accent)
        s.text(151, y, describe(c), 39, "serif", anchor="lm")
    s.path([(64, 242), (776, 242)], s.soft, 2)
    for i, order in enumerate(b["orders"]):
        y = 321 + i * 116
        chosen = bool(p and winner == LETTERS[i])
        s.label(121, y, LETTERS[i], chosen)
        s.d.rounded_rectangle(
            (191, y - 44, 738, y + 44), 20, outline=s.accent if chosen else s.soft, width=4
        )
        for j, c in enumerate(order):
            token(s, 267 + j * 131, y, c, 29)


def load_icons(s, x, y, load, r):
    for i, c in enumerate(load):
        token(s, x + (i - (len(load) - 1) / 2) * 2.28 * r, y, c, r)


def balance(s, b, proof, winner, p):
    for i, (left, right) in enumerate(b["scales"]):
        x = 216 + i * 408
        for cx, load in [(x - 94, left), (x + 94, right)]:
            load_icons(s, cx, 115, load, 19)
            s.d.arc((cx - 74, 112, cx + 74, 156), 0, 180, fill=s.ink, width=5)
            s.path([(cx, 156), (cx, 184)], s.ink, 5)
        s.path([(x - 95, 184), (x + 95, 184)], s.ink, 7)
        s.d.polygon([(x, 186), (x - 27, 234), (x + 27, 234)], fill=s.accent)
    s.path([(44, 270), (796, 270)], s.soft, 2)
    load_icons(s, 292, 348, b["target"], 29)
    s.text(425, 345, "=", 51, "serif")
    if p:
        load_icons(s, 567, 348, b["loads"][LETTERS.index(winner)], 29)
    else:
        s.text(566, 345, "?", 62, "display", s.accent)
    for i, load in enumerate(b["loads"]):
        x = 157 + i * 263
        s.d.rounded_rectangle((x - 109, 448, x + 109, 548), 18, outline=s.soft, width=3)
        load_icons(s, x, 497, load, 24)
        s.label(x, 595, LETTERS[i], bool(p and winner == LETTERS[i]))


DIAGRAMS = {
    f.__name__: f
    for f in [laser, maze, pipes, circuit, gears, routes, pattern, nonogram, lock, balance]
}
