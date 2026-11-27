"""A finite ray reflects off diagonal mirrors until it reaches a receiver or exits."""

from blinkpuzz2.core import LETTERS, Engine, Outcome, point, require, triplet


def propose(rng, level):
    n = 5 + (level == 2)
    y = rng.randrange(n)
    cells = [(x, r) for x in range(n) for r in range(n) if (x, r) != (0, y)]
    sites = rng.sample(cells, 7 + 2 * level)
    return {
        "size": n,
        "emitter_row": y,
        "mirrors": [[x, r, rng.choice(["/", "\\"])] for x, r in sites[3:]],
        "receivers": [list(p) for p in sites[:3]],
    }


def solve(b):
    n, row = b["size"], b["emitter_row"]
    require(type(n) is int and n in (5, 6) and type(row) is int and 0 <= row < n, "Invalid emitter")
    triplet(b["receivers"])
    targets = [point(p, n) for p in b["receivers"]]
    mirrors = {}
    for x, y, slope in b["mirrors"]:
        p = point([x, y], n)
        require(p not in mirrors and p not in targets and slope in ("/", "\\"), "Bad mirror")
        mirrors[p] = slope
    require((0, row) not in targets and (0, row) not in mirrors, "Obstructed emitter")
    x, y, dx, dy = 0, row, 1, 0
    visited, path, bends = set(), [], 0
    while 0 <= x < n and 0 <= y < n and (x, y, dx, dy) not in visited:
        visited.add((x, y, dx, dy))
        path.append([x, y])
        if (x, y) in targets:
            winner = LETTERS[targets.index((x, y))]
            require(bends >= 2, "Ray needs at least two reflections")
            return Outcome(
                [winner],
                {"path": path, "reflections": bends},
                len(path),
                len(mirrors),
                f"{bends} reflections lead to receiver {winner}.",
            )
        if (x, y) in mirrors:
            bends += 1
            if mirrors[x, y] == "/":
                dx, dy = -dy, -dx
            else:
                dx, dy = dy, dx
        x, y = x + dx, y + dy
    return Outcome([], {"path": path}, len(path), len(mirrors), "Ray misses the receivers.")


ENGINE = Engine(
    "laser",
    "Which crystal lights up?",
    ("Trace the beam from the arrow.", "Each mirror turns it 90°."),
    ("lab", "arcade"),
    ("size", "emitter_row", "mirrors", "receivers"),
    propose,
    solve,
)
