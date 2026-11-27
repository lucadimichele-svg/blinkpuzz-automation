import json
from types import SimpleNamespace

import pytest
from PIL import Image

from blinkpuzz2.scenes.assets import backdrop, checksum, install


def test_local_asset_roundtrip_and_missing_file_fallback(tmp_path):
    src = tmp_path / "licensed.png"
    Image.new("RGB", (540, 960), "#665588").save(src)
    pack = tmp_path / "pack.json"
    record = {
        "file": src.name,
        "artist": "Test artist",
        "license": "CC0-1.0",
        "source": "Test collection",
        "sha256": checksum(src),
    }
    pack.write_text(json.dumps({"lab": record, "desk": {**record, "file": "absent.jpg"}}))
    out = tmp_path / "bundle"
    out.mkdir()
    credits = install(out, ["lab", "desk", "ruins"], pack)
    spec = SimpleNamespace(seed=456)
    assert backdrop(out, credits, spec, "lab").getpixel((18, 35)) == (102, 85, 136)
    assert credits["desk"]["fallback"] and backdrop(out, credits, spec, "desk").size == (1080, 1920)
    assert credits["ruins"]["kind"] == "procedural"
    (out / "assets/lab.png").write_bytes(b"incomplete")
    with pytest.raises(ValueError, match="changed"):
        backdrop(out, credits, spec, "lab")


@pytest.mark.parametrize(
    "change", [{"license": "unknown"}, {"file": "../outside.jpg"}, {"sha256": "wrong"}]
)
def test_invalid_art_is_rejected(tmp_path, change):
    image = tmp_path / "source.jpg"
    Image.new("RGB", (100, 100)).save(image)
    record = {
        "file": image.name,
        "license": "CC-BY-4.0",
        "artist": "Test artist",
        "source": "Test collection",
        "sha256": checksum(image),
        **change,
    }
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps({"lab": record}))
    with pytest.raises(ValueError):
        install(tmp_path, ["lab"], pack)
