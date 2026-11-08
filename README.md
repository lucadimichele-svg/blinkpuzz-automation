# BlinkPuzz – Automated English Puzzle Reels

Standalone, zero-subscription-cost video-generation pipeline for **@blinkpuzz**.
The Vibsnaxx project is separate and never targeted.

## Status
- Original English vertical puzzle Reel generator: installed.
- GitHub Actions: configured for a rolling 7-day video buffer (06:17 UTC daily, also push/manual).
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
7. Only when unlocked: schedule eligible clips for **19:30 Europe/Berlin**. Reject any other account/channel. Reject duplicate challenge markers.

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
