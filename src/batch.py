#!/usr/bin/env python3
"""Keep a rolling 7-day inventory for the 4/day -> 2/day BlinkPuzz schedule."""
from datetime import datetime, timedelta, date
from pathlib import Path
from zoneinfo import ZoneInfo

from generate import make_reel
from schedule import filename_stem, slots_for

DIR = Path('docs/media')
DIR.mkdir(parents=True, exist_ok=True)
now = datetime.now(ZoneInfo('Europe/Berlin')).date()

generated = 0
for offset in range(7):
    day = now + timedelta(days=offset)
    for slot, _ in slots_for(day):
        stem = filename_stem(day, slot)
        files = [DIR / (stem + ext) for ext in ('.mp4', '.jpg', '.json')]
        if all(p.is_file() and p.stat().st_size > 0 for p in files):
            print(f'SKIP {stem}: already generated')
            continue
        print('GENERATE', stem, flush=True)
        make_reel(day.isoformat(), DIR, variant='' if slot == 'base' else slot)
        generated += 1

# Keep only the previous 45 days. Match both original YYYY-MM-DD
# and variant YYYY-MM-DD-B1 filenames.
removed = 0
for manifest in DIR.glob('*.json'):
    try:
        day = date.fromisoformat(manifest.stem[:10])
    except ValueError:
        continue
    if day < now - timedelta(days=45):
        for ext in ('.mp4', '.jpg', '.json'):
            (DIR / (manifest.stem + ext)).unlink(missing_ok=True)
        removed += 1

print(f'Generated {generated} clips; pruned {removed} old clips.')
