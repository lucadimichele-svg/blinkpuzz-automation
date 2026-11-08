# BlinkPuzz — Automated English puzzle Reels

A free-to-run Instagram content-production pipeline. Uses original visuals and sounds; no paid generative AI services required.

## Status
- **Generation:** prepared and tested locally, activation on GitHub in progress.
- **Instagram publishing:** **OFF by default**. Needs a separate BlinkPuzz Instagram professional account connected to Buffer, a Buffer API key, and verified hosted video URLs.
- **Safety:** no interaction with the existing Vibsnaxx repository or account.

## Production process
A GitHub Actions workflow runs on a daily schedule, creates a rolling seven-day supply of portrait 1080 × 1920 H.264/AAC Reels, validates the results, commits assets into `docs/media` and (after Pages is enabled) deploys the media.

## To activate publishing later
1. Create/connect the new BlinkPuzz Instagram professional account to Buffer.
2. In **Settings → Pages**, set deployment source to **GitHub Actions**.
3. Set Actions variables `ENABLE_PAGES=true`, `MEDIA_BASE_URL=https://lucadimichele-svg.github.io/blinkpuzz-automation/media`, `BUFFER_ORGANIZATION_ID`, `BUFFER_CHANNEL_ID`, `EXPECTED_IG_HANDLE`.
4. Set Actions secret `BUFFER_API_KEY`. Never paste it into repository files.
5. Confirm that the media URLs are publicly accessible and the exact Buffer channel matches the intended account. Only then set `AUTO_PUBLISH=true`.

Buffer API integration is not yet tested against the user's credentials; a queued post does not prove that Instagram published it. Verify the first published Reel and check failures periodically.

## Development
```bash
sudo apt-get install ffmpeg fonts-lato fonts-dejavu-core
python -m pip install -r requirements.txt pytest
pytest -q tests
python src/batch.py
python src/validate.py docs/media
```

Use only personally-owned/original assets. Scheduled GitHub jobs can be delayed or skipped; a seven-day queue helps but cannot guarantee continuous delivery.
