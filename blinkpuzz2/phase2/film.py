"""Compose a full-bleed set, persistent objective and a proof-driven motion track."""

import math

from PIL import Image, ImageDraw

from blinkpuzz2.core import require
from blinkpuzz2.scenes.drawing import contrast, font

from .bake import passes
from .experience import SAFE

# Hand-set line breaks and typographic scale are part of each grammar.
TITLES = {
    "laser": ("Which crystal", "catches the beam?", "cond", "left"),
    "maze": ("Which gate reaches", "the flag?", "display", "left"),
    "search": ("Find the", "matching moth.", "display", "left"),
    "mismatch": ("Spot the", "changed control.", "bold", "left"),
    "fit": ("Which insert fits", "the socket?", "cond", "center"),
    "pipes": ("Which pipe seals", "the gap?", "cond", "left"),
    "gears": ("Which way will the", "red gear turn?", "display", "center"),
    "shadow": ("Which tower casts", "this shadow?", "serif", "center"),
}
ACCENT = {
    "laser": "#9bf9f3",
    "maze": "#fbe39d",
    "search": "#ffe0aa",
    "mismatch": "#a9f2cf",
    "fit": "#ffcd76",
    "pipes": "#9aefea",
    "gears": "#ffd486",
    "shadow": "#ffe2ab",
}


def ease(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def dot(d, p, r, col):
    x, y = p
    d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def arrow(d, p, angle, r, col):
    x, y = p
    u, v = math.cos(angle), math.sin(angle)
    d.polygon(
        [
            (x + r * u, y + r * v),
            (x - r * 0.9 * u + r * 0.68 * v, y - r * 0.9 * v - r * 0.68 * u),
            (x - r * 0.9 * u - r * 0.68 * v, y - r * 0.9 * v + r * 0.68 * u),
        ],
        fill=col,
    )


def circular(d, p, r, clockwise, col, phase=0):
    x, y = p
    a = 20 + phase if clockwise else 138 + phase
    d.arc((x - r, y - r, x + r, y + r), a, a + 183, fill="#193135", width=13)
    d.arc((x - r, y - r, x + r, y + r), a, a + 183, fill=col, width=7)
    rad = math.radians(a + 183 if clockwise else a)
    tip = (x + r * math.cos(rad), y + r * math.sin(rad))
    arrow(d, tip, rad + (math.pi / 2 if clockwise else -math.pi / 2), 10, col)


def partial(points, t):
    dist = [math.dist(a, b) for a, b in zip(points, points[1:])]
    left = max(0, min(1, t)) * sum(dist)
    result = [tuple(points[0])]
    for a, b, n in zip(points, points[1:], dist):
        if left <= n and n:
            result.append(lerp(a, b, left / n))
            break
        result.append(tuple(b))
        left -= n
    return result


def trail(d, points, t, outer, inner, width):
    pts = partial(points, t)
    d.line(pts, fill=outer, width=width, joint="curve")
    d.line(pts, fill=inner, width=max(2, width // 3), joint="curve")
    return pts


def focus(d, p, r, col):
    x, y = p
    for start in (7, 97, 187, 277):
        d.arc((x - r, y - r, x + r, y + r), start, start + 64, fill="#183139", width=11)
        d.arc((x - r, y - r, x + r, y + r), start, start + 64, fill=col, width=6)


def text_on_scene(im, xy, txt, face, size, color, anchor, records, maxw=860):
    draw = ImageDraw.Draw(im)
    while size > 32 and draw.textlength(txt, font=font(face, size)) > maxw:
        size -= 1
    ft = font(face, size)
    box = draw.textbbox(xy, txt, font=ft, anchor=anchor)
    if not (SAFE[0] <= box[0] and box[2] <= SAFE[2] and SAFE[1] <= box[1] and box[3] <= SAFE[3]):
        raise ValueError(f"Text outside phone safe zone: {txt} {box}")
    # Contrast against the brightest background actually under the letters.
    patch = im.crop(box)
    background = tuple(c[1] for c in patch.getextrema())
    ratio = contrast(color, background)
    require(ratio >= 4.5, f"Insufficient contrast: {txt} ({ratio:.2f})")
    for item in records:
        a, b, c, d = item["box"]
        require(
            min(box[2], c) <= max(box[0], a) or min(box[3], d) <= max(box[1], b), "Type collision"
        )
    draw.text(xy, txt, fill=color, font=ft, anchor=anchor)
    records.append(
        {
            "text": txt,
            "box": list(box),
            "px": size,
            "contrast": round(ratio, 2),
            "glyph_width": round(draw.textlength(txt, font=ft), 1),
        }
    )


def title(im, s, cover=False):
    lines = TITLES[s.family]
    align = lines[-1]
    # The clock uses the space beneath its movement. Covers bring type into the grid crop.
    low = s.family == "gears"
    cy = (1320 if low else 493) if cover else (1348 if low else 275)
    mask = Image.new("L", (1, 1920))
    # Optical falloff across native imagery, without a new plaque or instruction card.
    end = cy + 119 + (49 if s.instruction and not cover else 0)
    mask.putdata(
        [
            round(246 * max(0, min(1, (end + 90 - y) / 90)))
            if not low
            else round(244 * max(0, min(1, (y - cy + 75) / 70)))
            for y in range(1920)
        ]
    )
    im = Image.composite(Image.new("RGB", im.size, "#18252c"), im, mask.resize(im.size))
    x = 502 if align == "center" else 78
    anchor = "mm" if align == "center" else "lm"
    rec = []
    for i, txt in enumerate(lines[:2]):
        text_on_scene(
            im,
            (x, cy + (88 if cover else 80) * i),
            txt,
            lines[2],
            79 if cover else 75,
            "#fff4d9",
            anchor,
            rec,
        )
    if s.instruction and not cover:
        text_on_scene(im, (x, cy + 146), s.instruction, "sans", 39, ACCENT[s.family], anchor, rec)
    # A restrained wordmark in a protected margin, outside the playable geometry.
    if not low:
        text_on_scene(
            im,
            (x, cy - 55),
            "BLINKPUZZ   /   " + s.grammar.upper(),
            "mono",
            32,
            ACCENT[s.family],
            anchor,
            rec,
        )
    return im, rec


class Shot:
    def __init__(self, s, st, cache):
        self.s, self.st = s, st
        self.beauty, self.sprites = passes(cache)
        self.base, self.type_audit = title(self.beauty, s)
        self.m = st.markers
        self.accent = ACCENT[s.family]
        # Permanently visible labels on physical fittings, never on transient cards.
        self.fitting_audit = []
        for lab in st.labels:
            x, y = lab["xy"]
            size = lab["px"]
            text = lab["text"]
            if text == "?":
                continue
            d = ImageDraw.Draw(self.base)
            w = max(size * 0.82, d.textlength(text, font=font("cond", size)) / 2 + 4)
            d.rounded_rectangle(
                (x - w, y - size * 0.64, x + w, y + size * 0.64), radius=15, fill="#18252c"
            )
            text_on_scene(
                self.base, (x, y), text, "cond", size, "#fff4d9", "mm", self.fitting_audit, 100
            )
        self.static = self.objects(self.base.copy(), 0, False)
        self.paint(self.static, 0, False)

    def objects(self, im, t, reveal):
        s, st = self.s, self.st
        for key, sprite in self.sprites.items():
            pos = st.sprites[key]["center"]
            rotation = 0
            if reveal and s.family == "gears":
                _, x, y = key.split("-")
                sign = next(v[2] for v in s.proof["directions"] if v[:2] == [int(x), int(y)])
                rotation = -sign * 200 * t
            if reveal and s.family == "pipes" and key == f"spare-{s.proof['slot']}":
                pos = lerp(pos, self.m["gap"], ease(t / 0.35))
            if reveal and s.family == "fit" and key == s.proof["answer"]:
                rotation = -360 * s.proof["clockwise_slots"] / s.proof["slots"] * ease(t / 0.68)
                pos = lerp(pos, self.m["socket"], ease((t - 0.12) / 0.64))
            if rotation:
                sprite = sprite.rotate(rotation, Image.Resampling.BICUBIC)
            x = round(pos[0] - (sprite.width - 1) / 2)
            y = round(pos[1] - (sprite.height - 1) / 2)
            im.paste(sprite, (x, y), sprite)
        return im

    def paint(self, im, t, reveal):
        d = ImageDraw.Draw(im)
        f = self.s.family
        m = self.m
        proof = self.s.proof
        ac = self.accent
        if f == "laser":
            path = m["ray"]
            p = m["muzzle"]
            end = lerp(path[0], path[1], 0.26)
            d.line([tuple(p), end], fill="#214548", width=14)
            d.line([tuple(p), end], fill="#afffec", width=7)
            arrow(d, end, math.atan2(end[1] - p[1], end[0] - p[0]), 11, "#cfffe8")
            if reveal:
                pts = trail(d, [p, *path], min(1, t / 0.83), "#35c5b9", "#fff5cd", 14)
                dot(d, pts[-1], 9, "#fffbd6")
                if t > 0.83:
                    focus(d, m["receiver"], 52 + 6 * math.sin(math.pi * t), ac)
        if f == "maze" and reveal:
            pts = trail(d, m["route"], min(1, t / 0.9), "#227487", "#ebf9cd", 10)
            x, y = pts[-1]
            a = math.atan2(y - pts[-2][1], x - pts[-2][0])
            arrow(d, (x, y), a, 14, "#e96c40")
            if t > 0.85:
                focus(d, m["flag"], 28, ac)
        if f == "search" and reveal:
            target = m[proof["answer"]]
            radius = 100 - 17 * ease(t / 0.5)
            focus(d, target, radius, ac)
            # Bring an enlargement of this exact specimen into the existing sample lens.
            if t > 0.25:
                x, y = target
                sx, sy = m["sample"]
                r = 81
                crop = self.beauty.crop(
                    (round(x - r), round(y - r), round(x + r), round(y + r))
                ).resize((197, 197), Image.Resampling.LANCZOS)
                mask = Image.new("L", crop.size, 0)
                ImageDraw.Draw(mask).ellipse(
                    (0, 0, 196, 196), fill=round(255 * ease((t - 0.25) / 0.35))
                )
                im.paste(crop, (round(sx - 98), round(sy - 98)), mask)
        if f == "mismatch" and reveal:
            i = proof["differences"][0]
            p = m[f"upper-{i}"]
            q = m[f"lower-{i}"]
            for a in (p, q):
                focus(d, a, 74 - 14 * ease(t / 0.55), ac)
            for start in range(0, 30, 2):
                if start / 30 < ease(t / 0.65):
                    d.line([lerp(p, q, start / 30), lerp(p, q, (start + 1) / 30)], fill=ac, width=4)
        if f == "fit" and reveal and t > 0.75:
            focus(d, m["socket"], 132 + 8 * math.sin(t * math.pi), ac)
        if f == "pipes":
            if not reveal or t < 0.3:
                x, y = m["gap"]
                d.text((x, y), "?", font=font("cond", 47), fill="#fff8d7", anchor="mm")
            if reveal and t > 0.34:
                pts = trail(d, m["water"], ease((t - 0.34) / 0.62), "#148a9e", "#b6fded", 11)
                dot(d, pts[-1], 7, "#f4ffe6")
        if f == "gears":
            circular(d, m["driver"], 40, True, "#f9ffe5", t * 200 if reveal else 0)
            if reveal:
                circular(
                    d,
                    m["output"],
                    58,
                    proof["answer"] == "clockwise",
                    "#fff0aa",
                    t * (200 if proof["answer"] == "clockwise" else -200),
                )
        if f == "shadow" and reveal:
            i = proof["tower"]
            tx, ty = m[f"tower-{i}"]
            sx, sy = m["screenbase"]
            h = proof["projections"][i]
            factor = ease(t / 0.77)
            cx, cy = lerp((tx, ty - 5), (sx, sy), factor)
            unit = 38 + 28 * factor
            pts = [(cx - len(h) * unit / 2, cy)]
            for j, v in enumerate(h):
                xx = cx + (j - len(h) / 2) * unit
                pts.extend([(xx, cy - v * unit), (xx + unit, cy - v * unit)])
            pts.extend([(cx + len(h) * unit / 2, cy), pts[0]])
            d.line(pts, fill="#613c35", width=9, joint="curve")
            d.line(pts, fill=ac, width=4, joint="curve")
            focus(d, (tx, ty - 60), 104, ac)
        return im

    def frame(self, t, reveal):
        if reveal:
            return self.paint(self.objects(self.base.copy(), t, True), t, True)
        im = self.static.copy()
        d = ImageDraw.Draw(im)
        # Ambient glints stay off the clue surface; the complete stationary solve geometry
        # comes from the same still at every time, including the first video frame.
        x, y = {
            "laser": (1039, 1566),
            "maze": (143, 1574),
            "search": (371, 1569),
            "mismatch": (895, 1610),
            "fit": (66, 1560),
            "pipes": (976, 1570),
            "gears": (881, 1566),
            "shadow": (503, 1570),
        }[self.s.family]
        alpha = (1 - math.cos(t * math.tau)) / 2
        size = 3 + 5 * alpha
        dot(d, (x, y), size, self.accent)
        return im

    def cover(self):
        # Frame the objects as a poster print; the opening film remains independently playable.
        bare = self.objects(self.beauty.copy(), 0, False)
        self.paint(bare, 0, False)
        im, audit = title(bare, self.s, True)
        return im, audit
