import random
from collections import deque
from dataclasses import asdict, dataclass

from blinkpuzz2.catalog import ENGINES
from blinkpuzz2.core import assess, canonical, digest, generate, point, require

from .games import NEW


# The primary rotation is explicit. Every legacy engine remains callable in its existing catalog.
@dataclass(frozen=True)
class Format:
    grammar: str
    objective: str
    instruction: str
    reveal: str
    camera_tilt: float


FORMATS = {
    "laser": Format(
        "Prism observatory",
        "Which crystal catches the beam?",
        "",
        "Pulse through each reflection",
        13,
    ),
    "maze": Format(
        "Harbor citadel",
        "Which gate reaches the flag?",
        "Stay inside the walls.",
        "Sail the open canal to the flag",
        31,
    ),
    "search": Format(
        "Lepidoptera cabinet",
        "Find the matching moth.",
        "Match wings and spots.",
        "Focus the loupe on the unique specimen",
        6,
    ),
    "mismatch": Format(
        "Patchbay twins",
        "Spot the changed control.",
        "Compare the two consoles.",
        "Link the one unequal pair of controls",
        12,
    ),
    "fit": Format(
        "Fly press",
        "Which insert fits the socket?",
        "You may turn it.",
        "Turn the matching broach and seat it",
        4,
    ),
    "pipes": Format(
        "Bathysphere manifold",
        "Which pipe seals the gap?",
        "Keep each bend as shown.",
        "Fit the spool and fill the continuous line",
        16,
    ),
    "gears": Format(
        "Escapement",
        "Which way will the red gear turn?",
        "Follow the drive arrow.",
        "Run the train and mark the output rotation",
        0,
    ),
    "shadow": Format(
        "Lantern theatre",
        "Which tower casts this shadow?",
        "Light shines straight from the front.",
        "Project the matching tower onto the screen",
        56,
    ),
}
FAMILIES = tuple(FORMATS)
SAFE = (55, 205, 950, 1530)


@dataclass(frozen=True)
class ExperienceSpec:
    version: int
    puzzle_id: str
    family: str
    seed: int
    edition: int
    grammar: str
    objective: str
    instruction: str
    board: dict
    visual_key: str
    evidence: dict
    solve_seconds: int
    reveal_seconds: int
    proof: dict
    demonstration: str
    canvas: list
    safe_zone: list


KEYS = {
    "laser": "arrow on emitter; three faceted receiver shapes",
    "maze": "numbered entrances and finish flag",
    "pipes": "inflow arrow, empty flange and three oriented spares",
    "gears": "drive arrow and red output with bullseye",
    "search": "magnified sample pinned above the drawer",
    "mismatch": "two equal banks in matching orientation",
    "fit": "open die and loose keyed inserts",
    "shadow": "backlit outline above front-facing sculptures",
}


def oracle(family, b):
    if family in NEW:
        return NEW[family][1](b)
    if family == "gears":
        require(set(b) == {"wheels", "drive", "output"}, "Unexpected gear clues")
        wheels = {point(p, 5) for p in b["wheels"]}
        drive = point(b["drive"], 5)
        require(
            drive in wheels and len(wheels) == len(b["wheels"]) and 6 <= len(wheels) <= 16,
            "Invalid train",
        )
        queue = deque([drive])
        depth = {drive: 0}
        while queue:
            x, y = queue.popleft()
            for q in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
                if q in wheels and q not in depth:
                    depth[q] = depth[x, y] + 1
                    queue.append(q)
        require(set(depth) == wheels, "Disconnected train")
        directions = [[*p, (-1) ** depth[p], depth[p]] for p in sorted(wheels)]
        choices = [p for p in directions if p[:2] == b["output"] and p[3] >= 2]
        require(len(choices) == 1, "Output must be meshed and at least two contacts away")
        return {
            "answer": "clockwise" if choices[0][2] == 1 else "counterclockwise",
            "directions": directions,
            "depth": choices[0][3],
            "inspected": len(directions),
        }
    result = assess(ENGINES[family], b)
    slot = "ABC".index(result.winners[0])
    answer = {
        "laser": ("prism", "cube", "hexagon"),
        "maze": ("gate-1", "gate-2", "gate-3"),
        "pipes": ("spare-1", "spare-2", "spare-3"),
    }[family][slot]
    return {"answer": answer, "slot": slot, **result.witness, "inspected": result.steps}


def make(family, seed, edition=0):
    f = FORMATS[family]
    require(type(seed) is int and edition in range(3), "Invalid seed or edition")
    rng = random.Random(digest(["experience", 1, family, seed, edition]))
    if family in NEW:
        propose, solve = NEW[family]
        for _ in range(500):
            b = propose(rng, edition)
            if b is not None:
                try:
                    proof = solve(b)
                except ValueError:
                    continue
                break
        else:
            raise ValueError("Proposal budget exhausted")
    else:
        legacy, _ = generate(ENGINES[family], seed, ("medium", "challenging", "easy")[edition])
        b = dict(legacy.board)
        if family == "gears":
            possible = [p for p in legacy.proof["witness"]["directions"] if p[3] >= 2]
            b["output"] = rng.choice(possible)[:2]
            del b["marked"]
        proof = oracle(family, b)
    solve = min(17, 9 + proof["inspected"] // 3)
    return ExperienceSpec(
        1,
        family + "-" + digest([family, b])[:16],
        family,
        seed,
        edition,
        f.grammar,
        f.objective,
        f.instruction,
        b,
        KEYS[family],
        {k: [0, solve] for k in ["objective", "visual_key", *b]},
        solve,
        4,
        proof,
        f.reveal,
        [1080, 1920],
        list(SAFE),
    )


def validate(s):
    require(
        canonical(s.proof) == canonical(oracle(s.family, s.board)), "Incorrect independent witness"
    )
    require(
        canonical(asdict(s)) == canonical(asdict(make(s.family, s.seed, s.edition))),
        "Experience, evidence or geometry disagrees with seed",
    )
    require(len((s.objective + " " + s.instruction).split()) <= 15, "Too many explanatory words")
    return s


def signature(s):
    b = s.board
    if s.family == "search":
        return (tuple(b["sample"]), tuple(b["shape"]), s.proof["answer"])
    if s.family == "mismatch":
        return (s.proof["from"][0], s.proof["answer"])
    if s.family == "fit":
        return (len(b["socket"]), tuple(b["socket"]))
    if s.family == "shadow":
        return tuple(b["screen"])
    if s.family == "laser":
        return (b["size"], b["emitter_row"], s.proof["reflections"], s.proof["answer"])
    if s.family == "pipes":
        return (len(b["grid"]), tuple(b["gap"]), b["pieces"][s.proof["slot"]])
    if s.family == "gears":
        return (len(b["wheels"]), s.proof["depth"], s.proof["answer"])
    return (b["size"], tuple(b["exit"]), s.proof["slot"], len(s.proof["path"]))


# Each family's first reserve deliberately exercises a borderline but valid case.
def boundary(s):
    b = s.board
    p = s.proof
    if s.family == "laser":
        return p["reflections"] >= 3
    if s.family == "maze":
        return len(p["path"]) >= 10
    if s.family == "gears":
        return p["depth"] >= 4
    if s.family == "pipes":
        return 0 in b["gap"] or len(b["grid"]) - 1 in b["gap"]
    if s.family == "search":
        return b["sample"][1] == 3
    if s.family == "mismatch":
        return abs(p["from"][1] - p["to"][1]) == 1
    if s.family == "fit":
        return p["clockwise_slots"] in (1, p["slots"] - 1)
    return any(h < h2 for h, h2 in zip(*b["towers"][p["tower"]]))


def collection(seed=20261128):
    pilots = []
    extra = []
    used = set()
    for ed in range(3):
        for i, f in enumerate(FAMILIES):
            for attempt in range(600):
                s = make(f, seed + ed * 1000 + i * 71 + attempt, ed)
                prior = [p for p in pilots if p.family == f]
                if any(signature(p) == signature(s) for p in prior):
                    continue
                if f == "gears" and ed == 1 and prior[0].proof["answer"] == s.proof["answer"]:
                    continue
                if f == "maze" and len(s.proof["path"]) < 7:
                    continue
                if f in ("laser", "pipes", "maze", "fit", "shadow") and any(
                    p.proof["answer"] == s.proof["answer"] for p in prior
                ):
                    continue
                if f == "laser" and (
                    len(s.proof["path"]) < 6 or (ed == 1 and s.proof["reflections"] < 3)
                ):
                    continue
                break
            else:
                raise ValueError("Unable to select distinct episode")
            pilots.append(validate(s))
            used.add(s.puzzle_id)
    for i in range(104):
        f = FAMILIES[i % 8]
        for offset in range(100):
            s = validate(make(f, seed + 10000 + i * 101 + offset, i % 3))
            if s.puzzle_id not in used and (i >= 8 or boundary(s)):
                break
        else:
            raise ValueError("Duplicate reserve inventory")
        extra.append(s)
        used.add(s.puzzle_id)
    return pilots, extra
