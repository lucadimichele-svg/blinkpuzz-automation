# BlinkPuzz — cinematic concept pilots (2026-11-22)

**Purpose:** five original experimental directions that move beyond static eight-second number/odd-one-out puzzles. No existing Instagram scheduling, GitHub workflows, or Buffer credentials changed as part of these pilots. Pilot MP4s are shared in the design conversation and are not hosted in this repository.

## Tested prototype concepts
| Pilot | Intended runtime | Puzzle mechanic | Verified answer |
| --- | ---: | --- | --- |
| The Midnight Heist | 26s | Closed-access theft timeline; 22:08 left / 22:10 doors locked / 22:13 theft / 22:15 arrival | B is the only suspect inside |
| Escape Protocol | 23s | Exactly one of three door statements true | Door A (only B's sign true) |
| Paradox City | 22s | Cross each of five skybridges once and return to origin | Impossible; two odd-degree graph vertices A,C |
| Reactor 09 | 23s | Exactly one switch on, two XOR light conditions and one equal-state alarm condition | B on; A=C off |
| The Memory Vault | 22s | Two views of six-artifact inventory, one substitution | Object 02: key becomes dagger |

## Production standard demonstrated
- Five distinct visual worlds: museum, sci-fi doors, futuristic city, orange reactor and golden vault.
- Image-driven scenes with large legible English overlays, timed clue reveals, outcome reveal and distinct cover per pilot.
- Original synthesized ambient/tick audio; no licensed track required for the prototypes.
- Five independently rendered 1080×1920 H.264/AAC MP4 pilots with durations 22–26s.
- No AI voice.
- Explicitly exploratory: cannot infer views or conversion from these prototypes.

## Engineering limitations and next steps
The pilots currently use high-quality scene artwork generated for the concepts plus a hand-authored timed-frame compositor. They are **not yet** a cost-free self-generating scene engine. A production system would need: (1) validated, parametric logic generation, (2) a deterministic background/asset strategy that has permission to reuse assets, (3) automated typography/cover checks, (4) media QA, (5) controlled A/B and staged rollout. Do not swap in static V4-style templates and mistake this for the above.

**Publication state:** NOT SCHEDULED. Keep current @blinkpuzz workflow running until pilot direction is deliberately integrated. Never modify @vibsnaxx.
