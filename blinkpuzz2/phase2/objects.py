"""Four object-first sets: specimen drawer, paired instruments, fly press and shadow theatre."""

import math

from .sets import floor_detail
from .stage import offset


def moth(st, p, wing, spots, scale, angle, tag):
    a = math.radians(angle)

    def turn(x, y):
        return [
            scale * (x * math.cos(a) - y * math.sin(a)),
            scale * (x * math.sin(a) + y * math.cos(a)),
        ]

    def pt(x, y, z):
        return offset(p, *turn(x, y), scale * z)

    def patch(shape, z, h, mat, name=None):
        return st.solid(
            offset(p, dz=z * scale), [turn(x, y) for x, y in shape], h * scale, mat, 1, name
        )

    # Three different forewing silhouettes: swept swallowtail, round silk and scalloped atlas.
    fronts = [
        [(0, -8), (17, -31), (51, -55), (61, -54), (54, -27), (43, -4), (28, 13), (9, 9)],
        [
            (0, -8),
            (11, -28),
            (30, -45),
            (49, -45),
            (57, -35),
            (58, -17),
            (49, -3),
            (28, 13),
            (9, 9),
        ],
        [
            (0, -8),
            (16, -31),
            (52, -42),
            (65, -38),
            (56, -26),
            (61, -19),
            (51, -12),
            (55, -5),
            (35, 7),
            (9, 9),
        ],
    ]
    wing_shape = fronts[wing]
    for side in (-1, 1):

        def flip(points):
            return [(side * x, y) for x, y in points]

        patch(
            flip(
                [
                    (2, 4),
                    (27, -1),
                    (44, 12),
                    (40, 29),
                    (31, 34),
                    (26, 31),
                    (20, 39),
                    (10, 28),
                    (4, 15),
                ]
            ),
            3,
            4,
            "rose",
        )
        patch(flip(wing_shape), 8, 4, "wingtip", tag + ("-left" if side < 0 else "-right"))
        inset = [(x * 0.83 + 2, y * 0.79 + 1) for x, y in wing_shape]
        patch(flip(inset), 11, 2, "orange")
        for end in ((42, -35), (48, -17), (32, 2)):
            st.line([pt(side * 6, 5, 14), pt(side * end[0], end[1], 14)], scale * 0.85, "wing")
        for j, (x, y) in enumerate([(30, -14), (41, -24), (19, -9)][:spots]):
            st.cyl(
                pt(side * x, y, 16),
                scale * 5.8,
                3 * scale,
                "wingtip",
                20,
                1,
                tag + f"-spot-{side}-{j}",
            )
            st.cyl(pt(side * x, y, 18), scale * 2.6, 2 * scale, "ivory", 16, 0)
        st.line(
            [pt(side * 2, -12, 12), pt(side * 7, -23, 12), pt(side * 13, -27, 13)],
            1.4 * scale,
            "charcoal",
        )
    st.ball(pt(0, 5, 13), (5 * scale, 23 * scale, 5 * scale), "charcoal")
    st.ball(pt(0, -14, 14), (6 * scale, 6 * scale, 6 * scale), "wingtip")


def search(st, s):
    b = s.board
    cols, rows = b["shape"]
    floor_detail(st, "walnut", s.edition)
    # Deep open cabinet. The reference sits in a separate brass magnifier above the rows.
    center = st.floor(510, 1075, -20)
    st.box(center, (963, 899 / st.cos, 57), "oak", 14)
    st.box(offset(center, dz=34), (905, 838 / st.cos, 18), "linen", 8)
    for x in (41, 982):
        st.box(st.floor(x, 1075, 17), (38, 928 / st.cos, 57), "walnut", 7)
        for y in (647, 1498):
            st.screw(*st.floor(x, y, 49), r=9)
    for y in (642, 1507):
        st.box(st.floor(510, y, 18), (975, 36, 62), "walnut", 7)
    target = st.floor(513, 615, 67)
    st.line([offset(target, 83, -23, -26), offset(target, 226, -68, -26)], 16, "brass")
    st.cyl(offset(target, dz=-12), 118, 23, "ivory")
    st.ring(target, 121, 109, 16, "brass")
    moth(st, target, *b["sample"], 1.48, 0, "sample")
    st.marker("sample", target)
    for i, (wing, spots, dx, dy, angle) in enumerate(b["specimens"]):
        col, row = i % cols, i // cols
        x = 123 + (col + 0.5) * 758 / cols + dx
        y = 746 + (row + 0.5) * 677 / rows + dy
        p = st.floor(x, y, 30)
        moth(st, p, wing, spots, 1.12 if rows < 4 else 1.03, angle, f"moth-{i}")
        st.marker(f"specimen-{i}", offset(p, dz=12))
    for x in (371, 650):
        st.cyl(st.floor(x, 1570, 2), 27, 24, "brass")
    st.line(
        [
            st.floor(371, 1570, 10),
            st.floor(395, 1601, 25),
            st.floor(626, 1601, 25),
            st.floor(650, 1570, 10),
        ],
        11,
        "brass",
    )


def instrument(st, p, kind, state, tag):
    x, y, z = p
    if kind == "dial":
        st.cyl(p, 45, 18, "rubber")
        st.ring(offset(p, dz=11), 40, 36, 6, "nickel")
        st.cyl(offset(p, dz=16), 31, 20, "jade", 32, 4)
        angle = (-145, -90, -35)[state] * math.pi / 180
        st.line(
            [offset(p, dz=29), offset(p, 27 * math.cos(angle), 27 * math.sin(angle), 29)],
            5,
            "ivory",
            tag,
        )
        for deg in (-145, -90, -35):
            a = math.radians(deg)
            st.cyl(offset(p, 47 * math.cos(a), 47 * math.sin(a), 12), 3, 4, "ivory", 12, 0)
    elif kind == "lever":
        st.box(p, (86, 53, 16), "rubber", 11)
        for i in (-1, 0, 1):
            st.cyl(offset(p, i * 28, 0, 11), 10, 7, "nickel")
        st.line([offset(p, dz=12), offset(p, (state - 1) * 27, -14, 38)], 7, "nickel")
        st.ball(offset(p, (state - 1) * 27, -14, 40), (13, 13, 12), "red", tag)
    else:
        st.box(p, (100, 39, 11), "ink", 8)
        st.box(offset(p, dz=6), (79, 7, 4), "rubber", 3)
        for k in (-1, 0, 1):
            st.box(offset(p, k * 30, -24, 4), (3, 7, 3), "ivory", 1)
        st.box(offset(p, (state - 1) * 30, 0, 14), (20, 40, 23), "honey", 5, tag=tag)
        st.box(offset(p, (state - 1) * 30, 0, 27), (3, 25, 2), "ivory", 1)


def mismatch(st, s):
    b = s.board
    cols, rows = b["layout"]
    floor_detail(st, "aubergine", s.edition)
    for idx, bank in enumerate(["upper", "lower"]):
        cy = (766, 1242)[idx]
        center = st.floor(501, cy, 0)
        st.box(center, (873, 408, 48), "walnut", 26)
        st.box(offset(center, dz=27), (807, 365, 28), "jade", 17)
        for x in (-413, 413):
            st.box(offset(center, x, 0, 29), (35, 394, 44), "oak", 11)
        for x in (-360, 360):
            for y in (-149, 149):
                st.screw(*offset(center, x, y, 44), r=7)
        for i, (kind, state) in enumerate(b[bank]):
            x = 161 + (i % cols + 0.5) * 680 / cols
            y = cy - 94 + i // cols * 119
            p = st.floor(x, y, 50)
            instrument(st, p, kind, state, f"{bank}-{i}")
            st.marker(f"{bank}-{i}", offset(p, dz=25))
        # Physical keyboard and grille identify two copies of the same synth.
        for i in range(18):
            st.box(st.floor(194 + i * 35, cy + 130, 47), (31, 64, 12), "ivory", 3)
            if i % 7 not in (2, 6) and i < 17:
                st.box(st.floor(211 + i * 35, cy + 113, 59), (18, 39, 14), "rubber", 2)
        for k in range(5):
            st.box(st.floor(485 + k * 32, cy - 158, 43), (23, 5, 3), "rubber", 2)
        for x in (865, 900):
            st.line(
                [
                    st.floor(x, cy - 113, 16),
                    st.floor(x + 53, cy - 163, 17),
                    st.floor(1010, cy - 189, 0),
                    st.floor(1150, cy - 340, -20),
                ],
                6,
                "ink",
            )


def radial_profile(bits, r):
    coords = []
    for i, value in enumerate(bits):
        for f, m in [
            (0, 1),
            (0.13, 1),
            (0.18, 1 + 0.34 * value),
            (0.73, 1 + 0.34 * value),
            (0.78, 1),
            (0.99, 1),
        ]:
            a = math.tau * (i + f) / len(bits) - math.pi / 2
            coords.append([r * m * math.cos(a), r * m * math.sin(a)])
    return coords


def fit(st, s):
    b = s.board
    floor_detail(st, "slate", s.edition)
    target = st.floor(508, 872, 51)
    st.cyl(offset(target, dz=-42), 360, 50, "jade", 96, 14)
    st.cyl(offset(target, dz=-18), 285, 35, "nickel", 96, 8)
    st.cyl(offset(target, dz=1), 217, 7, "rubber", 96, 2)
    hole = radial_profile(b["socket"], 85)
    outer = [[204 * math.cos(math.atan2(y, x)), 204 * math.sin(math.atan2(y, x))] for x, y in hole]
    st.solid(offset(target, dz=14), outer, 25, "copper", 2, "die", hole=hole)
    # The dark floor and raised matching contour are the actual void in an annular mesh.
    for i in range(8):
        a = i * math.tau / 8
        st.screw(*offset(target, 242 * math.cos(a), 242 * math.sin(a), 4), r=12)
    for x in (66, 948):
        st.box(st.floor(x, 819, 0), (71, 775, 87), "jade", 19)
        st.box(st.floor(x, 821, 46), (19, 658, 16), "nickel", 7)
    st.box(st.floor(510, 1368, -2), (891, 248, 44), "oak", 17)
    for i, bits in enumerate(b["parts"]):
        p = st.floor(242 + i * 264, 1368, 54)
        st.cyl(offset(p, dz=-27), 121, 16, "rubber")
        st.sprite(f"insert-{i}", p, 122)
        st.solid(p, radial_profile(bits, 85), 28, "brass", 2, f"insert-{i}")
        st.ring(offset(p, dz=15), 47, 43, 4, "copper")
        st.cyl(offset(p, dz=17), 20, 7, "ink")
        st.group = None
    st.marker("socket", target)


def tower_layout(index, width):
    return [218, 502, 786][index], 1346, 43 if width == 4 else 51


def shadow(st, s):
    b = s.board
    floor_detail(st, "aubergine", s.edition)
    # Stage wings and pleated velvet; a warm projection screen mounted in a gilt arch.
    for side in (-1, 1):
        for j in range(5):
            x = 509 + side * (481 + j * 35)
            st.cyl(st.floor(x, 974, 58), 42, 141, "velvet", 32, 5)
            st.box(st.floor(x, 967, 22), (40, 1730, 67), "velvet", 18)
    c = st.floor(503, 819, 30)
    st.box(c, (773, 486 / st.cos, 46), "brass", 49)
    st.box(offset(c, dz=25), (739, 452 / st.cos, 22), "honey", 31)
    profile = b["screen"]
    unit = 66
    bottom = 991
    for x, h in enumerate(profile):
        p = st.floor(503 + (x - (len(profile) - 1) / 2) * unit, bottom - h * unit / 2, 72)
        st.box(p, (unit + 0.5, h * unit / st.cos, 4), "charcoal", 0, tag=f"shadow-col-{x}")
    st.marker("screenbase", st.floor(503, bottom, 72))
    for i, tower in enumerate(b["towers"]):
        cx, cy, unit = tower_layout(i, len(profile))
        p = st.floor(cx, cy, 16)
        st.cyl(offset(p, dz=-8), 122, 40, "oak", 56, 5)
        st.ring(offset(p, dz=14), 120, 111, 7, "brass")
        yaw = math.radians(-15)
        for row, heights in enumerate(tower):
            for col, h in enumerate(heights):
                dx = (col - (len(heights) - 1) / 2) * unit
                # Row 0 is nearest the viewer.
                dy = (0.5 - row) * unit
                bx = dx * math.cos(yaw) - dy * math.sin(yaw)
                by = dx * math.sin(yaw) + dy * math.cos(yaw)
                for z in range(h):
                    pos = offset(p, bx, by, 20 + (z + 0.5) * unit)
                    st.box(
                        pos,
                        (unit - 0.6, unit - 0.6, unit - 0.6),
                        ("mint", "ivory", "rose")[i],
                        2,
                        -15,
                        f"voxel-{i}-{row}-{col}-{z}",
                    )
        st.marker(f"tower-{i}", p)
    for i in range(13):
        st.cyl(st.floor(105 + i * 66, 1485, 32), 9, 10, "lume", 20)
