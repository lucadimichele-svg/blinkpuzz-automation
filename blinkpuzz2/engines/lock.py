from itertools import permutations

from blinkpuzz2.core import LETTERS, Engine, Outcome, require, triplet

TOKENS = "KMSF"
NAMES = {"K": "Key", "M": "Moon", "S": "Star", "F": "Fish"}
ORDERS = ["".join(p) for p in permutations(TOKENS)]


def matches(order, clue):
    op, a, b = clue
    if op == "first":
        return order[0] == a
    if op == "before":
        return order.index(a) < order.index(b)
    if op == "beside":
        return abs(order.index(a) - order.index(b)) == 1
    return order.index(b) - order.index(a) == 1


def describe(clue):
    op, a, b = clue
    if op == "first":
        return NAMES[a] + " is first."
    verb = {"before": " is before ", "beside": " is beside ", "left": " is just left of "}[op]
    return NAMES[a] + verb + NAMES[b] + "."


def propose(rng, level):
    order = rng.choice(ORDERS)
    pool = [["first", order[0], ""]] if level < 2 else []
    for i, a in enumerate(order):
        for j, b in enumerate(order[i + 1 :], i + 1):
            pool.append(["before", a, b])
            if j == i + 1:
                pool.extend([["beside", *sorted([a, b])], ["left", a, b]])
    clues = rng.sample(pool, 3)
    near = [p for p in ORDERS if sum(matches(p, c) for c in clues) == 2]
    if len(near) < 2:
        return None
    choices = [order, *rng.sample(near, 2)]
    rng.shuffle(choices)
    return {"clues": clues, "orders": choices}


def solve(b):
    clues = b["clues"]
    require(len(clues) == 3, "Three notes required")
    for op, a, z in clues:
        require(
            a in NAMES
            and (
                (op == "first" and z == "")
                or (op in ("before", "beside", "left") and z in NAMES and a != z)
            ),
            "Invalid clue",
        )
    triplet(b["orders"])
    require(all(s in ORDERS for s in b["orders"]), "Invalid lock strip")
    checks = {p: [matches(p, c) for c in clues] for p in ORDERS}
    valid = [p for p, row in checks.items() if all(row)]
    require(len(valid) == 1, "Contradictory or underdetermined notes")
    require(
        all(any(not row[i] and sum(row) == 2 for row in checks.values()) for i in range(3)),
        "Redundant evidence",
    )
    return Outcome(
        [LETTERS[i] for i, p in enumerate(b["orders"]) if p in valid],
        {
            "valid_order": valid[0],
            "candidate_checks": [checks[p] for p in b["orders"]],
            "orders_tested": 24,
        },
        3,
        24,
        "Only this strip satisfies all three notes.",
    )


ENGINE = Engine(
    "lock",
    "Which strip opens the lock?",
    ("Read each strip from left to right.", "All three notes must fit."),
    ("desk", "editorial"),
    ("clues", "orders"),
    propose,
    solve,
)
