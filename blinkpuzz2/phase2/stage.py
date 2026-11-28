"""Model-space scene graph. Units are 1/100 Blender unit, positive Y towards the viewer."""

import math

from .experience import FORMATS

PAINT = {
    "ink": ("#172631", 0.26, 0.38),
    "rubber": ("#12191e", 0.05, 0.72),
    "nickel": ("#bdcbd4", 0.74, 0.28),
    "brass": ("#d8a448", 0.66, 0.31),
    "copper": ("#c77545", 0.56, 0.29),
    "ivory": ("#f3e4bc", 0.12, 0.39),
    "white": ("#f5eee1", 0.13, 0.31),
    "turquoise": ("#37afad", 0.42, 0.32),
    "jade": ("#245e57", 0.30, 0.42),
    "blue": ("#315a94", 0.30, 0.33),
    "red": ("#cf463c", 0.29, 0.32),
    "orange": ("#f78935", 0.25, 0.30),
    "walnut": ("#754331", 0.03, 0.46),
    "oak": ("#b7844e", 0.06, 0.46),
    "linen": ("#d8c5a1", 0, 0.91),
    "slate": ("#334b54", 0.2, 0.47),
    "stone": ("#e6c397", 0.05, 0.68),
    "sand": ("#b89164", 0.07, 0.60),
    "ocean": ("#206c83", 0.38, 0.23),
    "aubergine": ("#492c48", 0.12, 0.62),
    "velvet": ("#882f41", 0.04, 0.79),
    "honey": ("#f4bf66", 0.05, 0.42),
    "mint": ("#a3d7b1", 0.15, 0.45),
    "sky": ("#7ca6bc", 0.17, 0.40),
    "wing": ("#ab673c", 0.08, 0.56),
    "wingtip": ("#3c2a31", 0.03, 0.52),
    "lume": ("#bafde6", 0.05, 0.25),
    "rose": ("#dc8d78", 0.23, 0.31),
    "glass": ("#83d9dd", 0.62, 0.16),
    "charcoal": ("#282824", 0.08, 0.65),
}


class Stage:
    def __init__(self, s):
        self.family = s.family
        self.tilt = FORMATS[s.family].camera_tilt
        self.nodes = []
        self.sprites = {}
        self.markers = {}
        self.labels = []
        self.group = None
        self.art = {
            "laser": "ink",
            "maze": "ocean",
            "search": "walnut",
            "mismatch": "aubergine",
            "fit": "slate",
            "pipes": "jade",
            "gears": "walnut",
            "shadow": "aubergine",
        }[s.family]

    @property
    def cos(self):
        return math.cos(math.radians(self.tilt))

    @property
    def sin(self):
        return math.sin(math.radians(self.tilt))

    def floor(self, x, y, z=0):
        return [x, 960 + (y - 960) / self.cos, z]

    def screen(self, p):
        x, y, z = p
        return [x, 960 + (y - 960) * self.cos - z * self.sin]

    def add(self, kind, mat, pos, tag=None, **kw):
        node = dict(kind=kind, mat=mat, pos=list(pos), **kw)
        if tag:
            node["tag"] = tag
        if self.group:
            node["group"] = self.group
        self.nodes.append(node)
        return node

    def box(self, p, size, mat, bevel=5, angle=0, tag=None):
        return self.add("box", mat, p, tag, size=list(size), bevel=bevel, angle=angle)

    def cyl(self, p, r, h, mat, n=48, bevel=2, tag=None):
        return self.add("disc", mat, p, tag, r=r, h=h, n=n, bevel=bevel)

    def ball(self, p, scale, mat, tag=None):
        return self.add("ball", mat, p, tag, size=list(scale))

    def line(self, points, r, mat, tag=None):
        return self.add("tube", mat, points[0], tag, points=[list(p) for p in points], r=r)

    def solid(self, p, outline, h, mat, bevel=2, tag=None, hole=None):
        return self.add("profile", mat, p, tag, outline=outline, h=h, bevel=bevel, hole=hole)

    def ring(self, p, outer, inner, h, mat, n=64):
        return self.solid(p, circle(outer, n), h, mat, 1, hole=circle(inner, n))

    def screw(self, x, y, z, r=8):
        self.cyl((x, y, z), r, 4, "nickel", 20, 1)
        self.line(
            [(x - r * 0.55, y - r * 0.20, z + 2), (x + r * 0.55, y + r * 0.2, z + 2)], 1.4, "ink"
        )

    def label(self, text, p, size=36):
        self.labels.append({"text": text, "xy": self.screen(p), "px": size})

    def marker(self, key, p):
        self.markers[key] = self.screen(p)

    def sprite(self, key, center, radius):
        self.group = key
        self.sprites[key] = {"center": self.screen(center), "radius": int(radius)}

    def export(self):
        return {
            "family": self.family,
            "tilt": self.tilt,
            "nodes": self.nodes,
            "sprites": self.sprites,
            "markers": self.markers,
            "labels": self.labels,
            "palette": PAINT,
        }


def circle(r, n):
    return [[r * math.cos(math.tau * i / n), r * math.sin(math.tau * i / n)] for i in range(n)]


def offset(p, dx=0, dy=0, dz=0):
    return [p[0] + dx, p[1] + dy, p[2] + dz]


def polar(r, angle):
    a = math.radians(angle)
    return [r * math.cos(a), r * math.sin(a)]


def grid_pose(s):
    # Orthogonal board basis, expressed in model space rather than warped bitmap coordinates.
    if s.family == "laser":
        return (501, 960, min(143, 720 / s.board["size"]), [-5, 4, 0][s.edition])
    if s.family == "maze":
        return (507, 986, min(115, 612 / s.board["size"]), [23, 30, 18][s.edition])
    if s.family == "pipes":
        return (503, 895, min(151, 665 / len(s.board["grid"])), 0)
    return (505, 955, 149, [-6, 3, 0][s.edition])


def grid(s, stage, x, y, z=0):
    cx, cy, pitch, turn = grid_pose(s)
    n = {
        "laser": lambda: s.board["size"],
        "maze": lambda: s.board["size"],
        "pipes": lambda: len(s.board["grid"]),
        "gears": lambda: 5,
    }[s.family]()
    dx, dy = (x - (n - 1) / 2) * pitch, (y - (n - 1) / 2) * pitch
    if s.family == "gears":
        xs, ys = zip(*s.board["wheels"])
        dx = (x - (min(xs) + max(xs)) / 2) * pitch
        dy = (y - (min(ys) + max(ys)) / 2) * pitch
    a = math.radians(turn)
    p = stage.floor(cx, cy, z)
    return offset(p, dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a))


def beam_box(st, a, b, w, h, mat, tag=None):
    mid = [(x + y) / 2 for x, y in zip(a, b)]
    return st.box(
        mid,
        [math.dist(a[:2], b[:2]), w, h],
        mat,
        min(5, w * 0.18),
        math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])),
        tag,
    )
