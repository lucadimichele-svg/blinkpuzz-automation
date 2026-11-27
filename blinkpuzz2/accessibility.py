"""Text alternatives express the same simultaneous evidence as the diagrams."""


def position(p):
    return f"column {p[0] + 1}, row {p[1] + 1}"


def alternatives(items):
    return ". ".join(f"{letter}: {value}" for letter, value in zip("ABC", items)) + "."


def text_board(key, b):
    if key == "laser":
        mirrors = "; ".join(
            position([x, y]) + " " + ("rises right" if slope == "/" else "falls right")
            for x, y, slope in b["mirrors"]
        )
        return (
            f"Beam enters from the left in row {b['emitter_row'] + 1}. Mirrors: {mirrors}. Crystals: "
            + alternatives(map(position, b["receivers"]))
        )
    if key == "maze":
        links = "; ".join(position(a) + " to " + position(z) for a, z in b["passages"])
        return (
            "Entrances: "
            + alternatives(map(position, b["entrances"]))
            + " Flag at "
            + position(b["exit"])
            + ". Open corridors: "
            + links
            + "."
        )
    if key == "pipes":
        rows = "; ".join(" ".join(row) for row in b["grid"])
        return (
            f"Inlet on the left in row {b['inlet'] + 1}. Outlet on the right in row {b['outlet'] + 1}. "
            "Tiles by row, compass ports: " + rows + ". Spare pieces: " + alternatives(b["pieces"])
        )
    if key == "circuit":
        switches = ", ".join(f"{k} starts at {v}" for k, v in zip(b["inputs"], b["states"]))
        a, z, c = b["inputs"]
        return (
            switches
            + ". Reversed before the gates: "
            + (", ".join(b["inverted"]) or "none")
            + f". {a} and {z} feed {b['gates'][0]}. Its output and {c} feed {b['gates'][1]}, then the lamp."
        )
    if key == "lock":
        from .engines.lock import NAMES, describe

        return (
            " ".join(describe(c) for c in b["clues"])
            + " Strips: "
            + alternatives(", ".join(NAMES[t] for t in code) for code in b["orders"])
        )
    if key in ("nonogram", "pattern"):
        n = 4 if key == "nonogram" else 3

        def bitmap(bits):
            return " / ".join(bits[i : i + n] for i in range(0, len(bits), n))

        legend = " A one means filled. Slashes separate rows. "
        if key == "pattern":
            return (
                legend
                + "Sequence: "
                + ", then ".join(map(bitmap, b["sequence"]))
                + ". Tiles: "
                + alternatives(map(bitmap, b["tiles"]))
            )

        def clues(lines):
            return "; ".join(", ".join(map(str, line)) for line in lines)

        return (
            "Row runs: "
            + clues(b["rows"])
            + ". Column runs: "
            + clues(b["columns"])
            + "."
            + legend
            + alternatives(map(bitmap, b["prints"]))
        )
    if key == "balance":

        def load(s):
            return " plus ".join({"C": "circle", "D": "diamond", "T": "triangle"}[t] for t in s)

        return (
            ". ".join(load(a) + " balances " + load(z) for a, z in b["scales"])
            + ". Match "
            + load(b["target"])
            + ". "
            + alternatives(map(load, b["loads"]))
        )
    if key == "gears":
        return (
            "Drive at "
            + position(b["drive"])
            + ". Wheels at "
            + "; ".join(map(position, b["wheels"]))
            + ". Marked wheels: "
            + alternatives(map(position, b["marked"]))
        )
    junction = {"U": "upper junction", "V": "lower junction"}
    return (
        "Fares: "
        + "; ".join(
            f"{junction.get(a, a)} to {junction.get(z, z)} costs {fare}"
            for (a, z), fare in b["roads"].items()
        )
        + "."
    )
