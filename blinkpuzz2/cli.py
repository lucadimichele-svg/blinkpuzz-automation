import argparse
import json
from pathlib import Path

from .catalog import ENGINES
from .collection import build, qa, read, safe_output
from .core import LEVELS, PuzzleSpec, generate, validate
from .planning import import_insights


def main():
    ap = argparse.ArgumentParser(description="Offline BlinkPuzz production")
    subs = ap.add_subparsers(dest="action", required=True)
    subs.add_parser("catalog")
    gen = subs.add_parser("generate")
    gen.add_argument("--engine", choices=ENGINES, required=True)
    gen.add_argument("--seed", type=int, required=True)
    gen.add_argument("--difficulty", choices=LEVELS, default="medium")
    gen.add_argument("--out", type=Path, required=True)
    val = subs.add_parser("validate")
    val.add_argument("--spec", type=Path, required=True)
    ren = subs.add_parser("render")
    ren.add_argument("--spec", type=Path, required=True)
    ren.add_argument("--world")
    ren.add_argument("--no-reveal", action="store_true")
    ren.add_argument("--out", type=Path, required=True)
    pil = subs.add_parser("pilots")
    pil.add_argument("--seed", type=int, default=20261127)
    pil.add_argument("--count", type=int, default=20)
    pil.add_argument("--out", type=Path, default=Path("build/v2/pilots"))
    for parser in (pil, ren):
        parser.add_argument(
            "--scene-pack", type=Path, help="Optional local backplate credit manifest"
        )
    check = subs.add_parser("qa")
    check.add_argument("--folder", type=Path, required=True)
    ins = subs.add_parser("insights")
    ins.add_argument("--folder", type=Path, required=True)
    ins.add_argument("--csv", type=Path, required=True)
    a = ap.parse_args()
    if a.action == "catalog":
        result = {
            k: {"objective": e.title, "rules": e.rules, "worlds": e.worlds}
            for k, e in ENGINES.items()
        }
    elif a.action == "generate":
        spec, rejected = generate(ENGINES[a.engine], a.seed, a.difficulty)
        spec.save(safe_output(a.out))
        result = {"puzzle_id": spec.puzzle_id, "rejected": rejected}
    elif a.action == "validate":
        r = validate(PuzzleSpec.read(a.spec), ENGINES)
        result = {"winners": r.winners, "explanation": r.explanation, "witness": r.witness}
    elif a.action == "insights":
        result = import_insights(a.csv, read(a.folder / "index.json")["pilots"])
    else:
        if a.action == "qa":
            report = qa(a.folder)
        elif a.action == "pilots":
            report = build(a.out, a.count, a.seed, scene_pack=a.scene_pack)
        else:
            report = build(
                a.out,
                single=PuzzleSpec.read(a.spec),
                world=a.world,
                reveal=not a.no_reveal,
                scene_pack=a.scene_pack,
            )
        result = {k: v for k, v in report.items() if k != "pilot_checks"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
