# BlinkPuzz – Automated English Puzzle Reels

Standalone, zero-subscription-cost video-generation pipeline for **@blinkpuzz**.
The Vibsnaxx project is separate and never targeted.

## Status
- Original English vertical puzzle Reel generator: installed.
- GitHub Actions: daily rolling seven-day generation buffer, plus separate automated Buffer queue refills throughout each day.
- GitHub Pages: choose **Settings → Pages → Source: GitHub Actions** to activate hosting. This step needs a one-time owner action.
- Buffer API key: stored in **Actions secret `BUFFER_API_KEY`** by the owner. Do not paste secrets into chat or source files.
- Instagram publishing: **OFF** until `AUTO_PUBLISH=true` repository **variable** is explicitly set *after* testing. No live posts confirmed.


## Four-arm audience experiment (15–20 November 2026)

**Goal:** distinguish whether modest difficulty, withholding the in-video reveal, or plausible answer choices improve meaningful interactions without sacrificing watch time.

- **A:** easy puzzle + in-video reveal (3 Reels)
- **B:** medium puzzle + in-video reveal (3 Reels)
- **C:** medium puzzle + no in-video reveal (3 Reels; full spoiler solution in caption)
- **D:** medium puzzle + three plausible options + no in-video reveal (3 Reels; spoiler solution in caption)

All 12 experimental Reels are 12 seconds long, with the same visual layout and original audio. Each arm includes exactly one sequence, one arithmetic puzzle, and one logic puzzle. The 12 time slots are fixed in `docs/experiment_plan.json`, using the **existing** schedule (four per day until 16 Nov; two per day afterward). The 15 November and 16 November base slots were already booked with old content, so these two experiment arms were moved to midday on 19 and 20 November. Only the exact planned slots are treated, and new media have a separate `-EXP` suffix.

**Queue safety:** The publisher prefers `-EXP` over `-V3` over legacy media **only for a slot not already present in Buffer**. All prior posts and files are preserved. No separate extra daily posts are created. `src/experiment_report.py` writes a limited read-only Buffer queue audit to `docs/experiment_status.json`; this never proves actual Instagram delivery.

**Measurement:** At least 48 hours after each Reel appears on Instagram, record actual Instagram Insights at a consistent post age in `docs/experiment_results_template.csv` and run `python src/analyze_experiment.py`. Primary outcomes: comments per hundred views and average watch time; secondary: views, likes, shares, follows. No Instagram analytics credentials are connected for this account, so these must be supplied from Insights. Do not infer a winner from only a few Reels or from Buffer scheduling status.

Pinned comments are **not** currently automated via this Buffer setup; C/D use an opt-in caption spoiler instead. This is an explicit approximation, not a test of pinned comments.

## Creative V3 — more engaging variety (10 November update)

The previous Reels all looked similar. The generator now supports eight original challenge families with distinct color palettes, bold first-frame hooks and high-contrast mobile-readable layouts:
- Odd symbol, missing number, number sequence, order-of-operations, symbol equations, A/B comparison, memory flash and single-correct-door logic.
- All answers checked deterministically by dedicated tests (including 365 days × 5 variants).
- Each Reel keeps the same original-audio 8-second vertical H.264/AAC format.
- Creative metadata records `creative_version: "v3"` and the challenge family for future analysis.

**Rollout is non-destructive.** Previously queued media cannot safely be swapped.
- For November 11–16, `creative_inventory.py` prepares separately named `-V3` alternatives for not-yet-published time slots; the Buffer publisher selects a V3 alternative only if the matching original challenge has **not** already been queued.
- From November 17, all newly generated clips use V3 by default.
- Existing Instagram posts, Buffer queue entries, challenge IDs and file URLs are never silently changed. Better creative quality is a testable hypothesis, not a guarantee of increased reach.

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
