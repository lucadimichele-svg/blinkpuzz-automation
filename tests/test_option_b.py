from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schedule import BOOST_START, BOOST_END, slots_for, filename_stem, challenge_id, planned_items
from generate import build_puzzle


def test_option_b_exact_seven_days_then_two():
    assert BOOST_START == date(2026, 11, 10)
    assert BOOST_END == date(2026, 11, 16)
    for n in range(7):
        assert len(slots_for(BOOST_START + timedelta(days=n))) == 4
    assert len(slots_for(BOOST_END + timedelta(days=1))) == 2
    assert len(slots_for(BOOST_END + timedelta(days=100))) == 2


def test_slots_unique_and_ordered():
    all_slots = list(planned_items(BOOST_START, 12))
    ids = [challenge_id(day, slot) for day, slot, _, _ in all_slots]
    assert len(ids) == len(set(ids))
    assert all_slots == sorted(all_slots, key=lambda item: item[3])
    assert any(item[1] == 'base' for item in all_slots)
    assert all(challenge_id(day, 'base') == 'BP'+day.strftime('%Y%m%d')
               for day, _, _, _ in all_slots)


def test_legacy_names_unchanged():
    day = date(2026, 11, 12)
    assert filename_stem(day, 'base') == '2026-11-12'
    assert filename_stem(day, 'B1') == '2026-11-12-B1'
    assert challenge_id(day, 'B3') == 'BP20261112B3'


def test_variants_are_deterministic_and_distinct():
    for n in range(7):
        day = (BOOST_START + timedelta(days=n)).isoformat()
        puzzles = [build_puzzle(day, v) for v in ('', 'B1', 'B2', 'B3')]
        assert puzzles[0] == build_puzzle(day)
        assert puzzles[1] == build_puzzle(day, 'B1')
        assert len(set((p['kind'], p['answer'], str(p.get('grid', p.get('items', p.get('values')))))
                       for p in puzzles)) == 4
