"""Local-only inventory, review handoff and measured Insights import."""

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .catalog import ENGINES
from .core import PuzzleSpec, digest, generate, require

FIELDS = (
    "puzzle_id",
    "post_age_hours",
    "views",
    "average_watch_seconds",
    "shares",
    "comments",
    "follows",
)


@dataclass
class Entry:
    spec: PuzzleSpec
    world: str
    rejected: int


def fingerprint(spec):
    """Ignore choice placement, serialization order, seed and art direction."""
    b = dict(spec.board)
    for key in (
        "receivers",
        "marked",
        "entrances",
        "tiles",
        "orders",
        "pieces",
        "prints",
        "loads",
        "scales",
        "clues",
        "mirrors",
        "wheels",
        "inverted",
    ):
        if key in b:
            b[key] = sorted(b[key])
    if "passages" in b:
        b["passages"] = sorted(sorted(edge) for edge in b["passages"])
    return digest([spec.engine, b])


def inventory(count, seed):
    require(type(count) is int and 1 <= count <= 200, "Pilot count must be 1–200")
    entries, extra, seen = [], [], set()
    stats = {"proposals_rejected": 0, "duplicate_instances_rejected": 0, "accepted": 0}
    serial = 0

    def unique(engine, level):
        nonlocal serial
        for _ in range(1000):
            spec, rejected = generate(engine, seed + serial, level)
            serial += 1
            stats["proposals_rejected"] += rejected
            key = fingerprint(spec)
            if key not in seen:
                seen.add(key)
                stats["accepted"] += 1
                return spec, rejected
            stats["duplicate_instances_rejected"] += 1
        raise ValueError("Unique inventory exhausted")

    while len(entries) < count:
        cycle = len(entries) // len(ENGINES)
        remaining = list(ENGINES.values())
        while remaining and len(entries) < count:
            choices = [
                e
                for e in remaining
                if not entries
                or (e.worlds[cycle % 2] != entries[-1].world and e.key != entries[-1].spec.engine)
            ]
            # Arrange the last two positions to avoid stranding a repeated world.
            if len(remaining) > 1:
                viable = [
                    e
                    for e in choices
                    if any(q.worlds[cycle % 2] != e.worlds[cycle % 2] for q in remaining if e != q)
                ]
                choices = viable or choices
            require(choices, "No compatible order")
            eng = max(
                choices,
                key=lambda e: sum(q.worlds[cycle % 2] == e.worlds[cycle % 2] for q in remaining),
            )
            remaining.remove(eng)
            spec, rejected = unique(eng, "medium" if cycle % 2 == 0 else "challenging")
            entries.append(Entry(spec, eng.worlds[cycle % 2], rejected))
    for i in range(5):
        for eng in ENGINES.values():
            spec, _ = unique(eng, ("easy", "medium", "challenging", "medium", "medium")[i])
            extra.append(spec)
    return entries, extra, stats


def handoff(entries, enable_live_integration=False):
    if enable_live_integration:
        raise ValueError("Live integration requires a separately implemented, approved publisher")
    return [
        {
            "puzzle_id": r["puzzle_id"],
            "video": r["video"],
            "cover": r["cover"],
            "caption": r["title"],
            "accessibility_text": r["accessibility_text"],
            "state": "awaiting_editorial_review",
        }
        for r in entries
    ]


def insights_template(path, ids):
    with Path(path).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({"puzzle_id": i} for i in ids)


def import_insights(path, rows):
    allowed = {r["puzzle_id"]: r for r in rows}
    output = {}
    with Path(path).open(newline="") as f:
        reader = csv.DictReader(f)
        require(reader.fieldnames == list(FIELDS), "Unexpected Insights columns")
        for row in reader:
            key = row["puzzle_id"]
            require(key in allowed and key not in output, "Unknown or duplicate measurement")
            if all(not row[k] for k in FIELDS[1:]):
                continue
            age, views, watch = (
                float(row["post_age_hours"]),
                int(row["views"]),
                float(row["average_watch_seconds"]),
            )
            require(
                all(math.isfinite(x) for x in (age, watch))
                and age > 0
                and views > 0
                and watch >= 0,
                "Incomplete or invalid Insights",
            )
            metrics = {k: int(row[k]) for k in ("shares", "comments", "follows")}
            require(min(metrics.values()) >= 0, "Negative Insights count")
            output[key] = {
                "age_hours": age,
                "views": views,
                "watch_fraction": watch / allowed[key]["duration"],
                **{k + "_per_100_views": round(100 * v / views, 3) for k, v in metrics.items()},
            }
    # Suggestions need at least two real observations of a mechanic at the same post age.
    suggestions = []
    for eng in ENGINES:
        for age in sorted({m["age_hours"] for m in output.values()}):
            cohort = [
                k
                for k, m in output.items()
                if m["age_hours"] == age and allowed[k]["engine"] == eng
            ]
            if len(cohort) >= 2:
                for metric in (
                    "watch_fraction",
                    "shares_per_100_views",
                    "comments_per_100_views",
                    "follows_per_100_views",
                ):
                    best = max(output[k][metric] for k in cohort)
                    winners = [k for k in cohort if output[k][metric] == best]
                    if len(winners) == 1:
                        suggestions.append(
                            {
                                "mechanic": eng,
                                "age_hours": age,
                                "metric": metric,
                                "pilot": winners[0],
                                "hypothesis": "Repeat this setting with a fresh matched instance.",
                            }
                        )
    return {"measurements": output, "exploratory_retest_hypotheses": suggestions}
