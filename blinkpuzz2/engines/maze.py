from collections import deque

from blinkpuzz2.core import LETTERS, Engine, Outcome, point, require, triplet

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def propose(rng, level):
    n = 5 + (level == 2)
    starts = [[0, y] for y in sorted(rng.sample(range(n), 3))]
    occupied = {tuple(p) for p in starts}
    edges = []
    frontier = [(p, (p[0] + dx, p[1] + dy)) for p in sorted(occupied) for dx, dy in DIRS]
    while frontier:
        p, q = frontier.pop(rng.randrange(len(frontier)))
        if q in occupied or not all(0 <= v < n for v in q):
            continue
        occupied.add(q)
        edges.append([list(p), list(q)])
        frontier.extend((q, (q[0] + dx, q[1] + dy)) for dx, dy in DIRS)
    return {"size": n, "entrances": starts, "exit": [n - 1, rng.randrange(n)], "passages": edges}


def solve(b):
    n = b["size"]
    require(type(n) is int and n in (5, 6), "Invalid maze size")
    triplet(b["entrances"])
    starts = [point(p, n) for p in b["entrances"]]
    end = point(b["exit"], n)
    require(all(x == 0 for x, _ in starts) and end[0] == n - 1, "Port on wrong side")
    graph = {(x, y): [] for x in range(n) for y in range(n)}
    for a, z in b["passages"]:
        p, q = point(a, n), point(z, n)
        require(
            sum(abs(i - j) for i, j in zip(p, q)) == 1 and q not in graph[p], "Invalid corridor"
        )
        graph[p].append(q)
        graph[q].append(p)
    queue, parent = deque([end]), {end: None}
    while queue:
        p = queue.popleft()
        for q in graph[p]:
            if q not in parent:
                parent[q] = p
                queue.append(q)
    winners = [LETTERS[i] for i, p in enumerate(starts) if p in parent]
    path = []
    if winners:
        p = starts[LETTERS.index(winners[0])]
        while p is not None:
            path.append(list(p))
            p = parent[p]
    require(len({p[1] for p in path}) >= 2, "Straight or unreachable exit")
    return Outcome(
        winners,
        {"path": path, "reachable_cells": len(parent)},
        len(path),
        sum(len(graph[p]) > 2 for p in parent),
        "Only the highlighted corridor reaches the flag.",
    )


ENGINE = Engine(
    "maze",
    "Which gate reaches the flag?",
    ("Walk through gaps in the walls.", "Start at A, B or C."),
    ("ruins", "editorial"),
    ("size", "entrances", "exit", "passages"),
    propose,
    solve,
    6,
)
