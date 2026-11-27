from itertools import combinations_with_replacement, product

from blinkpuzz2.core import LETTERS, Engine, Outcome, require, triplet

SHAPES = "CDT"
LOADS = ["".join(p) for n in range(1, 4) for p in combinations_with_replacement(SHAPES, n)]


def mass(load, weights):
    return sum(weights[SHAPES.index(c)] for c in load)


def propose(rng, level):
    weights = rng.sample(range(1, 7), 3)
    groups = {}
    for load in LOADS:
        groups.setdefault(mass(load, weights), []).append(load)
    equals = [
        (a, b)
        for loads in groups.values()
        for a in loads
        for b in loads
        if a < b and not set(a) & set(b) and len(a) + len(b) <= 4 + int(level > 0)
    ]
    if len(equals) < 3:
        return None
    first, second, query = rng.sample(equals, 3)
    target, right = rng.sample(query, 2)
    near = [s for s in LOADS if 0 < abs(mass(s, weights) - mass(target, weights)) <= 4]
    options = [right, *rng.sample(near, 2)]
    rng.shuffle(options)
    return {"scales": [list(first), list(second)], "target": target, "loads": options}


def solve(b):
    eqs, target, loads = b["scales"], b["target"], b["loads"]
    triplet(loads)
    require(
        len(eqs) == 2
        and all(len(eq) == 2 and eq[0] != eq[1] for eq in eqs)
        and all(s in LOADS for s in [*(s for eq in eqs for s in eq), target, *loads])
        and target not in loads,
        "Invalid or trivial scales",
    )
    models = [
        w for w in product(range(1, 7), repeat=3) if all(mass(a, w) == mass(z, w) for a, z in eqs)
    ]
    require(models, "Contradictory scales")
    matches = [
        [LETTERS[i] for i, l in enumerate(loads) if mass(l, w) == mass(target, w)] for w in models
    ]
    require(all(m == matches[0] for m in matches), "Possible masses disagree")
    # Both clues must contribute to the equality, even without the distractors.
    if len(matches[0]) == 1:
        win = loads[LETTERS.index(matches[0][0])]
        for a, z in eqs:
            require(
                any(
                    mass(a, w) == mass(z, w) and mass(target, w) != mass(win, w)
                    for w in product(range(1, 7), repeat=3)
                ),
                "One scale gives away the answer",
            )
    return Outcome(
        matches[0],
        {"models_CDT": [list(w) for w in models], "matching_loads": matches[0]},
        2,
        len(models),
        "This load balances for every mass allowed by both scales.",
    )


ENGINE = Engine(
    "balance",
    "Which load balances the pan?",
    ("Both scales balance. Each shape has a", "fixed whole-number weight from 1 to 6."),
    ("desk", "workshop"),
    ("scales", "target", "loads"),
    propose,
    solve,
)
