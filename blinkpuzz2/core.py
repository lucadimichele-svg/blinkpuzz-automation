"""Public puzzle contracts. Oracles see only the public board."""

from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .accessibility import text_board
from .difficulty import distractors

Board = dict[str, Any]
LEVELS = ("easy", "medium", "challenging")
LETTERS = "ABC"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


@dataclass(frozen=True)
class Outcome:
    winners: list[str]
    witness: dict
    steps: int
    branches: int
    explanation: str


@dataclass(frozen=True)
class Engine:
    key: str
    title: str
    rules: tuple[str, ...]
    worlds: tuple[str, ...]
    fields: tuple[str, ...]
    propose: Callable[[random.Random, int], Board]
    solve: Callable[[Board], Outcome]
    min_steps: int = 2


@dataclass(frozen=True)
class PuzzleSpec:
    schema_version: int
    mechanic_version: int
    puzzle_id: str
    seed: int
    engine: str
    board: Board
    rules: list[str]
    options: list[str]
    solution: str
    proof: dict
    difficulty: dict
    evidence: list[str]
    accessibility_text: str

    @classmethod
    def read(cls, path):
        return cls(**json.loads(Path(path).read_text()))

    def save(self, path):
        write_json(path, asdict(self))


def assess(engine, board):
    require(set(board) == set(engine.fields), "Unexpected or missing board fields")
    try:
        result = engine.solve(board)
    except (KeyError, IndexError, TypeError, StopIteration, ZeroDivisionError) as exc:
        raise ValueError("Malformed board") from exc
    require(len(result.winners) == 1 and result.winners[0] in LETTERS, "Board has no unique answer")
    require(result.steps >= engine.min_steps, "Trivial solution")
    return result


def assemble(engine, seed, level, board, result):
    require(type(seed) is int and level in LEVELS, "Invalid generation parameters")
    # The identity excludes the seed, presentation and requested difficulty.
    identity = digest([1, engine.key, board])[:20]
    rules = list(engine.rules)
    evidence = list(engine.fields)
    return PuzzleSpec(
        1,
        1,
        engine.key + "-" + identity,
        seed,
        engine.key,
        board,
        rules,
        list(LETTERS),
        result.winners[0],
        {"winner_count": 1, "witness": result.witness, "reason": result.explanation},
        {
            "requested": level,
            "steps": result.steps,
            "branching": result.branches,
            "alternatives": 2,
            "distractors": distractors(engine.key, board, result),
            "simultaneous_rule_words": len(" ".join(rules).split()),
        },
        evidence,
        " ".join([engine.title, *rules, text_board(engine.key, board)]),
    )


def generate(engine, seed, level="medium"):
    require(level in LEVELS and type(seed) is int, "Invalid difficulty or seed")
    rng = random.Random(digest([engine.key, seed, level, 1]))
    for rejected in range(12000):
        board = engine.propose(rng, LEVELS.index(level))
        if board is None:
            continue
        try:
            result = assess(engine, board)
        except ValueError:
            continue
        return assemble(engine, seed, level, board, result), rejected
    raise RuntimeError(f"No suitable {engine.key} board for seed {seed}")


def validate(spec, catalog):
    require(spec.engine in catalog, "Unknown mechanic")
    engine = catalog[spec.engine]
    result = assess(engine, spec.board)
    expected = assemble(engine, spec.seed, spec.difficulty["requested"], spec.board, result)
    require(
        canonical(asdict(spec)) == canonical(asdict(expected)),
        "Contract, evidence or proof mismatch",
    )
    replay, _ = generate(engine, spec.seed, spec.difficulty["requested"])
    require(canonical(replay.board) == canonical(spec.board), "Seed does not reproduce this board")
    return result


def triplet(items):
    require(
        isinstance(items, list) and len(items) == 3 and len({canonical(x) for x in items}) == 3,
        "Three distinct choices required",
    )


def point(p, n):
    require(
        isinstance(p, list) and len(p) == 2 and all(type(v) is int and 0 <= v < n for v in p),
        "Coordinate outside board",
    )
    return tuple(p)


def choices(rng, answer, alternatives):
    others = list(dict.fromkeys(x for x in alternatives if x != answer))
    values = [answer, *rng.sample(others, 2)]
    rng.shuffle(values)
    return values
