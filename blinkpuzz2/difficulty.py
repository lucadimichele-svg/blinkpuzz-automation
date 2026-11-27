"""Observable properties of each distractor, in the units of the game."""

from collections import deque


def distractors(key, board, result):
    b, w = board, result.witness
    answer = result.winners[0]
    wrong = [i for i, k in enumerate("ABC") if k != answer]
    labels = ["ABC"[i] for i in wrong]
    if key == "laser":
        values = [
            min(abs(x - b["receivers"][i][0]) + abs(y - b["receivers"][i][1]) for x, y in w["path"])
            for i in wrong
        ]
        unit = "nearest ray distance in cells"
    elif key == "maze":
        graph = {}
        for a, z in b["passages"]:
            graph.setdefault(tuple(a), []).append(tuple(z))
            graph.setdefault(tuple(z), []).append(tuple(a))
        values = []
        for i in wrong:
            start = tuple(b["entrances"][i])
            queue, seen = deque([start]), {start}
            while queue:
                for cell in graph.get(queue.popleft(), []):
                    if cell not in seen:
                        seen.add(cell)
                        queue.append(cell)
            values.append(len(seen))
        unit = "explorable cells before ruling out gate"
    elif key == "pipes":
        unit, values = "connected cells before break", [len(w["traces"][k]) for k in labels]
    elif key == "circuit":
        table = w["truth_table"]
        unit = "signal differences from working configuration"
        values = [sum(a != z for a, z in zip(table[k], table[answer])) for k in labels]
    elif key == "lock":
        unit, values = "notes satisfied", [sum(w["candidate_checks"][i]) for i in wrong]
    elif key == "routes":
        unit = "excess fare over cheapest trip"
        values = [
            min(cost for path, cost in w["paths"] if path[1] == k) - w["cost"] for k in labels
        ]
    elif key == "gears":
        depths = {(x, y): depth for x, y, sign, depth in w["directions"]}
        unit, values = "contacts from drive", [depths[tuple(b["marked"][i])] for i in wrong]
    elif key == "balance":

        def mass(load, weights):
            return sum(weights["CDT".index(c)] for c in load)

        unit = "smallest mass difference across valid assignments"
        values = [
            min(
                abs(mass(b["loads"][i], model) - mass(b["target"], model))
                for model in w["models_CDT"]
            )
            for i in wrong
        ]
    else:
        target = w["bitmap"] if key == "nonogram" else w["sequence"][-1]
        tiles = b["prints"] if key == "nonogram" else b["tiles"]
        unit = "cells differing from solution"
        values = [sum(a != z for a, z in zip(target, tiles[i])) for i in wrong]
    return {"measure": unit, "values": dict(zip(labels, values))}
