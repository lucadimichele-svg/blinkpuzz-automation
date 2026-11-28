"""Public board proposals and answer-free oracles for the four new game families."""

import itertools
import math
from random import Random

from blinkpuzz2.core import require


def search_board(r: Random, edition):
    cols, rows = [(4, 3), (3, 4), (4, 4)][edition]
    target = [r.randrange(3), r.randrange(1, 4)]
    # Several near-matches share one identifying feature. Locations are independently jittered.
    kinds = [p for p in itertools.product(range(3), range(1, 4)) if list(p) != target]
    features = [target, *[list(r.choice(kinds)) for _ in range(cols * rows - 1)]]
    features[1] = [target[0], target[1] % 3 + 1]
    features[2] = [(target[0] + 1) % 3, target[1]]
    r.shuffle(features)
    bugs = []
    for i, (wing, spots) in enumerate(features):
        bugs.append([wing, spots, r.randint(-8, 8), r.randint(-8, 8), r.randint(-12, 12)])
    return {"shape": [cols, rows], "sample": target, "specimens": bugs}


def search_oracle(b):
    cols, rows = b["shape"]
    require(
        (cols, rows) in ((4, 3), (3, 4), (4, 4)) and len(b["specimens"]) == cols * rows,
        "Bad specimen drawer",
    )
    matches = []
    for i, (wing, spots, dx, dy, angle) in enumerate(b["specimens"]):
        require(
            wing in range(3)
            and spots in range(1, 4)
            and abs(dx) <= 8
            and abs(dy) <= 8
            and abs(angle) <= 12,
            "Obscured or invalid specimen",
        )
        if [wing, spots] == b["sample"]:
            matches.append(i)
    require(len(matches) == 1, "Sample must match one specimen")
    return {
        "answer": f"specimen-{matches[0]}",
        "matches": matches,
        "features": ["wing contour", "spots per forewing"],
        "inspected": cols * rows,
    }


def mismatch_board(r, edition):
    layout = [(3, 2), (4, 2), (3, 2)][edition]
    types = ["dial", "lever", "slide"]
    n = math.prod(layout)
    kinds = types + [r.choice(types) for _ in range(n - 3)]
    r.shuffle(kinds)
    upper = [[k, r.randrange(3)] for k in kinds]
    lower = [p[:] for p in upper]
    changed = r.choice([i for i, k in enumerate(kinds) if k == types[edition]])
    lower[changed][1] = (lower[changed][1] + r.randrange(1, 3)) % 3
    return {"layout": list(layout), "upper": upper, "lower": lower}


def mismatch_oracle(b):
    require(
        b["layout"] in ([3, 2], [4, 2])
        and len(b["upper"]) == len(b["lower"]) == math.prod(b["layout"]),
        "Bad controls",
    )
    differences = []
    for i, (a, z) in enumerate(zip(b["upper"], b["lower"])):
        require(
            len(a) == len(z) == 2
            and a[0] == z[0]
            and a[0] in ("dial", "lever", "slide")
            and all(type(v) is int and v in range(3) for v in [a[1], z[1]]),
            "Unmatched control",
        )
        if a != z:
            differences.append(i)
    require(len(differences) == 1, "Need exactly one changed control")
    i = differences[0]
    return {
        "answer": f"control-{i}",
        "differences": differences,
        "from": b["upper"][i],
        "to": b["lower"][i],
        "inspected": len(b["upper"]),
    }


def rotate(value, k):
    return value[k:] + value[:k]


def ring_equivalent(a, b):
    return any(rotate(a, k) == b for k in range(len(a)))


def fit_board(r, edition):
    n = [8, 9, 10][edition]
    profile = [0] * n
    for i in r.sample(range(n), 3 + int(edition == 2)):
        profile[i] = 1
    if any(rotate(profile, k) == profile for k in range(1, n)):
        return None
    # Lugs are all equally wide. Move one lug to make each decoy.
    variants = []
    for a in range(n):
        for z in range(n):
            if profile[a] == 1 and profile[z] == 0:
                v = profile[:]
                v[a], v[z] = 0, 1
                if not ring_equivalent(v, profile) and not any(
                    ring_equivalent(v, p) for p in variants
                ):
                    variants.append(v)
    if len(variants) < 2:
        return None
    parts = [rotate(profile, r.randrange(1, n)), *r.sample(variants, 2)]
    r.shuffle(parts)
    return {"socket": profile, "parts": parts}


def fit_oracle(b):
    socket, parts = b["socket"], b["parts"]
    n = len(socket)
    require(8 <= n <= 10 and len(parts) == 3 and 2 <= sum(socket) <= n - 2, "Bad broach")
    require(
        all(
            len(p) == n and all(type(v) is int and v in (0, 1) for v in p) and sum(p) == sum(socket)
            for p in [socket, *parts]
        ),
        "Bad keyed profile",
    )
    fits = []
    for i, part in enumerate(parts):
        for shift in range(n):
            if all(part[(k - shift) % n] == socket[k] for k in range(n)):
                fits.append([i, shift])
    require(len(fits) == 1, "Ambiguous insert or orientation")
    i, k = fits[0]
    return {
        "answer": f"insert-{i}",
        "insert": i,
        "clockwise_slots": k,
        "slots": n,
        "inspected": len(parts) * n,
    }


def shadow_board(r, edition):
    width = 3 + (edition == 1)
    heights = [r.randrange(1, 5) for _ in range(width)]
    if len(set(heights)) < 3:
        return None
    variants = [
        list(p)
        for p in sorted(set(itertools.permutations(heights)))
        if list(p) != heights and list(p) != heights[::-1]
    ]
    if len(variants) < 2:
        return None
    sculptures = []
    for outline in [heights, *r.sample(variants, 2)]:
        # Towers rest on a common baseline. Front columns may be shorter than the rear.
        sculptures.append([[r.randint(1, h) for h in outline], outline[:]])
    r.shuffle(sculptures)
    return {"screen": heights, "towers": sculptures}


def shadow_oracle(b):
    h = b["screen"]
    require(len(h) in (3, 4) and len(b["towers"]) == 3, "Bad shadow theatre")
    projections = []
    for tower in b["towers"]:
        require(
            len(tower) == 2
            and all(
                len(row) == len(h) and all(type(v) is int and 1 <= v <= 4 for v in row)
                for row in tower
            ),
            "Bad sculpture",
        )
        occupied = {(x, z) for row in tower for x, height in enumerate(row) for z in range(height)}
        projections.append([sum((x, z) in occupied for z in range(4)) for x in range(len(h))])
    matches = [i for i, v in enumerate(projections) if v == h]
    require(len(matches) == 1, "Multiple or missing shadows")
    return {
        "answer": f"tower-{matches[0]}",
        "tower": matches[0],
        "projections": projections,
        "inspected": len(h) * 2,
    }


NEW = {
    "search": (search_board, search_oracle),
    "mismatch": (mismatch_board, mismatch_oracle),
    "fit": (fit_board, fit_oracle),
    "shadow": (shadow_board, shadow_oracle),
}
