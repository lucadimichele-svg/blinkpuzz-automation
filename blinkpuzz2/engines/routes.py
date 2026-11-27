from blinkpuzz2.core import LETTERS, Engine, Outcome, require

# Three entry stops, then two junctions. Arrows always run left to right.
ENTRY = {"SA", "SB", "SC", "UX", "VX"}
FANS = [
    ("AU", "AV", "BV", "CV"),
    ("AU", "BV", "CV"),
    ("AU", "BU", "BV", "CV"),
    ("AU", "BU", "CV"),
    ("AU", "BU", "CU", "CV"),
]


def propose(rng, level):
    links = ENTRY | set(rng.choice(FANS))
    return {
        "roads": {edge: rng.randint(1, 4 + 2 * level) for edge in sorted(links)},
        "heights": [rng.randrange(235, 390, 10), rng.randrange(235, 390, 10)],
    }


def solve(b):
    edges = b["roads"]
    require(
        any(set(edges) == ENTRY | set(fan) for fan in FANS)
        and all(type(w) is int and 1 <= w <= 9 for w in edges.values()),
        "Invalid route map",
    )
    require(
        len(b["heights"]) == 2 and all(type(h) is int and 235 <= h < 390 for h in b["heights"]),
        "Invalid terminus",
    )
    paths = []

    def visit(route, cost):
        if route[-1] == "X":
            paths.append([route, cost])
        for edge, weight in sorted(edges.items()):
            if edge[0] == route[-1]:
                visit(route + edge[1], cost + weight)

    visit("S", 0)
    require({r[1] for r, cost in paths} == set(LETTERS), "Unreachable entry option")
    optimum = min(cost for r, cost in paths)
    best = [r for r, cost in paths if cost == optimum]
    return Outcome(
        [r[1] for r in best],
        {"paths": paths, "best": best, "cost": optimum},
        3,
        len(paths),
        f"The highlighted trip costs {optimum}, the lowest total.",
    )


ENGINE = Engine(
    "routes",
    "Which first stop costs least?",
    ("Travel left to right, from S to X.", "Add the three fares along your trip."),
    ("ruins", "editorial"),
    ("roads", "heights"),
    propose,
    solve,
)
