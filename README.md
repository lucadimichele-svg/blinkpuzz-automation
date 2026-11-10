# BlinkPuzz – Automated English Puzzle Reels

Standalone, zero-subscription-cost video-generation pipeline for **@blinkpuzz**.
The Vibsnaxx project is separate and never targeted.

## Status
- Original English vertical puzzle Reel generator: installed.
- GitHub Actions: daily rolling seven-day generation buffer, plus separate automated Buffer queue refills throughout each day.
- GitHub Pages: choose **Settings → Pages → Source: GitHub Actions** to activate hosting. This step needs a one-time owner action.
- Buffer API key: stored in **Actions secret `BUFFER_API_KEY`** by the owner. Do not paste secrets into chat or source files.
- Instagram publishing: **OFF** until `AUTO_PUBLISH=true` repository **variable** is explicitly set *after* testing. No live posts confirmed.

## Automatic workflow
1. Check that generated puzzles have unique and valid answers.
2. Make the next 7 days of 1080x1920, 8-second Reels.
3. Validate the actual H.264/AAC output.
4. Commit the generated MP4/JPEG/JSON under `docs/media/`.
5. Deploy `docs/` on GitHub Pages after Pages is enabled.
6. Verify the Buffer API connection for the **exact** Instagram channel `@blinkpuzz`. This step schedules nothing until `AUTO_PUBLISH` is set to `true`.
7. After explicit publishing activation, schedule only **@blinkpuzz** and reject duplicate challenge markers.

## Publishing cadence — Option B
- **November 10–16, 2026:** four Reels per day. November 10 at 16:30, 18:00, 19:30 and 21:30; subsequent boost days at 10:00, 14:00, 19:30 and 21:30 (Europe/Berlin).
- **From November 17, 2026 onward:** two Reels per day, at 12:00 and 19:30.
- The original one-per-day Reel remains the 19:30 slot. Existing scheduled posts are kept. Each additional Reel has its own stable date-and-slot ID.
- **Buffer Free:** only ten posts can be in its queue at a time. The light-weight GitHub Actions workflow `blinkpuzz-refill.yml` refills freed slots automatically; it cannot publish posts retroactively or guarantee successful Instagram delivery.
- Refill uses a single publishing owner; production, queueing, and status jobs run separately with shared queue concurrency to avoid double publishing.

No manual organization or channel IDs are required: the publisher discovers the exact @blinkpuzz Instagram channel via Buffer API and fails closed if it is ambiguous or not connected.

## Activation checklist
- [ ] Owner sets GitHub Pages source to GitHub Actions.
- [ ] First full **Actions** run succeeds and displays *Verified Buffer account @blinkpuzz* (check-only mode).
- [ ] The hosted mp4 URL `https://lucadimichele-svg.github.io/blinkpuzz-automation/media/YYYY-MM-DD.mp4` loads publicly.
- [ ] Verify that `@blinkpuzz` is the intended professional Instagram channel and automatic publishing is available.
- [ ] Set Actions repository variable `AUTO_PUBLISH=true` to enable queuing. **This is intentionally a separate safety switch.**
- [ ] Verify the first Reel inside Buffer's queue and then confirm it actually appears on Instagram at its scheduled time.
- [ ] Review failures periodically. A queue entry is not proof of a published post.

## Local development
```bash
sudo apt-get install ffmpeg fonts-lato fonts-dejavu-core
python -m pip install -r requirements.txt pytest
pytest -q tests
python src/batch.py
python src/validate.py docs/media
```

## Limitations
The system is not fully live-tested. GitHub scheduled workflows can be delayed or skipped, Buffer and Instagram limits and availability may change, and the Free plan has finite queue slots. Verify runs and publication outcomes. Only original assets are used.
