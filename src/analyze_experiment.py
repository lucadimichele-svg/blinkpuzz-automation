#!/usr/bin/env python3
"""Descriptive 48-hour BlinkPuzz experiment summary from actual Instagram Insights.

This does not estimate unseen metrics from Buffer scheduling or Reel cover counters.
Populate docs/experiment_results_template.csv from screenshots or account Insights.
N=3 per arm is exploratory and does not prove causality.
"""
import csv
from collections import defaultdict
from pathlib import Path

INPUT = Path('docs/experiment_results_template.csv')
ARMS = {
    'A':'Easy + in-Reel reveal',
    'B':'Medium + in-Reel reveal',
    'C':'Medium + no reveal (caption spoiler)',
    'D':'Medium + 3 choices + no reveal (caption spoiler)',
}
NUMERIC = ('views_48h','avg_watch_seconds','comments_48h','likes_48h','shares_48h','follows_48h')

def read_rows(path=INPUT):
    with open(path,encoding='utf-8',newline='') as f:
        records=list(csv.DictReader(f))
    for row in records:
        for key in NUMERIC:
            if row[key].strip():
                value=float(row[key])
                if value<0: raise ValueError('Negative Insights value: '+key)
                row[key]=value
            else:
                row[key]=None
    return records

def summarize(rows):
    report=[]
    for arm,label in ARMS.items():
        selected=[row for row in rows if row['arm']==arm]
        complete=[row for row in selected if all(row[k] is not None for k in NUMERIC)]
        views=sum(row['views_48h'] for row in complete)
        n=len(complete)
        report.append({
            'arm':arm,'label':label,'complete':n,'total':len(selected),
            'mean_views_48h':round(views/n,1) if n else None,
            'mean_watch_seconds':round(sum(row['avg_watch_seconds'] for row in complete)/n,2) if n else None,
            'comments_per_100_views':round(100*sum(row['comments_48h'] for row in complete)/views,2) if views else None,
            'likes_per_100_views':round(100*sum(row['likes_48h'] for row in complete)/views,2) if views else None,
            'shares_per_100_views':round(100*sum(row['shares_48h'] for row in complete)/views,2) if views else None,
            'follows_per_100_views':round(100*sum(row['follows_48h'] for row in complete)/views,2) if views else None
        })
    return report

if __name__=='__main__':
    rows=read_rows()
    print('EXPLORATORY ONLY; 12 Reels total; compare metrics at the SAME 48-hour age.\n')
    for result in summarize(rows):
        print(result)
    if any(result['complete']<result['total'] for result in summarize(rows)):
        print('\nIncomplete measurements: do NOT select a winning arm yet.')
