from blinkpuzz2.core import LETTERS, Engine, Outcome, choices, point, require, triplet

PORTS = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
BACK = dict(zip("NESW", "SWNE"))
TILES = ("EW", "NS", "EN", "ES", "NW", "SW")


def propose(rng, level):
    n = 4 + (level == 2)
    start = rng.randrange(n)
    path = [(-1, start)]
    y = start
    for x in range(n):
        path.append((x, y))
        dest = rng.randrange(n) if rng.random() < 0.72 else y
        while y != dest:
            y += 1 if dest > y else -1
            path.append((x, y))
    path.append((n, y))
    grid = [[rng.choice(TILES) for _ in range(n)] for _ in range(n)]
    gap = rng.choice([p for p in path if 0 < p[0] < n - 1])
    for a, p, z in zip(path, path[1:], path[2:]):
        tile = "".join(
            sorted(d for d, (dx, dy) in PORTS.items() if (p[0] + dx, p[1] + dy) in (a, z))
        )
        grid[p[1]][p[0]] = tile
    options = choices(rng, grid[gap[1]][gap[0]], TILES)
    grid[gap[1]][gap[0]] = "?"
    return {"grid": grid, "gap": list(gap), "inlet": start, "outlet": y, "pieces": options}


def solve(b):
    grid = b["grid"]
    n = len(grid)
    require(n in (4, 5) and all(len(row) == n for row in grid), "Invalid pipe board size")
    gap = point(b["gap"], n)
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            require(tile == "?" if (x, y) == gap else tile in TILES, "Bad pipe tile")
    triplet(b["pieces"])
    require(all(t in TILES for t in b["pieces"]), "Bad spare")
    require(all(type(b[k]) is int and 0 <= b[k] < n for k in ("inlet", "outlet")), "Bad pipe ports")
    winners, paths = [], {}
    for label, piece in zip(LETTERS, b["pieces"]):
        x, y, incoming = 0, b["inlet"], "W"
        path = []
        while 0 <= x < n and 0 <= y < n and [x, y] not in path:
            tile = piece if (x, y) == gap else grid[y][x]
            if incoming not in tile:
                break
            path.append([x, y])
            direction = tile.replace(incoming, "")
            dx, dy = PORTS[direction]
            x, y, incoming = x + dx, y + dy, BACK[direction]
        if (x, y) == (n, b["outlet"]) and list(gap) in path:
            winners.append(label)
        paths[label] = path
    return Outcome(
        winners,
        {"traces": paths},
        len(paths[winners[0]]) if winners else 0,
        3,
        "The fitted section completes an unbroken pipe.",
    )


ENGINE = Engine(
    "pipes",
    "Which piece fixes the leak?",
    ("Join IN to OUT through the gap.", "Use a piece exactly as shown."),
    ("workshop", "arcade"),
    ("grid", "gap", "inlet", "outlet", "pieces"),
    propose,
    solve,
    5,
)
