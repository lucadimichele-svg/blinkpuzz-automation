"""Physical sets for the four returning game families."""

import math

from blinkpuzz2.engines.pipes import PORTS

from .stage import beam_box, circle, grid, grid_pose, offset


def floor_detail(st, material, ed):
    st.box((540, 960, -92), (3600, 6400, 120), material, 10)
    if st.family == "laser":
        for x in (35, 1039):
            for y in range(20, 2000, 134):
                st.box((x, y, -22), (52, 115, 22), "ink", 8)
                st.screw(x, y, -8, 6)
    elif st.family in ("search", "gears"):
        # Long-grain joinery and a band of inlaid veneer.
        for x in (-80, 64, 277, 660, 985):
            st.box((x, 960, -29), (3, 4800, 6), "oak", 1)
    elif st.family == "maze":
        for i in range(22):
            x = (194 * i + 71 * ed) % 1135 - 45
            y = (331 * i + 54 * ed) % 2200
            st.line(
                [st.floor(x, y, -29), st.floor(x + 35, y + 2, -29), st.floor(x + 66, y - 2, -29)],
                2,
                "ocean",
            )


def optic(st, s):
    b = s.board
    n = b["size"]
    ed = s.edition
    floor_detail(st, "ink", ed)
    hub = st.floor(505, 960, -10)
    for width, length, h, mat in [
        (998, 978, 34, "nickel"),
        (976, 954, 39, "ink"),
        (920, 905, 43, "slate"),
    ]:
        st.box(hub, (width, length, h), mat, 44)
    for side in (-1, 1):
        for i in range(37):
            px = hub[0] - 401 + i * 22
            py = hub[1] + side * 426
            st.box((px, py, 15), (2, 13 if i % 4 == 0 else 6, 2), "ivory", 0.5)
        st.line(
            [
                st.floor(510 + side * 404, 1460),
                st.floor(510 + side * 445, 1520),
                st.floor(510 + side * 456, 1617),
                st.floor(510 + side * 308, 1645),
            ],
            9,
            "rubber",
        )
    for x in range(n):
        for y in range(n):
            cell = grid(s, st, x, y, 14)
            st.cyl(cell, 5, 7, "rubber", 12, 0)
    for x, y, slope in b["mirrors"]:
        a, z = (-0.34, 0.34) if slope == "/" else (-0.34, -0.34)
        start = grid(s, st, x + a, y + z, 38)
        end = grid(s, st, x - a, y - z, 38)
        st.cyl(grid(s, st, x, y, 20), 43, 14, "ink")
        beam_box(st, start, end, 16, 32, "nickel", f"mirror-{x}-{y}")
        beam_box(st, offset(start, dz=18), offset(end, dz=18), 7, 4, "lume")
        for p in [start, end]:
            st.cyl(offset(p, dz=6), 8, 30, "brass", 20)
    for i, (x, y) in enumerate(b["receivers"]):
        p = grid(s, st, x, y, 22)
        st.cyl(p, 49, 17, "ink")
        st.ring(offset(p, dz=10), 44, 38, 7, "nickel")
        m = ("orange", "turquoise", "rose")[i]
        sides = (3, 4, 6)[i]
        st.solid(offset(p, dz=35), circle(39, sides), 46, m, 8, f"receiver-{i}")
        st.solid(offset(p, dz=60), circle(24, sides), 6, "honey" if i == 0 else "lume", 2)
    y = b["emitter_row"]
    p = grid(s, st, -0.20, y, 34)
    beam_box(st, grid(s, st, -0.62, y, 30), p, 47, 42, "brass", "emitter")
    for step in (-0.49, -0.39, -0.29):
        beam_box(
            st, grid(s, st, step - 0.015, y, 32), grid(s, st, step + 0.015, y, 32), 55, 49, "ink"
        )
    st.markers["ray"] = [st.screen(grid(s, st, x, y, 45)) for x, y in s.proof["path"]]
    st.marker("muzzle", p)
    st.marker("receiver", grid(s, st, *b["receivers"][s.proof["slot"]], 65))


def wall_edges(n):
    for x in range(n + 1):
        for y in range(n):
            yield (x - 1, y), (x, y), (x - 0.5, y - 0.5), (x - 0.5, y + 0.5)
    for y in range(n + 1):
        for x in range(n):
            yield (x, y - 1), (x, y), (x - 0.5, y - 0.5), (x + 0.5, y - 0.5)


def maze(st, s):
    b = s.board
    n = b["size"]
    floor_detail(st, "ocean", s.edition)
    pitch = grid_pose(s)[2]
    ang = grid_pose(s)[3]
    center = grid(s, st, (n - 1) / 2, (n - 1) / 2, -8)
    st.box(center, (n * pitch + 35, n * pitch + 35, 60), "sand", 9, ang)
    st.box(offset(center, dz=33), (n * pitch, n * pitch, 12), "ocean", 6, ang)
    passages = {frozenset((tuple(a), tuple(z))) for a, z in b["passages"]}
    gates = {tuple(p) for p in b["entrances"]}
    for a, z, aa, zz in wall_edges(n):
        if (
            frozenset((a, z)) in passages
            or (a[0] == -1 and z in gates)
            or (z[0] == n and a == tuple(b["exit"]))
        ):
            continue
        p, q = grid(s, st, *aa, 49), grid(s, st, *zz, 49)
        tag = f"wall-{aa[0]},{aa[1]}-{zz[0]},{zz[1]}"
        beam_box(st, p, q, 18, 44, "stone", tag)
        for frac in (0.22, 0.73):
            v = [i + (j - i) * frac for i, j in zip(p, q)]
            st.box(
                offset(v, dz=25),
                (pitch * 0.43, 22, 8) if aa[0] != zz[0] else (22, pitch * 0.43, 8),
                "ivory",
                2,
                ang,
            )
    for i, (x, y) in enumerate(b["entrances"]):
        p = grid(s, st, -0.74, y, 21)
        st.cyl(p, 25, 18, "brass")
        st.label(str(i + 1), offset(p, dz=10), 33)
    x, y = b["exit"]
    finish = grid(s, st, x + 0.65, y, 35)
    st.cyl(finish, 16, 38, "stone")
    st.line([finish, offset(finish, dz=120)], 4, "ivory")
    st.solid(offset(finish, dx=20, dz=102), [[-19, -13], [32, -2], [-19, 15]], 15, "red", 2)
    for i in range(7):
        p = st.floor(50 + i * 163, 1615 + 30 * math.sin(i), -4)
        st.cyl(p, 48 + (i % 3) * 12, 80, "sand", 7, 7)
        st.cyl(offset(p, dz=40), 38, 10, "stone", 7, 3)
    st.markers["route"] = [st.screen(grid(s, st, *p, 35)) for p in s.proof["path"]]
    st.marker("flag", offset(finish, dz=105))


def pipe_path(center, tile, radius):
    d1, d2 = (PORTS[c] for c in tile)
    x, y, z = center
    # Quadratic fillet, with tangent stubs that meet the adjacent tile exactly.
    start = offset(center, d1[0] * radius, d1[1] * radius)
    end = offset(center, d2[0] * radius, d2[1] * radius)
    a = offset(center, d1[0] * radius * 0.49, d1[1] * radius * 0.49)
    zpt = offset(center, d2[0] * radius * 0.49, d2[1] * radius * 0.49)
    return [
        start,
        *[
            [(1 - t) ** 2 * a[j] + 2 * t * (1 - t) * center[j] + t * t * zpt[j] for j in range(3)]
            for t in (0, 0.2, 0.4, 0.6, 0.8, 1)
        ],
        end,
    ]


def spool(st, p, tile, r, tag, mat):
    pts = pipe_path(p, tile, r)
    st.line(pts, 15, mat, tag)
    for dx, dy in [PORTS[c] for c in tile]:
        a = offset(p, dx * r * 0.79, dy * r * 0.79)
        z = offset(p, dx * r * 0.92, dy * r * 0.92)
        st.line([a, z], 19, "brass")
    return pts


def pipes(st, s):
    b = s.board
    n = len(b["grid"])
    pitch = grid_pose(s)[2]
    r = pitch / 2
    floor_detail(st, "jade", s.edition)
    center = st.floor(503, 892, -6)
    st.box(center, (n * pitch + 45, n * pitch + 65, 42), "turquoise", 37)
    for x in (57, 976):
        st.line([st.floor(x, 300), st.floor(x, 1600)], 28, "copper")
        for y in [420, 1080, 1450]:
            st.box(st.floor(x, y, 12), (73, 24, 22), "brass")
    for y, row in enumerate(b["grid"]):
        for x, tile in enumerate(row):
            p = grid(s, st, x, y, 41)
            if tile == "?":
                st.box(offset(p, dz=-17), (pitch * 0.88, pitch * 0.88, 14), "ink", 18)
                st.label("?", offset(p, dz=3), 46)
                st.marker("gap", p)
            else:
                spool(st, p, tile, r, f"pipe-{x}-{y}", "ivory")
    for side, row in [(-0.65, b["inlet"]), (n - 0.35, b["outlet"])]:
        p = grid(s, st, side, row, 44)
        st.cyl(p, 31, 47, "brass")
        st.label("IN" if side < 0 else "OUT", offset(p, dz=30), 32)
    for i, tile in enumerate(b["pieces"]):
        p = st.floor(252 + 249 * i, 1383, 40)
        st.cyl(offset(p, dz=-37), 92, 35, "rubber")
        st.ring(offset(p, dz=-17), 90, 84, 6, "brass")
        st.sprite(f"spare-{i}", p, 103)
        spool(st, p, tile, r, f"spare-geometry-{i}", "orange")
        st.group = None
    cells = s.proof["traces"]["ABC"[s.proof["slot"]]]
    walk = [[-1, b["inlet"]], *cells, [n, b["outlet"]]]
    flow = []
    for a, p, z in zip(walk, walk[1:], walk[2:]):
        directions = [
            next(d for d, v in PORTS.items() if tuple(v) == (q[0] - p[0], q[1] - p[1]))
            for q in (a, z)
        ]
        pts = pipe_path(grid(s, st, *p, 57), directions, r)
        flow.extend(st.screen(pt) for pt in pts)
    st.markers["water"] = flow


def gear_outline(r):
    points = []
    for i in range(16):
        for frac, rad in [(0, 0.88), (0.16, 0.88), (0.27, 1), (0.54, 1), (0.68, 0.88)]:
            a = (i + frac) * math.tau / 16
            points.append([r * rad * math.cos(a), r * rad * math.sin(a)])
    return points


def gears(st, s):
    b = s.board
    ed = s.edition
    floor_detail(st, "walnut", ed)
    c = st.floor(505, 950, -6)
    st.cyl(c, 520, 43, "brass", 96, 8)
    st.cyl(offset(c, dz=22), 493, 19, "ink", 96)
    for r in (464, 478, 504):
        st.ring(offset(c, dz=34), r, r - 4, 4, "copper")
    for i in range(60):
        a = i * math.tau / 60
        st.box(
            offset(c, math.cos(a) * 448, math.sin(a) * 448, 37),
            (18 if i % 5 == 0 else 8, 3, 3),
            "ivory",
            1,
            math.degrees(a),
        )
    for x, y, sign, depth in s.proof["directions"]:
        p = grid(s, st, x, y, 54)
        key = f"gear-{x}-{y}"
        drive = [x, y] == b["drive"]
        output = [x, y] == b["output"]
        st.cyl(offset(p, dz=-13), 26, 27, "rubber")
        st.sprite(key, p, 84)
        profile = gear_outline(79)
        phase = (math.pi / 16 if sign < 0 else 0) + math.radians(grid_pose(s)[3])
        profile = [
            [u * math.cos(phase) - v * math.sin(phase), u * math.sin(phase) + v * math.cos(phase)]
            for u, v in profile
        ]
        st.solid(p, profile, 15, "red" if output else "turquoise" if drive else "brass", 2, key)
        st.ring(offset(p, dz=10), 62, 57, 4, "nickel" if drive else "copper")
        for i in range(5):
            a = phase + i * math.tau / 5
            st.cyl(offset(p, 42 * math.cos(a), 42 * math.sin(a), 10), 11, 3, "ink", 24, 1)
        st.cyl(offset(p, dz=13), 20, 10, "ivory" if drive or output else "nickel")
        st.line([offset(p, 4, 0, 20), offset(p, 30, 0, 20)], 3, "ink")
        if output:
            st.ring(offset(p, dz=20), 16, 11, 3, "red")
        st.group = None
        if drive:
            st.marker("driver", p)
        if output:
            st.marker("output", p)
