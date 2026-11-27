# BlinkPuzz 2.0

English-language puzzle Reels for editorial review. The engine, scene library, scoring, sound synthesis, encoding and verification run locally. Python 3.12, Pillow, DejaVu Sans/Serif/Mono (including the condensed faces), ffmpeg with libx264 and AAC, and ffprobe are the runtime dependencies. On Debian or Ubuntu install `ffmpeg fonts-dejavu-core fonts-dejavu-extra`. Install Python dependencies into a virtual environment.

```bash
python -m pip install -r requirements.txt pytest
python -m blinkpuzz2.cli catalog
python -m blinkpuzz2.cli generate --engine laser --seed 123 --difficulty medium --out build/v2/spec.json
python -m blinkpuzz2.cli validate --spec build/v2/spec.json
python -m blinkpuzz2.cli render --spec build/v2/spec.json --out build/v2/demo
python -m blinkpuzz2.cli pilots --count 20 --seed 20261127 --out build/v2/pilots
python -m blinkpuzz2.cli qa --folder build/v2/pilots
```

Open `build/v2/pilots/contact_sheet.jpg` to browse the collection. The matching numbered MP4 contains the playable problem and a solution replay. The proof sheet shows all final answer frames. Each index entry links the video, cover, full spec, proof JSON and proof image. The spec includes the public rules, a text alternative, a reproducible seed and both distractors' difficulty measurements. `additional_specs.json` contains fifty further validated puzzles. `quality.json` records actual decoded frames and streams. The shareable local bundle is `build/v2/pilots.zip`.

| Reference | Contents |
| --- | --- |
| [Decision log](DECISIONS.md) | Legacy audit and build sequence |
| [Architecture](architecture.md) | Contracts, retries, timing, scene production and licensed local art |
| [Mechanics](mechanics.md) | Ten games, oracles and proof interpretation |
| [Acceptance report](quality.md) | Actual benchmark results, media checks, pilot table and open human validation |
| [Rollout](rollout.md) | Offline review, measurement, retention and approval boundary |

For a controlled no-reveal variant, pass `--no-reveal` to `render` with its own output directory. The full proof remains available for editorial review. `--world` accepts the pair of compatible sets listed by `catalog`.

```bash
python -m pytest -q tests tests_v2
BLINKPUZZ_FULL_RENDER=1 python -m pytest -q tests_v2/test_collection.py
```

The second command builds a fresh full-size benchmark in pytest temporary storage by default. Set `BLINKPUZZ_PILOT_DIR=build/v2/pilots` to retain the artifacts. Reusing an existing matching output runs QA again. A different build requires its own destination.
