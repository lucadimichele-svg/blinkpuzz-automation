from datetime import date,timedelta
from collections import Counter
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from visual_v4 import KINDS,build,validate,draw_reel,draw_cover

def test_six_original_templates_and_resolved_answers():
    day=date(2026,11,23)
    types=set()
    for i in range(120):
        text=(day+timedelta(days=i)).isoformat()
        p=build(text)
        types.add(p['style'])
        assert validate(p)
        assert p==build(text)
        assert build(text,'N1')['kind'] != p['kind']
    assert types==set(KINDS)

def test_independent_cover_no_timer():
    for i in range(6):
        p=build((date(2026,11,23)+timedelta(days=i)).isoformat())
        cover=draw_cover(p)
        video=draw_reel(p,0)
        assert cover.size==video.size==(1080,1920)
        assert cover.getpixel((540,1660))!=video.getpixel((540,1660))
        assert draw_reel(p,7).size==(1080,1920)