# BlinkPuzz 2.0 — PHASE 2: CREATIVE & VISUAL ENGINE REBUILD

**Task type:** substantial product-development sprint, not incremental cosmetics.
**Starting point:** `blinkpuzz-2-dev` contains a functioning offline pipeline with ten mechanics, six procedural graphic worlds and a reported 20-Reel benchmark. The current reviewed archive is available as the `blinkpuzz-2-pilots` GitHub Actions artifact, run 46154928411, generated from commit d203842. Reproduce and inspect the existing covers, gameplay frames and proof sequences before changing anything.
**Source contracts:** `AGENTS.md`, `docs/v2/MASTER_BRIEF.md`, the V2 implementation, all `tests_v2/` and `docs/v2/quality.md`.
**Live state:** main remains untouched. NO publishing, Buffer mutations, schedule changes, live account actions, or unrelated project changes.

## 1. Product decision: V2 is a technical FOUNDATION, not creatively ready

V2 appears to have succeeded in deterministic production and testable rules. It did **not** solve the actual owner's product problem:
- Overall impression is still an illustrated static quiz-card collection, not an engaging universe of high-quality mini-games;
- Complex text-evidence / code / nonogram / balance problems are poor defaults for 2-second mobile comprehension and may be better as optional niche formats;
- Six world color/material treatments are insufficient if the diagram occupies the same flat card space and gameplay is visually passive;
- Technically unique and solvable does NOT mean understandable, satisfying or attention-worthy. Automated QA must not claim to measure subjective fun.
- 20 technically distinct samples are NOT successful if the viewer perceives them as twenty template variants.

**North star:** a portfolio of visually compelling, immediately legible mini-game Reels. A casual viewer understands the objective within 2 seconds, has all required facts simultaneously on screen, can work out one objectively fair answer with 8–20 seconds of actual attention, and enjoys seeing the physical/visual reveal.

**Do not solve this by adding animated titles, extra clue cards, longer narration, another set of flat backgrounds, or more colors.**

## 2. Major engineering deliverables

### A. Editorial mechanic selector + comprehension contract
- Audit and objectively rate each existing format for first-two-second comprehension, number of words/rules, simultaneous visibility, solution certainty, false-friend distractors, spatial legibility and pleasure of reveal.
- Categorize engines `mainstream ready`, `requires redesign`, `niche/parked` with rationale. Existing engines remain available; do not delete functioning V2 work to hide weaknesses.
- Introduce a versioned `ExperienceSpec` or equivalent that explicitly includes: one-sentence viewer objective; board/icon/key; invariant simultaneous evidence; expected viewing time; independent proof; way the answer is demonstrated; target aspect/safe zones.
- Every essential gameplay symbol must be self-explanatory or explained by a **single permanently visible visual legend**. Never require sequential memorization.
- Do NOT force A/B/C on intrinsically different games. A natural 1-choice, trace-to-outcome, identify-the-object, find-the-path, or direct-spot objective is acceptable.

### B. At least 8 audience-first, *visually different* mini-game families
Rebuild/extend existing engines with reusable geometry, avoiding 8 variants of a 3-choice poster. Target a collection including:
1. **Optical ray physics:** one laser, physically accurate mirrors, clearly indicated emitter and target; satisfying path-trace replay.
2. **Spatial maze / path finding:** intricate but mobile-readable maze with selectable entrance or marked destination; no textual lore.
3. **Hidden object / visual search:** one provably unique target hidden among contextual objects (not randomized illegible clutter); programmatic object identity & occlusion rules.
4. **Spot the mismatch:** compare two richly designed machines, diagrams or scenes; precisely one semantically relevant mismatch, proven by scene graph.
5. **Shape fit / mechanical assembly:** identify which realistic part fits an opening; actual geometry and transform checks, not vibe-based.
6. **Pipe / fluid flow / machine routing:** unique connectivity under explicit orientation and constraints; animation of correct fill/flow.
7. **Gear train / kinetic reasoning:** driver direction plus a reachable output; real gear contacts and parity, animated reveal.
8. **Shadow/silhouette or perspective reasoning:** choose matching physical form; calculate the actual projection or rotation; ensure uniqueness and fairness.

Preserve potentially useful earlier circuits, nonograms, lock codes, balance, routes and patterns in a **secondary catalog**, but do not use them to meet the 8 mass-audience benchmark slots unless their cognitive load is clearly redesigned.

**Originality requirement:** at least three new genuinely different validated game engines beyond the current ten. They must be distinct in interaction, not merely image treatments. Each engine has an independent checker and 100 seed tests. Explicitly document any currently infeasible mechanics and do not claim them completed.

### C. Real scene/visual architecture (NOT only backgrounds)
- Refactor scene composition so the **interactive puzzle lives inside** the environment (laser hardware in optical chamber, maze in an architectural set, gears in a machine, search scene with physical objects) and is never just a centered generic white card.
- Support at least 8 meaningful **scene grammars** with different composition, spatial camera angle, lighting/material treatment and reveal language; layout changes must come from scene geometry, not only new names.
- Build a reusable asset/camera/lighting/layout system. Use procedural Blender/3D or another **actually executable, locally validated** 3D approach if available and operationally realistic; otherwise produce high-quality layered/parallax 2.5D with explicit limitations. Do not claim photorealistic 3D if it is flat illustration.
- Keep a deterministic local asset library with rights attribution; optional approved high-end images can serve as scene plates, never as the sole source of puzzle truth. No unapproved paid API.
- Choose format-specific cameras/storyboards (macro machine view, top-down desk, isometric maze, tracking path, cutaway lab). The game board and necessary evidence must be fixed in content during the full solving interval; subtle ambient animation is allowed if it does not change semantics or visibility.
- Aim for distinctive game-world art in **the gameplay frame**, not just the cover.

### D. Video experience & production
- First full frame is usable; clear and visually strong hook without sequential intro card.
- Normal target length 12–22 seconds; optimize per format based on reasoning steps, not arbitrary 15s loop.
- The full board and rules are available continuously; animated countdown may exist outside the puzzle safe zone but must not obscure details.
- Reveal is visually gratifying and explains the exact correct physical action/path, not just colored letter B.
- Sound is original, appropriate to world (clicks, liquid, machinery, optics); no licensing guesswork.
- Actual 1080x1920 MP4 H.264/AAC, safe zones for Instagram overlays and phone readability, motion and compression QA.
- Ensure entirely English interface to viewers, no robot voice required.

### E. Validation and engagement readiness
- Maintain V2 oracle/proof contracts and existing test coverage. Verify *displayed* object geometry maps 1:1 to each engine's exact semantic model; tests must fail if an artist misplaces a mirror, gear or passage.
- Prove each generated instance has a single correct solution (or correctly unique visual oddity), sufficient misleading but fair alternatives, and no contradictory/intermittent evidence.
- Compute useful QA: max simultaneously displayed explanatory text, actual glyph widths, contrast in multiple stages, shape size in phone-scale preview, safe-zone occupancy, repeated scene composition, perceptual near-duplicates and schema-level repeated gameplay.
- Automated uniqueness/legibility is necessary, **not** proof of fun. Make a separate review scorecard for 2-second understanding, perceived difficulty and delight of reveal; initially leave human fields UNRATED. Do not invent audience tests or Instagram retention.
- No publishing, analytics credentials, fake success metric or in-place modification of `main`.

## 3. Benchmark: one coordinated, substantial deliverable

Build **24 complete new Reels**, representing 8 visually different game families × 3 substantially different instances each, across >=8 distinct scene grammars. A cover contact sheet is necessary but insufficient: also create a **24-frame gameplay contact sheet** (first solve frame), a **24-frame reveal contact sheet**, and a grid with paired same-mechanic episodes to verify real structural variety.

At least 100 additional distinct valid specs across the 8 engines, including adversarial cases. Select pilot cases for genuinely distinct puzzles, not shallow answer-letter changes.

Generate:
- Full 24-episode MP4/JPG/JSON/proof collection, packaged as a ZIP; include machine-readable QA and editor review checklist.
- `contact_sheet_covers.jpg`, `contact_sheet_gameplay.jpg`, `contact_sheet_reveals.jpg`.
- One-page comparison `docs/v2/PHASE2_BEFORE_AFTER.md` demonstrating how the gameplay view differs from V2, with actual output screenshots, and candidly specifying where cinematic quality falls short.
- `docs/v2/PHASE2_IMPLEMENTATION_REPORT.md`: exact files changed, supported engines, tests run and result counts, render diagnostics, limits, blocked assets/resources, and link to downloadable GitHub Actions artifact.
- New non-publishing dev-only GitHub Actions workflow for building and uploading the 24-pilot ZIP. Ensure a verified successful run/artifact, not merely a workflow YAML. Never pass publishing secrets to this workflow.

**Review gate:** 24 videos are not approval to post. After the artifact is downloaded, viewer/editor checks actual gameplay frames and videos; only then decide on an opt-in small Instagram A/B test. The existing @blinkpuzz publication pipeline remains running independently.

## 4. Quality thresholds that cannot be sidestepped

- 100% of gameplay clues appear simultaneously before any animation begins and remain visible.
- Explanatory burden: one dominant task/question, optional one brief persistent instruction; prefer zero prose beyond question/labels; set explicit documented thresholds, explain justified exceptions.
- No safety/door-type guesses without evidence.
- No formats where the viewer must first learn a multi-step abstract rule before understanding the goal.
- At least eight visibly different **play surfaces**, not just themed frames or different colors.
- At least eight families truly playable from video screenshot without audio and without seeing prior frames.
- All solutions externally and independently checkable from displayed visual geometry.
- No invented evidence of viewer enthusiasm, retention improvement, or organic reach.
- Preserve the existing set; never overwrite V2 pilot files or live content.

## 5. Codex execution instructions

1. Inspect repo and prior artifact. Write an honest short audit of deficiencies in existing V2 gameplay frames.
2. Propose a concrete architecture and implement it (not only a plan).
3. Build/upgrade engines and map their semantics onto real visual geometry and diverse scenes.
4. Run full tests and render *all 24 pilots*, inspect downsampled gameplay frames, fix issues.
5. Upload the real archive via successful dev-only GitHub Actions run (accessible to ChatGPT through GitHub connector).
6. Commit only to `blinkpuzz-2-dev`; no merge, no Instagram scheduling. Provide direct run link and factual report.
7. If real 3D / cinematic quality is impossible under resources, report exactly why and what reusable assets or cost-effective setup would be needed. Never relabel flat posters as a high-end cinematic engine.

**This task is not finished when only one attractive example exists or a technical-only QA suite passes.** It is finished when a substantially improved, visibly distinct 24-video playable collection is available for independent critical review, or when a concrete, test-supported blocker report explains precisely what prevented it.
