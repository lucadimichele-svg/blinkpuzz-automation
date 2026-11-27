import os
import socket
from pathlib import Path

import pytest

from blinkpuzz2.catalog import ENGINES
from blinkpuzz2.collection import build, read
from blinkpuzz2.core import generate


def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("Network access during local production")

    monkeypatch.setattr(socket.socket, "connect", deny)


def test_offline_smoke(tmp_path, monkeypatch):
    offline(monkeypatch)
    spec, _ = generate(ENGINES["laser"], 123)
    result = build(tmp_path / "pilot", single=spec, reveal=False)
    assert (
        result["count"] == 1 and result["pilot_checks"][0]["decoded_video"]["frames_compared"] > 200
    )
    assert read(tmp_path / "pilot/index.json")["pilots"][0]["storyboard"]["reveal_seconds"] == 0


@pytest.mark.skipif(
    os.getenv("BLINKPUZZ_FULL_RENDER") != "1", reason="opt-in full native-resolution benchmark"
)
def test_full_collection(tmp_path, monkeypatch):
    offline(monkeypatch)
    folder = Path(os.getenv("BLINKPUZZ_PILOT_DIR", str(tmp_path / "pilots")))
    report = build(folder, 20, 20261127)
    assert (report["count"], report["world_count"], report["unique_boards"]) == (20, 6, 70)
    assert all(
        r["decoded_video"]["frames_compared"] == 24 * r["duration"] for r in report["pilot_checks"]
    )
    assert len(list(folder.glob("*.mp4"))) == 20
    assert folder.with_suffix(".zip").is_file()
