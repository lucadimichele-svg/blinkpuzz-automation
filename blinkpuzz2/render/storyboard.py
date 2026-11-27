from dataclasses import asdict, dataclass

from blinkpuzz2.core import require


@dataclass(frozen=True)
class Storyboard:
    solve_seconds: int
    reveal_seconds: int
    evidence_intervals: dict[str, list[int]]
    timing_reason: str

    @property
    def duration(self):
        return self.solve_seconds + self.reveal_seconds


def storyboard(spec, reveal=True):
    steps, branches = spec.difficulty["steps"], spec.difficulty["branching"]
    seconds = min(
        18,
        9
        + min(steps, 9) // 2
        + min(branches, 24) // 6
        + {"easy": 0, "medium": 1, "challenging": 2}[spec.difficulty["requested"]],
    )
    reason = f"{steps} reasoning steps, {branches} branches or compatible states; {seconds}s simultaneous inspection."
    return Storyboard(
        seconds,
        3 if reveal else 0,
        {key: [0, seconds] for key in ["objective", "rules", *spec.evidence]},
        reason,
    )


def validate_timeline(spec, story):
    expected = storyboard(spec, bool(story.reveal_seconds))
    require(asdict(story) == asdict(expected), "Staged, missing or inconsistent evidence interval")
