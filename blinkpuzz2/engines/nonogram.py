from itertools import groupby, product

from blinkpuzz2.core import LETTERS, Engine, Outcome, require, triplet


def runs(line):
    return [sum(1 for _ in values) for bit, values in groupby(line) if bit == "1"] or [0]


def propose(rng, level):
    n = 4
    pixels = ["".join(rng.choice("01") for _ in range(n)) for _ in range(n)]
    rows = [runs(r) for r in pixels]
    cols = [runs(c) for c in zip(*pixels)]
    if [0] in rows + cols or (level > 0 and [1, 1] not in rows + cols):
        return None
    # Preserve row clues in decoys so viewers must cross-check columns.
    flat = "".join(pixels)
    decoys = []
    for i in range(n):
        for line in product("01", repeat=n):
            if runs(line) == rows[i] and "".join(line) != pixels[i]:
                decoys.append("".join([*pixels[:i], "".join(line), *pixels[i + 1 :]]))
    if len(set(decoys)) < 2:
        return None
    tiles = [flat, *rng.sample(sorted(set(decoys)), 2)]
    rng.shuffle(tiles)
    return {"rows": rows, "columns": cols, "prints": tiles}


def solve(b):
    rows, cols = b["rows"], b["columns"]
    n = 4
    lines = ["".join(p) for p in product("01", repeat=n)]
    require(
        len(rows) == len(cols) == n and all(c in [runs(l) for l in lines] for c in rows + cols),
        "Invalid run lengths",
    )
    triplet(b["prints"])
    require(all(len(t) == 16 and set(t) <= {"0", "1"} for t in b["prints"]), "Invalid print")
    candidates = [[l for l in lines if runs(l) == clue] for clue in rows]
    valid, tested = [], 0
    for grid in product(*candidates):
        tested += 1
        if [runs(col) for col in zip(*grid)] == cols:
            valid.append("".join(grid))
    require(len(valid) == 1, "Run clues must determine the full image uniquely")
    return Outcome(
        [LETTERS[i] for i, p in enumerate(b["prints"]) if p == valid[0]],
        {"bitmap": valid[0], "row_compatible_boards": tested, "matching_boards": 1},
        n * 2,
        tested,
        "Every row and column has exactly the printed runs.",
    )


ENGINE = Engine(
    "nonogram",
    "Which print fits the grid?",
    ("Numbers count solid blocks in order.", "Separate each run by an empty square."),
    ("arcade", "desk"),
    ("rows", "columns", "prints"),
    propose,
    solve,
)
