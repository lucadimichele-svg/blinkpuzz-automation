from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from experiment_report import summarize


def test_experiment_audit_does_not_confuse_base_and_noon_ids():
    posts = [
        {"id": "one", "status": "scheduled", "dueAt": "2026-11-17T11:00:00Z",
         "text": "Example\nChallenge ID: BP20261117N1\nSPOILER — SOLUTION BELOW"},
        {"id": "two", "status": "scheduled", "dueAt": "2026-11-17T18:30:00Z",
         "text": "Example\nChallenge ID: BP20261117\nSPOILER — SOLUTION BELOW"},
        {"id": "three", "status": "scheduled", "dueAt": "2026-11-18T11:00:00Z",
         "text": "Example\nChallenge ID: BP20261118N1\nSPOILER — SOLUTION BELOW"},
        {"id": "four", "status": "scheduled", "dueAt": "2026-11-18T18:30:00Z",
         "text": "Example\nChallenge ID: BP20261118\nSPOILER — SOLUTION BELOW"},
    ]
    rows = summarize(posts)
    for date in ("2026-11-17", "2026-11-18"):
        for slot in ("base", "N1"):
            row = next(x for x in rows if x["date"] == date and x["slot"] == slot)
            assert row["number_of_matching_buffer_posts"] == 1
            assert len(row["buffer_posts"]) == 1
    assert sum(x["number_of_matching_buffer_posts"] > 1 for x in rows) == 0
