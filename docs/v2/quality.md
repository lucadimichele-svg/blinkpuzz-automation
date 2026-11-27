# Pilot collection acceptance record

Benchmark seed `20261127`. The collection contains 20 complete English-language Reels, two per mechanic in different compatible worlds. Fifty further specs have unique board fingerprints across the entire 70-puzzle inventory. Every saved solution was recomputed from the public board and checked against its seed.

## Executed checks

- **Test suite.** 1064 passed in 172.57s (0:02:52). The run included legacy regressions, 100 deterministic-seed cases per mechanic, structural variability, adversarial inputs, staged evidence, art provenance and fallback, duplicate checks, the credential-free single-pilot smoke test and a fresh twenty-pilot end-to-end render.
- **Generation.** 70 boards accepted after 189 rejected proposals. The inventory rejected 0 repeated accepted-board fingerprints. Every mechanic also produced at least five distinct structural configurations in the seed sweep.
- **Timing.** The opening frame contains the complete game. Solve intervals span 11–18 seconds. Each film adds three seconds of witness replay. Total runtime across the collection is 331 seconds.
- **Media.** All 20 files passed ffprobe checks for H.264, yuv420p, native 1080 × 1920 at 24 fps and AAC. Stream and container lengths matched the storyboard within 60 ms. Decoded PCM RMS ranged from 945.95 to 1054.28 on the signed 16-bit scale.
- **Visual QA.** All 7,944 delivered frames were decoded and compared against their intended phase at 135 × 240. The verifier masks only the moving playhead strip. The worst local block mean difference was 3 on the 0–255 luminance scale, below the limit of 30.
- **Layout.** Across all assessed phases there were zero clipped text boxes, text collisions or overlapping gameplay surfaces. The minimum measured text contrast was 5.98 to one. The smallest recorded text including brand labels was 26 native pixels. Essential cover regions fit the central square crop.
- **Diversity.** Six sets, ten mechanics and twenty different boards. The minimum pairwise cover difference hash distance was 32 bits of 256, above the duplicate gate of seven. Adjacent covers use different world compositions.
- **Review and isolation.** Both contact sheets, all posters, proof stills, spec digests and local handoff manifests passed. Offline Insights import of blank measurements yields zero observations and zero recommendations. Work is confined to the development branch.

## Per-pilot results

The proof column gives the sole winning option returned by the independent oracle. A render pass includes stream validation, real audio, poster verification and decoded-frame comparison.

| Pilot | Mechanic | Visual world | Seed | Solve + replay | Proof | Render |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 01 | laser | Optics Lab | 20261127 | 15 + 3 s | B, unique | Pass, 432 frames |
| 02 | maze | Tidal Archive | 20261128 | 13 + 3 s | B, unique | Pass, 384 frames |
| 03 | lock | Bureau of Evidence | 20261129 | 15 + 3 s | B, unique | Pass, 432 frames |
| 04 | pipes | Brass Works | 20261130 | 12 + 3 s | A, unique | Pass, 360 frames |
| 05 | pattern | Form Studies | 20261131 | 11 + 3 s | C, unique | Pass, 336 frames |
| 06 | nonogram | Pocket Arcade | 20261132 | 18 + 3 s | C, unique | Pass, 504 frames |
| 07 | circuit | Optics Lab | 20261133 | 11 + 3 s | A, unique | Pass, 336 frames |
| 08 | routes | Tidal Archive | 20261134 | 11 + 3 s | A, unique | Pass, 336 frames |
| 09 | balance | Bureau of Evidence | 20261135 | 11 + 3 s | A, unique | Pass, 336 frames |
| 10 | gears | Brass Works | 20261136 | 12 + 3 s | C, unique | Pass, 360 frames |
| 11 | laser | Pocket Arcade | 20261137 | 16 + 3 s | B, unique | Pass, 456 frames |
| 12 | maze | Form Studies | 20261138 | 16 + 3 s | B, unique | Pass, 456 frames |
| 13 | pipes | Pocket Arcade | 20261139 | 15 + 3 s | A, unique | Pass, 432 frames |
| 14 | lock | Form Studies | 20261140 | 16 + 3 s | C, unique | Pass, 456 frames |
| 15 | circuit | Brass Works | 20261141 | 12 + 3 s | A, unique | Pass, 360 frames |
| 16 | pattern | Pocket Arcade | 20261142 | 12 + 3 s | C, unique | Pass, 360 frames |
| 17 | nonogram | Bureau of Evidence | 20261143 | 18 + 3 s | A, unique | Pass, 504 frames |
| 18 | routes | Form Studies | 20261144 | 12 + 3 s | A, unique | Pass, 360 frames |
| 19 | balance | Brass Works | 20261145 | 12 + 3 s | C, unique | Pass, 360 frames |
| 20 | gears | Tidal Archive | 20261146 | 13 + 3 s | A, unique | Pass, 384 frames |

The single-spec CLI regenerated pilot 01 from seed 20261127. The standalone and collection MP4 had the same SHA-256, `52e15aff19fa58965a442a148231106559bde6807a6077f5ee5ce17e5bff66c7`.

## Actual ffprobe sample

Pilot 01, `01-laser.mp4`. Each of the twenty stream summaries is also in `quality.json`.

```text
codec_name=h264|width=1080|height=1920|pix_fmt=yuv420p|avg_frame_rate=24/1|duration=18.000000|nb_frames=432
codec_name=aac|sample_rate=24000|avg_frame_rate=0/0|duration=18.000000|nb_frames=423
```

## Reproducible review packet

Reference runtime used Python 3.12.14, Pillow 12.3.0, FFmpeg/ffprobe 7.1.5 and system DejaVu faces on Linux. The README lists the reproduction commands. Digests identify these specific local deliverables.

| File | SHA-256 |
| --- | --- |
| `pilots.zip` (26,813,807 bytes) | `4aca768ea16d44f8c573e5886407aaa01967f5e9119c01145edc9ccb0d1f439f` |
| `index.json` | `01e5938a713cb4711ffe8e85616885513fb48a19cbcd552220ab0caa387ef24d` |
| `quality.json` | `c3a46236962887b4fc44bd26dafeb2cefb9aeb6ba0a931582cb6ea916657dad1` |

## Open validation

The mechanical and file acceptance checks passed. The cover and proof sheets received a visual inspection. Decoded solve frames from the maze, nonogram and balance films were also inspected at 360 × 640. The final English rules specify staying inside the maze, gaps between runs, and whole-number masses. The graphic treatment is original procedural illustration. A first-time viewer study is still needed to measure two-second comprehension, perceived difficulty, small-screen comfort and enjoyment. Frame comparison checks a reduced image and has no OCR or perceptual audience model. A hash distance quantifies image difference and cannot measure art direction. There are no measured Instagram retention, sharing or follow outcomes for these pilots. Production rollout requires a separate owner decision.
