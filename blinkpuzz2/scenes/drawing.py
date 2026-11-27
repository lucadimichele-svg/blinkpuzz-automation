"""Audited foreground drawing in fixed, native-pixel coordinates."""

import math
from functools import lru_cache
from pathlib import Path

from PIL import ImageColor, ImageDraw, ImageFont

from blinkpuzz2.core import require

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FACES = {
    "sans": "DejaVuSans",
    "bold": "DejaVuSans-Bold",
    "mono": "DejaVuSansMono-Bold",
    "serif": "DejaVuSerif",
    "display": "DejaVuSerifCondensed-Bold",
    "cond": "DejaVuSansCondensed-Bold",
}


@lru_cache(maxsize=256)
def font(face, size):
    return ImageFont.truetype(str(FONT_DIR / (FACES[face] + ".ttf")), size)


def mix(a, b, t):
    return tuple(
        round(x + (y - x) * t)
        for x, y in zip(
            ImageColor.getrgb(a) if isinstance(a, str) else a,
            ImageColor.getrgb(b) if isinstance(b, str) else b,
        )
    )


def luminance(color):
    rgb = ImageColor.getrgb(color) if isinstance(color, str) else color
    lin = [v / 3294.6 if v <= 10 else ((v / 255 + 0.055) / 1.055) ** 2.4 for v in rgb]
    return sum(x * y for x, y in zip(lin, [0.2126, 0.7152, 0.0722]))


def contrast(a, b):
    lo, hi = sorted([luminance(a), luminance(b)])
    return (hi + 0.05) / (lo + 0.05)


class Surface:
    def __init__(self, image, ink, paper, accent):
        self.image, self.d = image, ImageDraw.Draw(image)
        self.ink, self.paper, self.accent = ink, paper, accent
        self.soft = mix(ink, paper, 0.68)
        self.records = []

    def text(
        self,
        x,
        y,
        value,
        size,
        face="bold",
        color=None,
        bg=None,
        anchor="mm",
        maxw=None,
        minimum=30,
    ):
        color, bg = color or self.ink, bg or self.paper
        value = str(value)
        while size > minimum and maxw and self.d.textlength(value, font=font(face, size)) > maxw:
            size -= 1
        f = font(face, size)
        box = self.d.textbbox((x, y), value, font=f, anchor=anchor)
        w, h = self.image.size
        require(
            size >= minimum and (not maxw or box[2] - box[0] <= maxw + 1), f"Text too wide: {value}"
        )
        require(0 <= box[0] < box[2] <= w and 0 <= box[1] < box[3] <= h, f"Clipped text: {value}")
        ratio = contrast(color, bg)
        require(ratio >= 4.5, f"Low contrast: {value}")
        for prev in self.records:
            a, b, c, d = prev["box"]
            require(
                min(c, box[2]) <= max(a, box[0]) or min(d, box[3]) <= max(b, box[1]),
                f"Text collision: {prev['text']} / {value}",
            )
        self.d.text((x, y), value, font=f, anchor=anchor, fill=color)
        self.records.append(
            {"text": value, "box": list(box), "px": size, "contrast": round(ratio, 2)}
        )

    def path(self, pts, fill=None, width=6):
        if len(pts) > 1:
            self.d.line(pts, fill=fill or self.ink, width=width, joint="curve")

    def disc(self, x, y, r, fill, outline=None, width=2):
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=width)

    def label(self, x, y, label, chosen=False, r=25):
        color = self.accent if chosen else self.ink
        self.disc(x, y, r, color)
        self.text(x, y, label, 34, color=self.paper, bg=color)

    def arrow(self, x, y, dx, dy, length=25, color=None):
        color = color or self.ink
        self.d.polygon(
            [
                (x + dx * length, y + dy * length),
                (x - dy * length * 0.55, y + dx * length * 0.55),
                (x + dy * length * 0.55, y - dx * length * 0.55),
            ],
            fill=color,
        )


def cog(d, x, y, r, teeth, fill, outline, phase=0):
    pts = []
    for i in range(teeth * 4):
        angle = phase + math.tau * i / (teeth * 4)
        rad = r if i % 4 in (1, 2) else r * 0.84
        pts.append((x + rad * math.cos(angle), y + rad * math.sin(angle)))
    d.polygon(pts, fill=fill)
    d.line([*pts, pts[0]], fill=outline, width=3, joint="curve")
