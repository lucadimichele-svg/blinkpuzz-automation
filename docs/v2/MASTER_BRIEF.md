# BLINKPUZZ 2.0 — MASTER DEVELOPMENT BRIEF

**Status:** implementation specification, not a claim that the engine exists.
**Project:** @blinkpuzz, English-language Instagram brain-game Reels.
**Development branch:** `blinkpuzz-2-dev` (never implement by rewriting live `main`).
**Scope:** build a substantial, extensible, validated content-production platform. No one-off toy prototype and no superficial recolor of legacy V3/V4.

## 0. What failed, and what success means

The current 8s static templates get repeatable but modest views and little follower conversion. User feedback was consistent:
- "Too small": content feels like a template that substitutes numbers or colors.
- Puzzles are shallow or arbitrary, or the opposite: too many sequential clues to memorize.
- Changing palettes and backgrounds is not substantive variety.
- Door/survival puzzles that rely on vibes ("which looks safe?") have no provable answer.
- Cinematic scenes are appealing, but spectacle without genuine mechanics is not a game.
- In prior demos, a multistep clue sequence required holding earlier text in working memory; that is disallowed.

**Product invariant:** Within 2 seconds, a mobile viewer understands what to investigate; a meaningful solution may take 8–20 seconds. All indispensable clues remain simultaneously visible for the full solving segment. No arbitrary sign logic, no contradicting or underdetermined clues. Impressive but legible visual worlds + real puzzles + reproducible technical automation. Authentic engagement and follows are the goals, not manufactured comments.

## 1. Isolation, security and scope constraints

1. Inspect the repository before coding: `src/generate.py`, `src/creative_v3.py`, `src/visual_v4.py`, `src/schedule.py`, `src/batch.py`, `src/publish.py`, the tests, `.github/workflows/`, `README.md`, `docs/cinematic_pilot_plan.md`.
2. Work only on `blinkpuzz-2-dev` until explicit owner approval for merge/rollout. Put all new code in `blinkpuzz2/` (Python package) plus separate `tests_v2/`, `docs/v2/`, and optionally a non-publishing GitHub Actions workflow. Do not edit the live publisher, schedule, Buffer connection, secrets, GitHub Pages deployment, or `docs/media/` on `main`.
3. Never change Vibsnaxx, Dreamy Elsewhere, their automation schedules/accounts, or other unrelated files even if they happen to appear in this repository.
4. Production remains 2 scheduled posts/day on the existing independent `main` workflow. No public experimental posts, Buffer mutations, or Instagram actions without separate explicit approval.
5. The system must work locally without a paid model API. Optional model/image providers must be adapters, disabled by default; never assume a free realistic-cinematic-image API. Provide a credible deterministic/asset-library mode with licensed/original art, and a documented path to a higher-end scene provider. Do not fabricate high-fidelity photorealism via a cheap vector-only renderer and call it cinematic.
6. No secrets in code, logs, manifests, docs or generated video metadata. Never fetch `BUFFER_API_KEY` from the developer branch workflow. No automatic chargeable model calls.

## 2. Deliver a *system*, not individual puzzle scripts

The package should contain discrete, testable layers with explicit typed contracts:

- **Puzzle contract & catalog**: `PuzzleSpec` including `puzzle_id`, `seed`, `engine`, `mechanic_version`, structured board/graph, globally visible rules, candidate options when appropriate, solution, machine-readable proof, difficulty components, evidence, palette-independent semantic entities, and accessibility text. Include schema version and JSON serialization.
- **Generators**: seedable, parameterized instance construction per mechanic, not a handful of hard-coded puzzles.
- **Independent validators/oracles**: for each mechanic, enumerate or solve the instance *independently of the generator's chosen answer*. Require precisely one intended interpretation/answer; reject ambiguous, invalid, unsolvable, trivial, off-screen or duplicated instances.
- **Difficulty calibration**: measure path length/branching, distractor plausibility, reasoning steps, readability, cognitive load. Adjustable between easy / medium / challenging, with a bias toward medium. Do not equate difficult with lots of text or memorization.
- **Scene/asset engine**: separates game geometry and gameplay clues from visual background, perspective, materials, animation, lighting, typography and audio; artwork must never silently change puzzle semantics. Scene themes should be composable only when genuinely compatible with the mechanic. Maintain asset provenance/license.
- **Storyboard and time engine**: Intro hook <=2s; board and all clues shown continuously for the solving portion (no staggered rule reveals); optional hints must not remove necessary original information; solution demonstration at end OR no-reveal mode for controlled tests. Audio original and copyright safe.
- **Cover engine**: cover distinct from a mid-countdown frame, with big readable question, meaningful game art, subject visible in Instagram grid crop and a subtle BlinkPuzz identity.
- **Renderer**: offline 1080x1920, H.264 + AAC MP4, 9:16, original sound effects; robust fallback if images missing. FFmpeg-based pipeline okay; do not make renderer depend on paid services.
- **Quality gates**: logical uniqueness, on-screen legibility/no clipping, no accidental repeated puzzle, visual diversity metrics, proof replay overlays, video/audio metadata and duration validation; fail closed before any export.
- **Planning/analytics adapter**: offline manifest + a report template for per-video Instagram Insights (not assumed accessible). Recommend variants from measured retention, shares, comments, follows only once actual data exists; do not treat Buffer status as engagement.
- **Publishing adapter boundary**: export queue-ready manifest without side effects. Integration to current Buffer publisher should be a separate later-approved PR, not part of this sprint.

## 3. At least 10 genuinely different playable mechanics

Implement *at least ten fully working, distinct* mechanisms from the following candidate catalog, with clean interfaces and separate independent solvers. Prefer 12 if feasible; don't count palette or theme changes as mechanics.

| Mechanic | Immediately understood viewer task | Independent correctness check |
| --- | --- | --- |
| Laser/mirrors | Which of A/B/C crystals gets hit? | grid ray traversal; reflection and collision simulation |
| Spatial maze | Which entrance reaches the exit? | graph/BFS connectivity; one winning start |
| Circuit board | Which switch/configuration activates device? | Boolean satisfiability / exhaustive truth table |
| Pipe routing | Which pipe piece connects source and sink? | connectivity/flow after rotation; one valid option |
| Shortest safe route | Which marked route meets an exact constraint? | weighted graph search + unique winner |
| Lock-code clues | Which code satisfies 2–3 simultaneous visual clues? | enumerate finite candidates; one code; rules ALWAYS on screen |
| Missing pattern tile | Which geometrically transformed tile completes the board? | programmatic transformation and candidate uniqueness |
| Match the 3D rotation | Which rotated physical piece fits? | exact transform of original geometric representation |
| Balance scales | Which object has the correct weight/placement? | algebraic finite-domain solver |
| Nonogram microgrid | Which tiny pixel pattern satisfies row/column counts? | enumerate boards and require unique solution |
| Mechanism / gears | Which drive gear moves a marked direction? | graph parity / gear propagation constraints |
| Intersection / signal flow | Which destination receives an item/beam? | deterministic state transition graph |

**Do not fake any mechanic** by drawing a dramatic door and picking the friendly-looking one. Reject ambiguous examples. For physically realistic reflection, graph parity, pipes and geometry, implement actual verifiable models. If an engine cannot guarantee uniqueness or concise explanation, skip it and implement another catalog engine properly; state the gap rather than presenting a non-game as finished.

Each engine must support a minimum of five visibly different configurations, not only different numeric constants.

## 4. Visual diversity standards

Provide >=6 distinct art/interaction directions with real layout/scene differences:
1. Cinematic sci-fi research lab / laser board;
2. Architectural maze / isometric ruins;
3. Detective desk / evidence board where evidence is all visible at once;
4. Mechanical workshop / kinetic gears and contraptions;
5. Minimal high-end editorial puzzle screen with large graphics;
6. Vivid tactile tabletop / arcade puzzle.

Optional extras: underwater research station, botanical conservatory, mystery museum, cosmic observatory.

- *Scene* diversity is not just background hue: different focal structures, camera/projection approach, puzzle board placement, materials, iconography, type grid and reveal behavior.
- Do not use a fixed top label + small center card + bottom countdown for every video.
- Solving information must be encoded on a high-contrast foreground puzzle surface visible through the entire solving interval.
- 9:16 vertical 1080x1920 full frame. Instagram-safe central crop, minimum legible fonts for phones, no clipped headings.
- Covers must not all show the number "4" or any repeated countdown screenshot.
- Preserve original licensed creative assets; document origin and usage permission.
- Validate color contrast and report frame-level layout collisions (bounding boxes, text truncation tests); generate a contact sheet of all twenty covers and proof frames.

## 5. Benchmark collection / acceptance criteria (required)

Produce *20 real, distinct playable pilot Reels* plus their covers, structured manifests and solver proofs (artifacts, not just plans):
- minimum 10 different mechanics represented; preferably 12;
- minimum 6 different art worlds; no two adjacent covers same composition;
- 2 visibly different settings/instances for every mechanic covered twice;
- timings individually justified (roughly 12–24 s; don't stretch to 30s without reason);
- in every case an unfamiliar viewer understands objective without reading sequential rules;
- every required clue remains visible from the first gameplay frame to reveal;
- every solution has an independently computed machine-readable proof and optional replay/visual reveal;
- at least 50 *additional* unique puzzle specs across seed values (not necessarily rendered), plus reproducibility and rejection stats;
- no unverified factual statements about real-world physics/geography in puzzle logic;
- all MP4s tested via ffprobe for 1080x1920, H.264 video, AAC audio, expected duration and usable poster file;
- save `build/v2/pilots/` with 20 MP4s + covers + `index.json` + `proofs/` + `contact_sheet.jpg`, and `build/v2/pilots.zip` locally or as workflow artifacts, **not bulk committed as binaries to Git**;
- show a summary table by mechanic, visual world, duration, seed, uniqueness proof check and render check.

**Automated tests:**
- >=100 distinct seeds per implemented mechanic; independent solver verifies unique solution, deterministic re-generation and structural validity.
- Contract tests and edge-case/adversarial tests for invalid puzzles.
- Negative tests explicitly reject staged clues, contradictory information and more than one correct option.
- Per-frame legibility and out-of-frame element checks.
- Media metadata checks and duplication detection (puzzle ID + cover perceptual/image-layout similarity).
- Smoke test builds 1 pilot with no credentials or internet.
- End-to-end test builds full 20; make slower render tests opt-in or in a non-publishing workflow to limit Actions minutes.
- Flag limitations clearly: programmatic proof and file QA do not substitute for audience testing or human judgment of entertainment quality.

**Acceptance threshold:** This sprint is NOT complete when only an architecture diagram, one laser demo or six recolored cards exist. It is complete only with the working modular system and playable, validated, visibly diverse 20-Reel collection. If blocked by asset creation/budget, supply the functioning mechanics, runnable tests and a precise evidence-based gap report instead of claiming finished cinematic assets.

## 6. Implementation and developer experience

Use current Python/Pillow/FFmpeg foundation where it helps, but organize as a new `blinkpuzz2/` package. Prefer stable standard libraries; avoid heavy/paid external dependencies unless justified.
Suggested repository structure:
```
blinkpuzz2/
    core/{models,contracts,validators,seed,quality}.py
    engines/{laser,maze,circuits,pipes,routes,lockcode,pattern,rotation,balance,nonogram,gears,flow}.py
    scenes/{registry,assets,layouts,typography}.py
    render/{storyboard,frames,video,audio,covers}.py
    planning/{catalog,inventory,experiments,metrics}.py
    cli.py
tests_v2/
docs/v2/{architecture,mechanics,quality,rollout}.md
build/v2/   # gitignored; artifact output only
```
Actual package layout may differ if it is more idiomatic; explain deviations.

Implement CLI:
```
python -m blinkpuzz2.cli catalog
python -m blinkpuzz2.cli generate --engine laser --seed 123 --difficulty medium --out build/v2/spec.json
python -m blinkpuzz2.cli validate --spec build/v2/spec.json
python -m blinkpuzz2.cli render --spec build/v2/spec.json --out build/v2/demo
python -m blinkpuzz2.cli pilots --count 20 --seed 20261127 --out build/v2/pilots
python -m blinkpuzz2.cli qa --folder build/v2/pilots
```
If CLI changes, keep equivalent documented commands with demonstrable working output.

CI: create a NEW dev-only GitHub Actions workflow with no secrets and no publishing side effects; optionally upload pilot assets as Actions artifacts. Never expose `BUFFER_API_KEY` to a dev branch job. Do not mutate existing workflows in this sprint.

## 7. Required technical and design decisions to document

- Puzzle contracts, engine registries, schema versioning, oracle correctness and retry/fail policies.
- Difficulty calibration that does not burden memory.
- What is programmatically provable vs. what requires visual/user testing.
- Original assets vs. paid optional generation (honest cost per asset and failure recovery).
- Storage/retention for previews, avoiding huge binary Git commits.
- Deployment strategy later: shadow generation, human review of sample, limited test scheduling, performance comparison, gradual replacement, rollback. **No automatic rollout now.**
- Existing Instagram analytics are not connected in a tool accessible here; create import adapters/templates, no fake feedback loop or made-up rankings.

## 8. Coding process expected from Codex

1. Audit repository and risks; record succinct design decision log `docs/v2/DECISIONS.md`.
2. Implement core spec + validation and one representative engine with independent oracle.
3. Expand to >=10 distinct, genuinely working engines.
4. Implement scene compositor, six layout archetypes, covers, original sound and video renderer.
5. Generate and QA 20 pilots; produce contact sheet and machine-readable quality report.
6. Run tests and ffprobe; fix concrete failures. Document exact passing/failing test counts and known gaps.
7. Push commits to `blinkpuzz-2-dev` only. Provide review links and reproducible commands.
8. Stop without merging or changing any production schedule. Ask for explicit approval only when actual rollout is ready.

## 9. Definition of "impressive"

Not more text. Not simply more steps. Not abstract backgrounds with a numbered equation. Meaningful interactive geometry, distinct art direction, obvious objective, fair rules, real discoverable solution, gratifying answer reveal, and cinematic presentation that does not hide the clues. It must look like a collection of distinct mini-games rather than a template with color changes.

**Owner preference:** challenge weak assumptions frankly. Never say "done" if only the code was written but tests or assets did not complete.
