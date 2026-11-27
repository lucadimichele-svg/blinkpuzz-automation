import csv
import itertools
from dataclasses import replace
from pathlib import Path

import pytest
from PIL import Image

from blinkpuzz2.catalog import ENGINES
from blinkpuzz2.collection import dhash, safe_output
from blinkpuzz2.core import generate
from blinkpuzz2.planning import (
    FIELDS,
    handoff,
    import_insights,
    insights_template,
    inventory,
)
from blinkpuzz2.render.frames import background, scene
from blinkpuzz2.render.media import checked_image, probe
from blinkpuzz2.render.storyboard import storyboard, validate_timeline
from blinkpuzz2.scenes.drawing import Surface


@pytest.mark.parametrize("engine", ENGINES)
def test_all_compatible_layouts(engine):
    e = ENGINES[engine]
    s, _ = generate(e, 72)
    for world in e.worlds:
        bg = background(s, world)
        for phase, progress in [("solve", 0), ("cover", 0), ("proof", 0.5), ("proof", 1)]:
            frame, audit = scene(s, world, bg, phase, progress)
            assert frame.size == (1080, 1920)
            assert (
                audit["min_contrast"] >= 4.5 and audit["text_collisions"] == audit["clipped"] == 0
            )
            if phase == "cover":
                for region in ("objective", "board"):
                    _, y, _, bottom = audit["regions"][region]
                    assert y >= 420 and bottom <= 1500


def test_delayed_and_disappearing_clues_rejected():
    s, _ = generate(ENGINES["lock"], 41)
    timeline = storyboard(s)
    for interval in ([1, timeline.solve_seconds], [0, timeline.solve_seconds - 1]):
        with pytest.raises(ValueError, match="Staged"):
            validate_timeline(
                s,
                replace(
                    timeline, evidence_intervals={**timeline.evidence_intervals, "clues": interval}
                ),
            )


def test_clipped_contrast_and_overlap():
    s = Surface(Image.new("RGB", (300, 200), "white"), "black", "white", "blue")
    s.text(100, 90, "gate", 36)
    for x, y, fg in [(103, 100, "black"), (-30, 100, "black"), (140, 150, "#aaaaaa")]:
        with pytest.raises(ValueError):
            s.text(x, y, "gate", 36, color=fg)


def test_plan_coverage_and_safety():
    entries, extra, stats = inventory(20, 20261127)
    assert len(entries) == 20 and len(extra) == 50 and stats["accepted"] == 70
    assert all(a.world != b.world for a, b in itertools.pairwise(entries))
    assert all(
        {e.world for e in entries if e.spec.engine == k} == set(v.worlds)
        for k, v in ENGINES.items()
    )
    with pytest.raises(ValueError):
        handoff([], enable_live_integration=True)
    with pytest.raises(ValueError):
        safe_output(Path(__file__).resolve().parents[1] / "docs/media/demo.mp4")


def test_media_rejects_wrong_still_and_unreadable_video(tmp_path):
    p = tmp_path / "cover.jpg"
    Image.new("RGB", (1080, 1920), "white").save(p)
    with pytest.raises(ValueError):
        checked_image(p, Image.new("RGB", (1080, 1920), "black"))
    import subprocess

    with pytest.raises((subprocess.CalledProcessError, ValueError)):
        probe(p, 12)
    q = tmp_path / "copy.jpg"
    q.write_bytes(p.read_bytes())
    assert dhash(p) == dhash(q)


def test_insights_requires_real_comparable_observations(tmp_path):
    rows = [{"puzzle_id": k, "engine": "laser", "duration": 15} for k in ["x", "y"]]
    p = tmp_path / "insights.csv"
    insights_template(p, ["x", "y"])
    assert import_insights(p, rows) == {"measurements": {}, "exploratory_retest_hypotheses": []}

    def write(age):
        with p.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerows([FIELDS, ["x", 48, 120, 8, 5, 2, 3], ["y", age, 160, 10, 4, 2, 3]])

    write(24)
    assert not import_insights(p, rows)["exploratory_retest_hypotheses"]
    write(48)
    assert import_insights(p, rows)["exploratory_retest_hypotheses"]
    write(-1)
    with pytest.raises(ValueError):
        import_insights(p, rows)
