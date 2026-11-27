# AGENTS.md — BlinkPuzz 2.0 development branch

You are working in the existing `lucadimichele-svg/blinkpuzz-automation` repository on branch **`blinkpuzz-2-dev`**.

## Mandatory first step
Read `docs/v2/MASTER_BRIEF.md` in full. Treat it as the product, quality, architecture, safety, and acceptance contract. Also audit `README.md`, `src/`, the current `tests/`, and `.github/workflows/` before implementing.

## Production protection
- Work on `blinkpuzz-2-dev` only. Do not commit to or merge into `main`.
- Existing `main` is an operational @blinkpuzz auto-publishing system. Do **not** disable, mutate, or replace its Buffer workflow, Pages settings, GitHub variables, secrets, or cadence.
- Do **not** touch Vibsnaxx, Dreamy Elsewhere, their assets, accounts, or related tasks.
- NO live posts, publishing queue mutations, API-key reads, paid generation tasks, or external provider calls during development.
- Put new code under `blinkpuzz2/`, new tests under `tests_v2/`, and build artifacts under ignored `build/v2/`.
- Add a new dev-only, publishing-free validation workflow if useful; never alter current production CI jobs without an explicitly approved separate change.

## Developer behavior
- Build a reusable, substantial engine—not a palette update and not one-off Reel prototypes.
- Every puzzle requires fair, unique, independently verified solutions. Keep every necessary clue on-screen simultaneously throughout the solving period.
- A cinematic setting is not a substitute for interactive game logic. If only visual assets can be reused for free, explain their limitations honestly; no fake "infinite generative photorealism."
- Provide >=10 distinct genuine mechanisms, >=6 meaningfully distinct visual worlds, 50+ verified generated instances and 20 completed pilot videos **or** a truthful blocker report listing exact shortfalls.
- Run automated tests; report real results and ffprobe output instead of claiming completion based on code presence.
- Distinguish viewer engagement *hypotheses* from real measured Instagram Insights. Queue status != Instagram delivery.
- Keep deliverables reproducible and ready for review, with a cover contact sheet and explanation of how to inspect each game's rules, answer and proof.
- Prepare future integration behind an explicit feature switch but **do not** merge or publish to Instagram.

## First coding task
Inspect code, create `docs/v2/DECISIONS.md` (audit, architecture and build sequence), then implement the typed puzzle contracts and independent solver baseline. Continue across the engine catalog, render pipeline and batch collection. Avoid stopping after only a plan; make working progress in this Codex task.
