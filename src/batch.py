#!/usr/bin/env python3
"""Maintain a rolling 7-day media buffer; retain at most 45 days of hosted clips."""
from datetime import datetime, timedelta, date
from pathlib import Path
from zoneinfo import ZoneInfo
from generate import make_reel

DIR=Path('docs/media')
DIR.mkdir(parents=True, exist_ok=True)
now=datetime.now(ZoneInfo('Europe/Berlin')).date()
for offset in range(7):
    day=(now+timedelta(days=offset)).isoformat()
    trio=[DIR/(day+suffix) for suffix in ('.mp4','.jpg','.json')]
    if all(p.exists() for p in trio):
        print(f'SKIP {day} already generated')
        continue
    print('GENERATE', day)
    make_reel(day, DIR)

for json_path in DIR.glob('*.json'):
    try:
        day=date.fromisoformat(json_path.stem)
    except ValueError:
        continue
    if day < now-timedelta(days=45):
        for suffix in ('.mp4','.jpg','.json'):
            (DIR/(json_path.stem+suffix)).unlink(missing_ok=True)
        print('PRUNE',day)
