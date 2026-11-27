from collections import deque

from blinkpuzz2.core import LETTERS, Engine, Outcome, point, require, triplet

from .maze import DIRS


def propose(rng, level):
    n = 5
    cells = [tuple(rng.randrange(n) for _ in range(2))]
    target = 8 + level * 2
    while len(cells) < target:
        x, y = rng.choice(cells)
        dx, dy = rng.choice(DIRS)
        q = x + dx, y + dy
        if q not in cells and all(0 <= v < n for v in q):
            cells.append(q)
    return {
        "wheels": [list(p) for p in cells],
        "drive": list(cells[0]),
        "marked": [list(p) for p in rng.sample(cells[1:], 3)],
    }


def solve(b):
    cells = {point(p, 5) for p in b["wheels"]}
    require(len(cells) == len(b["wheels"]) and 6 <= len(cells) <= 16, "Invalid wheel set")
    drive = point(b["drive"], 5)
    triplet(b["marked"])
    marks = [point(p, 5) for p in b["marked"]]
    require(drive in cells and drive not in marks and set(marks) <= cells, "Bad gear labels")
    turns, depth, queue = {drive: 1}, {drive: 0}, deque([drive])
    while queue:
        p = queue.popleft()
        for dx, dy in DIRS:
            q = p[0] + dx, p[1] + dy
            if q in cells and q not in turns:
                turns[q], depth[q] = -turns[p], depth[p] + 1
                queue.append(q)
            if q in cells:
                require(turns[q] == -turns[p], "Locked gear train")
    require(set(turns) == cells, "Disconnected gear")
    winners = [LETTERS[i] for i, p in enumerate(marks) if turns[p] == 1]
    steps = depth[marks[LETTERS.index(winners[0])]] if winners else 0
    return Outcome(
        winners,
        {"directions": [[*p, turns[p], depth[p]] for p in sorted(cells)]},
        steps,
        len(cells) - 1,
        "Each contact reverses the turn. An even count matches the drive.",
    )


ENGINE = Engine(
    "gears",
    "Which gear turns clockwise?",
    ("The drive turns clockwise.", "Touching gears turn opposite ways."),
    ("workshop", "ruins"),
    ("wheels", "drive", "marked"),
    propose,
    solve,
)
