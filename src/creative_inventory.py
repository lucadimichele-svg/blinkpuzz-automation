#!/usr/bin/env python3
"""Create independent v3 alternatives for not-yet-published Option B slots.

This never modifies existing MP4/JPEG/JSON files or Buffer posts.
The publisher prefers improved assets ONLY for future slots it hasn't queued.
"""
from datetime import date, datetime, timedelta
from pathlib import Path

from creative_v3 import make_reel
from schedule import BOOST_END, TZ, planned_at, slots_for

DIR=Path('docs/media')
DIR.mkdir(parents=True,exist_ok=True)
now=datetime.now(TZ)
UPGRADE_FROM=date(2026,11,11)
upgrade_count=0
for ordinal in range((BOOST_END-UPGRADE_FROM).days+1):
    day=UPGRADE_FROM+timedelta(days=ordinal)
    for slot,clock in slots_for(day):
        when=planned_at(day,clock)
        if when <= now+timedelta(minutes=20):
            continue
        variant='' if slot=='base' else slot
        stem=day.isoformat()+('-'+variant if variant else '')+'-V3'
        files=[DIR/(stem+suffix) for suffix in ('.mp4','.jpg','.json')]
        if all(f.exists() and f.stat().st_size>0 for f in files):
            continue
        print('UPGRADE (separate media; safe for queued posts)',stem,flush=True)
        make_reel(day.isoformat(),DIR,variant=variant,asset_label='V3')
        upgrade_count+=1
print(f'Created {upgrade_count} optional upgraded clips; originals preserved.')
