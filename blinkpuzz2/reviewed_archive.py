"""Restore the reviewed ZIP metadata and verify each member before Actions upload."""

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo


def verify_archive(source: Path, reference: Path, destination: Path) -> None:
    expected = json.loads(reference.read_text())
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
        staged = Path(temp) / "pilots.zip"
        with ZipFile(source) as src, ZipFile(staged, "w") as out:
            if sorted(src.namelist()) != sorted(expected["members"]):
                raise ValueError("ZIP inventory differs from the reviewed collection")
            for name, record in sorted(expected["members"].items()):
                payload = src.read(name)
                actual = hashlib.sha256(payload).hexdigest()
                if actual != record["sha256"]:
                    raise ValueError(f"Reviewed member mismatch: {name}, SHA-256 {actual}")
                modified = datetime.fromisoformat(record["timestamp"])
                info = ZipInfo(name, modified.timetuple()[:6])
                info.create_system = 3
                info.external_attr = 0o100600 << 16
                info.compress_type = ZIP_DEFLATED if name.endswith((".csv", ".json")) else ZIP_STORED
                out.writestr(info, payload)
        with staged.open("rb") as bundle:
            actual = hashlib.file_digest(bundle, "sha256").hexdigest()
        if actual != expected["sha256"]:
            raise ValueError(f"ZIP container differs from the reviewed archive: {actual}")
        os.replace(staged, destination)
        print(f"Verified {len(expected['members'])} members and archive SHA-256 {actual}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    verify_archive(args.source, args.reference, args.destination)
