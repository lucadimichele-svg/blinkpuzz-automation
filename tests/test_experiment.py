from collections import Counter
from datetime import date
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))

from experiment import ARMS, TEST, LENGTH, REVEAL_AT, assignment, build, plan, render, validate
from schedule import slots_for


def test_balanced_experiment_exactly_12():
    assert len(TEST)==12
    assert Counter(row[2] for row in TEST)=={'A':3,'B':3,'C':3,'D':3}
    assert all(Counter(row[3] for row in TEST if row[2]==arm)=={'sequence':1,'math':1,'logic':1} for arm in ARMS)
    assert len({row[:2] for row in TEST})==len(TEST)
    assert all(row[1] in dict(slots_for(date.fromisoformat(row[0]))) for row in TEST)
    assert all(date(2026,11,15)<=date.fromisoformat(row[0])<=date(2026,11,18) for row in TEST)
    assert assignment('2026-11-14','B1') is None


def test_answers_are_correct_distinct_and_reproducible():
    puzzles=[build(day,slot) for day,slot,_,_ in TEST]
    assert len({(p['family'],str(p['display'])) for p in puzzles})==12
    for p in puzzles:
        assert p==build(p['day'],p['slot'])
        assert validate(p)
        assert p['duration_seconds']==12
        arm=ARMS[p['arm']]
        assert p['easy']==(arm['difficulty']=='easy')
        assert p['in_video_reveal']==arm['in_video_reveal']
        assert p['choices_enabled']==arm['choices']
        if arm['choices']:
            assert p['correct_letter'] in 'ABC'
            assert len(p['options'])==3


def test_mobile_canvas_and_on_screen_reveal_arms():
    for day,slot,_,_ in TEST:
        p=build(day,slot)
        before=render(p,REVEAL_AT-1)
        after=render(p,REVEAL_AT)
        assert before.size == after.size == (1080,1920)
        assert before.getpixel((540,1600))!=after.getpixel((540,1600))


def test_experiment_is_exploratory_and_not_misreported_as_instagram_insights():
    data=plan()
    assert len(data['slots'])==12
    assert 'not statistically conclusive' in data['note']
    assert 'comments_per_100_views' in data['primary_metrics']