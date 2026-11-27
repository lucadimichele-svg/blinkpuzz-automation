import copy
import json
from dataclasses import asdict, replace

import pytest

from blinkpuzz2.catalog import ENGINES
from blinkpuzz2.core import LEVELS, PuzzleSpec, assess, generate, validate
from blinkpuzz2.planning import fingerprint


@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("seed", range(100))
def test_seed_and_oracle(engine, seed):
    e = ENGINES[engine]
    level = LEVELS[seed % 3]
    s, rejected = generate(e, seed, level)
    again, attempts = generate(e, seed, level)
    assert asdict(s) == asdict(again) and rejected == attempts
    restored = PuzzleSpec(**json.loads(json.dumps(asdict(s))))
    assert validate(restored, ENGINES).winners == [s.solution]
    assert e.solve(copy.deepcopy(s.board)).witness == s.proof["witness"]
    assert s.evidence and s.accessibility_text and s.options == list("ABC")


@pytest.mark.parametrize("engine", ENGINES)
def test_structural_variety(engine):
    structural = {
        "laser": "mirrors",
        "maze": "passages",
        "lock": "clues",
        "pipes": "grid",
        "pattern": "sequence",
        "nonogram": "rows",
        "circuit": "gates",
        "routes": "roads",
        "balance": "scales",
        "gears": "wheels",
    }
    shapes = set()
    for seed in range(100):
        b = generate(ENGINES[engine], seed)[0].board
        value = b[structural[engine]]
        if engine == "routes":
            value = sorted(value)  # Require distinct road networks regardless of fares.
        if engine == "circuit":
            value = [value, b["inverted"]]
        shapes.add(json.dumps(value, sort_keys=True))
    assert len(shapes) >= 5


@pytest.mark.parametrize("engine", ENGINES)
def test_reject_tampered_answer_proof_and_hidden_fields(engine):
    s, _ = generate(ENGINES[engine], 101)
    for altered in [
        replace(s, solution=next(k for k in "ABC" if k != s.solution)),
        replace(s, proof={}),
        replace(s, rules=["A new rule appears later"]),
        replace(s, board={**s.board, "hidden_answer": "C"}),
        replace(s, schema_version=0),
        replace(s, seed=s.seed + 981),
    ]:
        with pytest.raises(ValueError):
            validate(altered, ENGINES)


def test_ambiguous_and_unsolvable_lock():
    b = generate(ENGINES["lock"], 3)[0].board
    for clues in [
        [["before", "K", "M"]] * 3,
        [["before", "K", "M"], ["before", "M", "K"], ["before", "F", "S"]],
    ]:
        with pytest.raises(ValueError, match="Contradictory or underdetermined"):
            assess(ENGINES["lock"], {**b, "clues": clues})


def test_ray_has_known_turns_and_rejects_outside_and_miss():
    b = {
        "size": 5,
        "emitter_row": 3,
        "mirrors": [[2, 3, "/"], [2, 1, "/"]],
        "receivers": [[1, 0], [4, 1], [1, 4]],
    }
    result = assess(ENGINES["laser"], b)
    assert result.winners == ["B"] and result.witness["path"] == [
        [0, 3],
        [1, 3],
        [2, 3],
        [2, 2],
        [2, 1],
        [3, 1],
        [4, 1],
    ]
    for mirrors in [[[5, 3, "/"]], [], [[1, 3, "/"], [1, 3, "\\"]]]:
        with pytest.raises(ValueError):
            assess(ENGINES["laser"], {**b, "mirrors": mirrors})


def test_disconnected_gears_and_duplicate_candidates():
    b = {
        "wheels": [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [4, 4]],
        "drive": [0, 0],
        "marked": [[1, 0], [2, 0], [3, 0]],
    }
    with pytest.raises(ValueError, match="Disconnected"):
        assess(ENGINES["gears"], b)
    b = generate(ENGINES["pipes"], 17)[0].board
    with pytest.raises(ValueError, match="distinct choices"):
        assess(ENGINES["pipes"], {**b, "pieces": ["EW", "EW", "NS"]})


def test_equal_cheapest_routes_and_two_winning_switches():
    b = {
        "roads": dict.fromkeys(["SA", "SB", "SC", "AU", "BU", "CV", "UX", "VX"], 1),
        "heights": [250, 310],
    }
    with pytest.raises(ValueError, match="no unique answer"):
        assess(ENGINES["routes"], b)
    switches = {"inputs": list("ABC"), "gates": ["OR", "OR"], "states": [0, 0, 0], "inverted": []}
    with pytest.raises(ValueError, match="no unique answer"):
        assess(ENGINES["circuit"], switches)


def test_ambiguous_nonogram_even_if_only_one_print_fits():
    b = {
        "rows": [[1]] * 4,
        "columns": [[1]] * 4,
        "prints": ["1000010000100001", "1" * 16, "0" * 16],
    }
    with pytest.raises(ValueError, match="full image uniquely"):
        assess(ENGINES["nonogram"], b)


def test_impossible_scales_and_broken_transform():
    bad = {"scales": [["C", "CC"], ["D", "T"]], "target": "CC", "loads": ["D", "DT", "T"]}
    with pytest.raises(ValueError, match="Contradictory scales"):
        assess(ENGINES["balance"], bad)
    b = generate(ENGINES["pattern"], 14)[0].board
    with pytest.raises(ValueError):
        assess(ENGINES["pattern"], {**b, "sequence": [b["sequence"][0]] * 2})


def test_choice_shuffle_preserves_geometry_fingerprint():
    s, _ = generate(ENGINES["pipes"], 29)
    assert fingerprint(s) == fingerprint(
        replace(s, board={**s.board, "pieces": s.board["pieces"][::-1]})
    )
