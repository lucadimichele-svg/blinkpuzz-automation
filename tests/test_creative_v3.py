from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))

from creative_v3 import (KINDS, THEMES, build_puzzle, validate_puzzle, render)
from generate import make_reel as dispatch_make_reel


def test_creative_v3_answers_and_uniqueness_for_a_year():
    start=date(2026,11,17)
    formats=set()
    for offset in range(365):
        day=(start+timedelta(days=offset)).isoformat()
        group=[build_puzzle(day, variant) for variant in ('','B1','B2','B3','N1')]
        assert len({p['kind'] for p in group[:4]}) == 4
        assert len({p['kind'] for p in (group[0],group[4])}) == 2
        for p in group:
            formats.add(p['kind'])
            assert validate_puzzle(p) is True
            assert p['answer']
            assert p['creative_version']=='v3'
        assert group[0] == build_puzzle(day)
    assert formats == set(KINDS) == set(THEMES)


def test_poster_stage_is_legible_and_vertical():
    for i in range(12):
        day=(date(2026,11,17)+timedelta(days=i)).isoformat()
        p=build_puzzle(day)
        image=render(p,0)
        reveal=render(p,7)
        assert image.size==(1080,1920)
        assert reveal.size==(1080,1920)
        assert image.getpixel((540,1500)) != reveal.getpixel((540,1500))


def test_legacy_assets_are_not_retargeted():
    from generate import build_puzzle as original
    p=original('2026-11-10','B2')
    assert p['kind'] in ('grid','sequence','equations')
