"""Axonometric masonry and a roofless maze viewed from above the southwest corner."""

from blinkpuzz2.core import LETTERS


def ruin_maze(s, b, proof, winner, p):
    n = b["size"]
    sx, sy = 324 / n, 218 / n

    def vertex(x, y):
        return 419 + (x - y) * sx, 95 + (x + y) * sy

    def center(x, y):
        return vertex(x + 0.5, y + 0.5)

    d = s.d
    corners = [vertex(0, 0), vertex(n, 0), vertex(n, n), vertex(0, n)]
    d.polygon([(x, y + 22) for x, y in corners], fill="#987d5b")
    d.polygon(corners, fill="#e9d4ab", outline=s.ink, width=3)
    openings = {frozenset((tuple(a), tuple(z))) for a, z in b["passages"]}
    starts = {tuple(pt) for pt in b["entrances"]}
    end = tuple(b["exit"])
    for a in range(1, n):
        s.path([vertex(a, 0), vertex(a, n)], "#d7be95", 2)
        s.path([vertex(0, a), vertex(n, a)], "#d7be95", 2)
    if p:
        route = proof["path"][: max(2, round(len(proof["path"]) * p))]
        s.path([center(*pt) for pt in route], s.accent, 9)
    walls = []
    for y in range(n):
        for x in range(n):
            adj = [((x - 1, y), (x, y), (x, y + 1)), ((x, y - 1), (x, y), (x + 1, y))]
            if x == n - 1 and (x, y) != end:
                adj.append(((x + 1, y), (x + 1, y), (x + 1, y + 1)))
            if y == n - 1:
                adj.append(((x, y + 1), (x, y + 1), (x + 1, y + 1)))
            for q, a, z in adj:
                if q[0] < 0 and (x, y) in starts or frozenset(((x, y), q)) in openings:
                    continue
                walls.append((sum(a) + sum(z), vertex(*a), vertex(*z)))
    for _, a, z in sorted(walls):
        top = [(a[0], a[1] - 14), (z[0], z[1] - 14)]
        d.polygon([a, z, top[1], top[0]], fill="#617b74", outline=s.ink, width=2)
        s.path(top, "#243f40", 8)
        s.path([(x, y - 2) for x, y in top], "#c4b28c", 3)
    for label, pt in zip(LETTERS, b["entrances"]):
        xx, yy = vertex(-0.55, pt[1] + 0.5)
        s.label(xx, yy - 12, label, bool(p and label == winner), 22)
    xx, yy = vertex(n + 0.20, end[1] + 0.5)
    s.path([(xx, yy), (xx, yy - 45)], s.ink, 5)
    d.polygon([(xx, yy - 45), (xx + 35, yy - 37), (xx, yy - 24)], fill=s.accent)


def cabinet(d, w, cover):
    """Build a molded cabinet around the entire playing surface."""
    d.rounded_rectangle((41, 241, 1035, 1641), 96, fill="#271838", outline="#b299c8", width=9)
    d.rounded_rectangle((63, 260, 1014, 1619), 77, fill="#62426f", outline="#885e8b", width=7)
    for x in (76, 984):
        for y in range(400, 1390, 35):
            d.ellipse((x, y, x + 9, y + 9), fill="#38243e")
    d.polygon(
        [(62, 1556), (1012, 1556), (1076, 1789), (6, 1789)],
        fill="#6b4980",
        outline="#24182e",
        width=6,
    )
    for x, y, c in [(174, 1663, "#f78482"), (818, 1650, "#b7f6d0"), (925, 1708, "#f4cd81")]:
        d.ellipse((x - 40, y - 27, x + 40, y + 42), fill="#392847")
        d.ellipse((x - 36, y - 32, x + 36, y + 24), fill=c, outline="#fae4cb", width=4)
    d.line((170, 1703, 151, 1642), fill="#291c38", width=17)
    d.ellipse((120, 1600, 181, 1661), fill="#ec8586", outline="#f7d7c3", width=4)


def folio(d, w):
    d.polygon([(44, 281), (977, 230), (1025, 1573), (84, 1640)], fill="#311f29")
    d.polygon([(36, 259), (965, 218), (1014, 1557), (78, 1624)], fill="#e5cba1")
    d.line((94, 314, 140, 1540), fill="#af836d", width=3)
    d.polygon([(787, 221), (871, 216), (877, 331), (839, 312), (800, 337)], fill="#963b36")
