import copy
from dataclasses import replace

import pytest

from blinkpuzz2.core import digest
from blinkpuzz2.phase2.collection import selector
from blinkpuzz2.phase2.experience import (
    FAMILIES,
    boundary,
    collection,
    make,
    oracle,
    signature,
    validate,
)
from blinkpuzz2.phase2.geometry import build_scene, check_camera, check_scene


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("seed", range(100))
def test_independent_replay_and_display_geometry(family, seed):
    s = make(family, seed, seed % 3)
    assert oracle(family, copy.deepcopy(s.board)) == s.proof
    assert validate(s) == s
    assert s.evidence == {
        key: [0, s.solve_seconds] for key in [*s.board, "objective", "visual_key"]
    }
    assert 12 <= s.solve_seconds + s.reveal_seconds <= 22
    assert check_scene(s, build_scene(s))["feature_at_360px"] >= 3


def test_benchmark_has_eight_valid_boundary_cases_and_no_duplicate_boards():
    pilots, extra = collection()
    assert (len(pilots), len(extra)) == (24, 104)
    assert len({digest([s.family, s.board]) for s in pilots + extra}) == 128
    assert {s.family for s in extra[:8] if boundary(s)} == set(FAMILIES)
    assert len({s.grammar for s in pilots}) == 8
    assert set(selector()) == {
        "laser",
        "maze",
        "gears",
        "pipes",
        "nonogram",
        "circuit",
        "lock",
        "balance",
        "routes",
        "pattern",
    }
    for family in FAMILIES:
        selected = [s for s in pilots if s.family == family]
        assert {s.edition for s in selected} == {0, 1, 2}
        assert len({signature(s) for s in selected}) == 3
    for s in extra:
        assert check_scene(s, build_scene(s))["checked_entities"] > 0


@pytest.mark.parametrize("family", FAMILIES)
def test_solver_rejects_ambiguous_or_unplayable_board(family):
    s = make(family, 31)
    b = copy.deepcopy(s.board)
    if family == "search":
        i = (s.proof["matches"][0] + 1) % len(b["specimens"])
        b["specimens"][i][:2] = b["sample"]
    elif family == "mismatch":
        b["upper"] = b["lower"]
    elif family == "fit":
        b["parts"][(s.proof["insert"] + 1) % 3] = b["socket"]
    elif family == "shadow":
        b["towers"][(s.proof["tower"] + 1) % 3] = b["towers"][s.proof["tower"]]
    elif family == "maze":
        b["passages"] = []
    elif family == "laser":
        b["receivers"][1] = b["receivers"][0]
    elif family == "pipes":
        b["pieces"][1] = b["pieces"][0]
    else:
        b["output"] = b["drive"]
    with pytest.raises(ValueError):
        oracle(family, b)


@pytest.mark.parametrize("family", FAMILIES)
def test_artist_edits_invalidate_geometry(family):
    s = make(family, 58)
    st = build_scene(s)
    nodes = {n["tag"]: n for n in st.nodes if "tag" in n}
    if family == "gears":
        next(iter(nodes.values()))["pos"][0] += 20
    elif family == "maze":
        next(iter(nodes.values()))["pos"][1] += 16
    elif family == "laser":
        next(n for k, n in nodes.items() if k.startswith("mirror-"))["angle"] += 90
    elif family == "shadow":
        next(n for k, n in nodes.items() if k.startswith("voxel-"))["pos"][0] += 21
    elif family == "mismatch":
        n = nodes["lower-0"]
        if n["kind"] == "tube":
            n["points"][-1][1] += 19
            n["points"][-1][0] += 13
        else:
            n["pos"][0] += 17
    elif family == "fit":
        nodes["die"]["hole"][2][1] *= 0.52
    elif family == "pipes":
        next(n for k, n in nodes.items() if k.startswith("pipe-"))["points"][0][0] += 20
    else:
        nodes["sample-right"]["outline"].pop()
    with pytest.raises(ValueError):
        check_scene(s, st)


def test_staged_evidence_and_wrong_answer_rejected():
    s = make("search", 68)
    with pytest.raises(ValueError):
        validate(replace(s, evidence={**s.evidence, "sample": [3, s.solve_seconds]}))
    with pytest.raises(ValueError):
        validate(replace(s, proof={**s.proof, "answer": "another moth"}))


def test_projected_mesh_displacement_fails():
    st = build_scene(make("laser", 28))
    receipt = {n["tag"]: st.screen(n["pos"]) for n in st.nodes if "tag" in n}
    check_camera(st, receipt)
    receipt["emitter"][0] += 1
    with pytest.raises(ValueError):
        check_camera(st, receipt)
