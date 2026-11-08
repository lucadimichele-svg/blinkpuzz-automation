import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from generate import build_puzzle


def test_a_year_of_consistent_answers():
    start = date(2026, 1, 1)
    fingerprints = set()
    for n in range(365):
        day = (start + timedelta(days=n)).isoformat()
        p = build_puzzle(day)
        assert p['answer']
        if p['kind'] == 'grid':
            r, c = p['cell']
            assert p['grid'][r][c] == p['odd']
            assert sum(item == p['odd'] for row in p['grid'] for item in row) == 1
            assert p['answer'] == f'{chr(65+c)}{r+1}'
            fingerprint = (p['normal'], p['odd'], p['cell'])
        elif p['kind'] == 'sequence':
            a, b, c, _ = p['items']
            assert int(p['answer']) == c + (c-b) + (c-b-(b-a))
            fingerprint = tuple(p['items'])
        else:
            x, y, z = p['x'], p['y'], p['z']
            assert p['values'] == [2*x, x+y, y+z]
            assert int(p['answer']) == z
            fingerprint = tuple(p['values'])
        fingerprints.add((p['kind'], fingerprint))
    assert len(fingerprints) > 100


def test_determinism():
    assert build_puzzle('2026-11-09') == build_puzzle('2026-11-09')
