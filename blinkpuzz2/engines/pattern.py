from blinkpuzz2.core import LETTERS, Engine, Outcome, choices, require, triplet


def propose(rng, level):
    cells = set(rng.sample(range(9), 3 + level))

    def rotate(shape):
        return {3 * (p % 3) + 2 - p // 3 for p in shape}

    stages = [cells]
    for _ in range(3):
        stages.append(rotate(stages[-1]))
    pack = lambda s: "".join("1" if i in s else "0" for i in range(9))
    tiles = [pack(s) for s in stages]
    if len(set(tiles)) < 4:
        return None
    near = [
        pack((stages[2] - {p}) | {q})
        for p in sorted(stages[2])
        for q in range(9)
        if q not in stages[2]
    ]
    return {"sequence": tiles[:2], "tiles": choices(rng, tiles[2], near)}


def solve(b):
    shown, tiles = b["sequence"], b["tiles"]
    triplet(tiles)
    require(
        len(shown) == 2
        and all(
            isinstance(s, str) and len(s) == 9 and set(s) == {"0", "1"} for s in [*shown, *tiles]
        ),
        "Invalid mosaic",
    )

    def turn(s):
        return "".join(s[(2 - col) * 3 + row] for row in range(3) for col in range(3))

    require(
        turn(shown[0]) == shown[1] and turn(shown[1]) != shown[0], "Broken or symmetric sequence"
    )
    target = turn(shown[1])
    return Outcome(
        [LETTERS[i] for i, t in enumerate(tiles) if t == target],
        {"sequence": [*shown, target], "source_indices": [6, 3, 0, 7, 4, 1, 8, 5, 2]},
        2,
        3,
        "The marked cells all move one quarter-turn clockwise.",
    )


ENGINE = Engine(
    "pattern",
    "Which tile comes next?",
    ("Rotate the whole tile 90° clockwise", "at every step."),
    ("editorial", "arcade"),
    ("sequence", "tiles"),
    propose,
    solve,
)
