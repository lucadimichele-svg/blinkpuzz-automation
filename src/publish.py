#!/usr/bin/env python3
"""Queue BlinkPuzz Reels through Buffer only after explicit activation.

Publication is disabled unless AUTO_PUBLISH=true and the intended Instagram
channel is verified. The Vibsnaxx account is always blocked.
"""
import json
import os
from pathlib import Path
import sys
import time
from datetime import date, timedelta
from urllib.parse import quote
import requests

API = 'https://api.buffer.com'


def gql(query, token, variables=None):
    r = requests.post(
        API, json={'query': query, 'variables': variables or {}},
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        timeout=30)
    r.raise_for_status()
    payload = r.json()
    if payload.get('errors'):
        raise RuntimeError('Buffer GraphQL: ' + json.dumps(payload['errors'])[:750])
    return payload['data']


def get_posts(token, org, channel):
    query = """query ListPosts($org: OrganizationId!, $channel: ChannelId!, $after: String) {
      posts(first: 50, after: $after, input: { organizationId: $org,
        filter: {channelIds: [$channel], status: [scheduled, sent, sending, error]}}) {
        edges { node {id text status dueAt} }
        pageInfo {hasNextPage endCursor}
      }
    }"""
    allposts = []
    after = None
    for _ in range(15):
        data = gql(query, token, {'org': org, 'channel': channel, 'after': after})
        result = data['posts']
        allposts.extend(e['node'] for e in result['edges'])
        if not result['pageInfo']['hasNextPage']:
            return allposts
        after = result['pageInfo']['endCursor']
        if not after:
            raise RuntimeError('Buffer pagination returned empty cursor')
    raise RuntimeError('More than 750 posts returned; refusing to guess deduplication')


def check_channel(token, channel):
    query = """query Channel($channel: ChannelId!) { channel(input: {id: $channel}) {
      id name service isDisconnected isLocked isQueuePaused
    }}"""
    data = gql(query, token, {'channel': channel})['channel']
    if not data or str(data.get('service', '')).lower() != 'instagram':
        raise RuntimeError('Channel must be Instagram. Publishing disabled.')
    name = str(data.get('name', '')).lower().strip('@')
    if 'vibsnaxx' in name:
        raise RuntimeError('Safety stop: Vibsnaxx must never be targeted by BlinkPuzz.')
    if any(data.get(key) for key in ('isDisconnected', 'isLocked', 'isQueuePaused')):
        raise RuntimeError('Instagram channel disconnected/locked/paused')
    expected = os.getenv('EXPECTED_IG_HANDLE', 'blinkpuzz').lstrip('@').lower()
    if name != expected:
        raise RuntimeError(f'Expected Instagram channel @{expected}, got @{name}. STOP.')
    return name


def check_public_media(url, tries=1):
    for attempt in range(tries):
        try:
            r = requests.get(url, headers={'Range': 'bytes=0-2047'},
                             stream=True, timeout=16, allow_redirects=True)
            if r.status_code in (200, 206) and 'text/html' not in r.headers.get('Content-Type', '').lower():
                r.close()
                return True
            r.close()
        except requests.RequestException:
            pass
        if attempt+1 < tries:
            time.sleep(12)
    return False


def queue(token, channel, caption, url):
    mutation = """mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess { post { id dueAt status } }
        ... on MutationError { message }
      }
    }"""
    data = gql(mutation, token, {'input': {
        'text': caption,
        'channelId': channel,
        'schedulingType': 'automatic',
        'mode': 'addToQueue',
        'metadata': {'instagram': {'type': 'reel', 'shouldShareToFeed': True}},
        'assets': [{'video': {'url': url, 'metadata': {'thumbnailOffset': 1000}}}]
    }})['createPost']
    if 'post' not in data:
        raise RuntimeError(f'Buffer rejected post: {data.get("message", data)}')
    return data['post']


def main():
    if os.getenv('AUTO_PUBLISH', '').lower() != 'true':
        print('Publishing disabled (AUTO_PUBLISH not true). Safe exit.')
        return 0
    token = os.getenv('BUFFER_API_KEY', '')
    org = os.getenv('BUFFER_ORGANIZATION_ID', '')
    channel = os.getenv('BUFFER_CHANNEL_ID', '')
    base = os.getenv('MEDIA_BASE_URL', '').rstrip('/')
    if not all((token, org, channel, base)):
        print('Publishing gated: missing Buffer credentials or MEDIA_BASE_URL.', file=sys.stderr)
        return 1
    if not base.startswith('https://'):
        raise ValueError('MEDIA_BASE_URL must use HTTPS')
    name = check_channel(token, channel)
    posts = get_posts(token, org, channel)
    scheduled = [p for p in posts if p['status'] in ('scheduled', 'sending')]
    errors = [p for p in posts if p['status'] == 'error' and 'Challenge ID: BP' in p['text']]
    if errors:
        print(f'WARNING: {len(errors)} failed BlinkPuzz posts require inspection', file=sys.stderr)
        return 2
    known = set()
    for p in posts:
        for line in p['text'].splitlines():
            if line.startswith('Challenge ID: '):
                known.add(line.split(': ', 1)[1])
    max_queue = int(os.getenv('MAX_QUEUED_POSTS', '7'))
    slots = max(0, min(10, max_queue) - len(scheduled))
    if slots == 0:
        print(f'@{name}: queue full ({len(scheduled)} posts).')
        return 0
    today = date.today()
    files = sorted(Path('docs/media').glob('*.json'))
    count = 0
    for path in files:
        data = json.loads(path.read_text(encoding='utf8'))
        day = date.fromisoformat(data['date'])
        if day < today-timedelta(days=2) or day > today+timedelta(days=12):
            continue
        marker = 'BP'+data['date'].replace('-', '')
        if marker in known:
            continue
        url = base+'/'+quote(data['video'])
        if not check_public_media(url, tries=10):
            raise RuntimeError('Hosted media not reachable yet: '+url)
        response = queue(token, channel, data['caption'], url)
        print(f'Queued {marker}: {response["id"]} for {response.get("dueAt")}')
        count += 1
        if count >= slots:
            break
    print(f'@{name}: {count} new posts queued; {len(scheduled)+count}/{max_queue} occupied.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
