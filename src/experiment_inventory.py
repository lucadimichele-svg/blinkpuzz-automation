#!/usr/bin/env python3
"""Produce the fixed 12 controlled-experiment assets safely and only once.

Every experiment MP4 has a separate -EXP filename; old media remain intact.
Publishing is handled solely by src/publish.py after Pages deployment.
"""
from pathlib import Path
from experiment import TEST, make_reel, plan
import json

MEDIA = Path('docs/media')
MEDIA.mkdir(parents=True,exist_ok=True)
Path('docs/experiment_plan.json').write_text(json.dumps(plan(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
created=0
for day,slot,arm,family in TEST:
    stem=day+('' if slot=='base' else '-'+slot)+'-EXP'
    filenames=[MEDIA/(stem+extension) for extension in ('.mp4','.jpg','.json')]
    if all(f.is_file() and f.stat().st_size>0 for f in filenames):
        print('EXPERIMENT SKIP',stem,flush=True)
        continue
    if any(f.is_file() for f in filenames):
        raise RuntimeError(f'Partial experiment asset: {stem}; refusing to overwrite')
    print(f'EXPERIMENT PRODUCE {stem} arm={arm} family={family}',flush=True)
    make_reel(day,slot,MEDIA)
    created+=1
print(f'Experiment assets created this run: {created}; total fixed slots: {len(TEST)}')
