from blinkpuzz2.core import LETTERS, Engine, Outcome, require

OPS = {"AND": lambda a, b: a & b, "OR": lambda a, b: a | b, "XOR": lambda a, b: a ^ b}


def propose(rng, level):
    ops = ["AND", "OR"] if level == 0 else list(OPS)
    return {
        "inputs": rng.sample(list(LETTERS), 3),
        "states": [rng.randrange(2) for _ in LETTERS],
        "gates": [rng.choice(ops), rng.choice(ops)],
        "inverted": rng.sample(list(LETTERS), level),
    }


def solve(b):
    ports, state, gates = b["inputs"], b["states"], b["gates"]
    require(
        sorted(ports) == list(LETTERS)
        and len(state) == 3
        and all(type(x) is int and x in (0, 1) for x in state),
        "Bad switch bank",
    )
    require(len(gates) == 2 and all(g in OPS for g in gates), "Unknown gate")
    require(
        isinstance(b["inverted"], list)
        and set(b["inverted"]) <= set(LETTERS)
        and len(set(b["inverted"])) == len(b["inverted"]) <= 2,
        "Invalid inverters",
    )
    outcomes = {}
    for toggle in ["initial", *LETTERS]:
        a, c, d = [
            bit ^ int(label == toggle) ^ int(label in b["inverted"])
            for label, bit in zip(ports, state)
        ]
        inner = OPS[gates[0]](a, c)
        outcomes[toggle] = [a, c, d, inner, OPS[gates[1]](inner, d)]
    require(outcomes["initial"][-1] == 0, "Lamp already on")
    winners = [k for k in LETTERS if outcomes[k][-1]]
    return Outcome(
        winners, {"truth_table": outcomes}, 2, 3, "This flip sends a 1 through the final gate."
    )


ENGINE = Engine(
    "circuit",
    "Which switch lights the lamp?",
    ("Flip one switch. NOT reverses a bit.", "AND: both · OR: any · XOR: exactly one."),
    ("lab", "workshop"),
    ("inputs", "states", "gates", "inverted"),
    propose,
    solve,
)
