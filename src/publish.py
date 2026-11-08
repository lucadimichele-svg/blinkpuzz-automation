#!/usr/bin/env python3
"""Schedule original BlinkPuzz Instagram Reels via Buffer.

Safety rules: never target an account other than @blinkpuzz, never publish until
AUTO_PUBLISH=true, and never publish a clip whose URL cannot be accessed.
Uses Buffer's public GraphQL API, and needs only BUFFER_API_KEY as a secret.
"""
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import quote

import requests

BUFFER_ENDPOINT = "https://api.buffer.com"
EXPECTED_HANDLE = "blinkpuzz"
TIMEZONE = ZoneInfo("Europe/Berlin")
MEDIA_URL = "https://lucadimichele-svg.github.io/blinkpuzz-automation/media"
TARGET_LOCAL_HOUR = 19
TARGET_LOCAL_MINUTE = 30


def gql(query, token, variables=None):
    response = requests.post(
        BUFFER_ENDPOINT,
        json={"query": query, "variables": variables or {}},
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        timeout=35,
    )
    response.raise_for_status()
    body = response.json()
    if body.get("errors"):
        raise RuntimeError("Buffer query failed: " + json.dumps(body["errors"])[:600])
    return body["data"]


def discover_blinkpuzz(token):
    """Read all organizations; exact-match the Instagram handle and reject ambiguity."""
    data = gql("query { account { organizations { id name } } }", token)
    orgs = data["account"]["organizations"]
    matches = []
    query = """query Channels($org: OrganizationId!) {
      channels(input: {organizationId: $org}) {
        id name service isLocked isDisconnected isQueuePaused
      }
    }"""
    for org in orgs:
        channels = gql(query, token, {"org": org["id"]})["channels"]
        for channel in channels:
            if channel["name"].strip().lower().lstrip("@") == EXPECTED_HANDLE:
                if str(channel["service"]).lower() != "instagram":
                    raise RuntimeError("@blinkpuzz exists but is not an Instagram channel")
                matches.append((org["id"], channel))
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one Instagram channel @{EXPECTED_HANDLE}, got {len(matches)}"
        )
    org, channel = matches[0]
    if channel["isLocked"] or channel["isDisconnected"] or channel["isQueuePaused"]:
        raise RuntimeError("BlinkPuzz Buffer channel is locked, disconnected or paused")
    return org, channel["id"]


def list_posts(token, org, channel):
    query = """query Posts($org: OrganizationId!, $channel: ChannelId!, $cursor: String) {
      posts(first: 100, after: $cursor, input: {
        organizationId: $org, filter: {channelIds: [$channel]}
      }) {
        edges { node { id text status dueAt } }
        pageInfo { hasNextPage endCursor }
      }
    }"""
    posts, cursor = [], None
    for _ in range(10):
        data = gql(query, token, {"org": org, "channel": channel, "cursor": cursor})["posts"]
        posts += [edge["node"] for edge in data["edges"]]
        if not data["pageInfo"]["hasNextPage"]:
            return posts
        cursor = data["pageInfo"]["endCursor"]
        if not cursor:
            raise RuntimeError("Pagination failed: missing cursor")
    raise RuntimeError("More than 1000 channel posts; refusing to risk duplicate publication")


def media_ready(url):
    for i in range(12):
        try:
            resp = requests.get(url, stream=True, timeout=20, headers={"Range": "bytes=0-1023"})
            status = resp.status_code
            mime = resp.headers.get("Content-Type", "").lower()
            resp.close()
            if status in (200, 206) and ("video/" in mime or "octet-stream" in mime):
                return True
        except requests.RequestException:
            pass
        if i < 11:
            time.sleep(10)
    return False


def add_post(token, channel, caption, media, when):
    mutation = """mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess { post { id status dueAt } }
        ... on MutationError { message }
      }
    }"""
    data = gql(mutation, token, {"input": {
        "channelId": channel,
        "text": caption,
        "schedulingType": "automatic",
        "mode": "customScheduled",
        "dueAt": when,
        "metadata": {"instagram": {"type": "reel", "shouldShareToFeed": True}},
        "assets": [{"video": {"url": media, "metadata": {"thumbnailOffset": 2000}}}],
    }})["createPost"]
    if not data.get("post"):
        raise RuntimeError("Buffer refused scheduling: " + str(data.get("message", data)))
    return data["post"]


def main():
    token = os.getenv("BUFFER_API_KEY", "")
    if not token:
        print("BUFFER_API_KEY secret not set", file=sys.stderr)
        return 1
    org, channel = discover_blinkpuzz(token)
    print(f"Verified Buffer account @{EXPECTED_HANDLE}; no other channels will be used.")
    if os.getenv("AUTO_PUBLISH", "").lower() != "true":
        print("CHECK ONLY: Auto-publishing disabled. No new posts created.")
        return 0

    posts = list_posts(token, org, channel)
    markers = set()
    for post in posts:
        for line in (post["text"] or "").splitlines():
            if line.startswith("Challenge ID: "):
                markers.add(line.split(": ", 1)[1].strip())
    failed = [post for post in posts if str(post["status"]).lower() in ("error", "failed")
              and "Challenge ID: BP" in (post["text"] or "")]
    if failed:
        raise RuntimeError(f"{len(failed)} failed BlinkPuzz posts must be investigated")

    active = sum(str(post["status"]).lower() in ("buffer", "scheduled", "sending")
                 for post in posts)
    room = max(0, 7 - active)
    now = datetime.now(TIMEZONE)
    added = 0
    for manifest in sorted(Path("docs/media").glob("*.json")):
        meta = json.loads(manifest.read_text(encoding="utf-8"))
        day = datetime.fromisoformat(meta["date"]).date()
        local = datetime(day.year, day.month, day.day,
                         TARGET_LOCAL_HOUR, TARGET_LOCAL_MINUTE, tzinfo=TIMEZONE)
        if not now < local <= now + timedelta(days=10):
            continue
        marker = "BP" + meta["date"].replace("-", "")
        if marker in markers:
            continue
        if added >= room:
            break
        url = MEDIA_URL + "/" + quote(meta["video"])
        if not media_ready(url):
            raise RuntimeError("Hosted video not publicly accessible: " + url)
        published = add_post(token, channel, meta["caption"], url,
                             local.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z"))
        print(f"Scheduled {marker} for {local.isoformat()}: Buffer post {published['id']}")
        added += 1
    print(f"Scheduled {added} new posts; {active + added}/7 queue slots occupied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
