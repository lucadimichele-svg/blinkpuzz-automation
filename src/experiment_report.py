#!/usr/bin/env python3
"""Read-only @blinkpuzz Buffer experiment queue audit. No IG engagement access.

Runs only with BUFFER_API_KEY available inside GitHub Actions secrets.
Never writes credentials or commenter data to the public repository.
"""
import json
import os
from datetime import datetime,timezone
from pathlib import Path

# Keep this audit lightweight: the queue-refill workflow installs requests,
# not Pillow. Read the static experiment plan instead of importing the
# video rendering module (which depends on Pillow).
from publish import discover_blinkpuzz, list_posts
from schedule import challenge_id

PLAN = json.loads(Path('docs/experiment_plan.json').read_text(encoding='utf-8'))
TEST = [(r['date'], r['slot'], r['arm'], r['type']) for r in PLAN['slots']]


def summarize(posts):
    rows=[]
    for day,slot,arm,family in TEST:
        marker=challenge_id(datetime.fromisoformat(day).date(),slot)
        found=[]
        for post in posts:
            if f'Challenge ID: {marker}' in (post.get('text') or ''):
                found.append(post)
        # Challenge ID is unique; multiple matches mean a queue duplication.
        states=[]
        for post in found:
            caption=post.get('text') or ''
            states.append({'buffer_status':str(post.get('status','unknown')),
                           'due_at':post.get('dueAt'),
                           'is_experiment_asset':'SPOILER — SOLUTION BELOW' in caption})
        rows.append({'date':day,'slot':slot,'arm':arm,'family':family,
                     'challenge_id':marker,'buffer_posts':states,
                     'number_of_matching_buffer_posts':len(states)})
    return rows


def main():
    token=os.getenv('BUFFER_API_KEY','')
    if not token: raise RuntimeError('Missing Buffer API token (must be supplied as GitHub secret)')
    org,channel=discover_blinkpuzz(token)
    posts=list_posts(token,org,channel)
    rows=summarize(posts)
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'account':'@blinkpuzz','experiment_id':'BP-2026-11-ABCD',
            'count':len(rows),
            'experiment_asset_buffer_records':sum(sum(x['is_experiment_asset'] for x in r['buffer_posts']) for r in rows),
            'duplicate_slot_count':sum(r['number_of_matching_buffer_posts']>1 for r in rows),
            'rows':rows,
            'note':'Buffer queue/post statuses only, NOT verified Instagram delivery or reach/engagement metrics. Instagram Insights must be supplied separately.'}
    path=Path('docs/experiment_status.json')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('BlinkPuzz experiment queue audit:',len(rows),'slots;',result['experiment_asset_buffer_records'],'experiment records;',result['duplicate_slot_count'],'duplicates')

if __name__=='__main__':
    main()