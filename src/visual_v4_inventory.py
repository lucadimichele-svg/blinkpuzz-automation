#!/usr/bin/env python3
"""Build separate V4 assets for all future BlinkPuzz slots in 7-day horizon.

Previously generated videos and already-queued Buffer posts are never replaced.
"""
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from schedule import slots_for, planned_at
from visual_v4 import make_reel

TODAY = datetime.now(ZoneInfo('Europe/Berlin')).date()
DIR = Path('docs/media')
DIR.mkdir(parents=True,exist_ok=True)
created=0
for offset in range(1,8):
    day=TODAY+timedelta(days=offset)
    if day < date(2026,11,23):continue
    for slot,clock in slots_for(day):
        if planned_at(day,clock) <= datetime.now(ZoneInfo('Europe/Berlin'))+timedelta(minutes=20):continue
        variant='' if slot=='base' else slot
        stem=day.isoformat()+('-'+variant if variant else '')+'-V4'
        fs=[DIR/(stem+extension) for extension in ('.mp4','.jpg','.json')]
        if all(x.exists() and x.stat().st_size>0 for x in fs):
            print('V4 SKIP '+stem,flush=True);continue
        if any(x.exists() for x in fs):
            raise RuntimeError(f'Partial assets {stem}: investigate rather than overwrite')
        print('V4 GENERATE '+stem,flush=True)
        make_reel(day.isoformat(),DIR,variant=variant)
        created+=1
print('V4 assets generated:',created)