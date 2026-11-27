# Contracts and production

## Public puzzle and verification

The catalog binds a mechanic version, exact board fields, question, rules, two compatible art worlds, a proposal function and an oracle. `PuzzleSpec` schema 1 serializes ordinary JSON. Board locations use zero-based column and row coordinates. Letters refer to the listed answer choices. The screen-reader description spells out one-based coordinates, wiring, symbolic relationships or run lengths.

Generation starts a deterministic random stream from the mechanic name, signed integer seed, level and version. A proposal contains only public geometry and choices. The oracle receives only that board. It derives candidate outcomes and witnesses, and the shared gate requires exactly one winning letter and a mechanic-specific minimum reasoning depth. The gate rejects malformed geometry, contradictory evidence and insufficient reasoning. Generation retries within a 12,000-proposal limit and fails explicitly on exhaustion. Revalidation recomputes the witness, checks the complete serialized contract and regenerates the board from the seed. Changes to a generator or ruleset that reinterpret saved data require a new mechanic version and a version-specific reader.

A content-derived ID omits the seed and presentation. Inventory has a second canonical fingerprint which removes superficial choice reordering and passage serialization order. It retries repeated content and records the rejections. The benchmark runs two catalog cycles in different settings, followed by five further instances of each mechanic. The allowable order prevents adjacent repetitions of a world.

## Difficulty and timing

The spec records steps (trace length, constraints or substitutions), branching, alternatives, simultaneous rule length and a per-distractor measurement in domain units. Examples include distance to a laser trace, satisfied lock clues, surplus fare and differing tile cells. The renderer measures the actual text bounds and contrast after selecting a set. The requested levels change board size, distribution, shape density, topology or available components according to the mechanic. These measures guide timing. Their correlation with perceived difficulty needs a viewer study.

The first video frame already contains the objective, rules, board and options. One immutable solve surface feeds every solving frame. A playhead moves outside the clue regions. The timeline contract includes a full-length interval for every required field. The last three seconds expose the oracle witness, with progressive path tracing where appropriate. No-reveal mode ends at the end of the solve interval. Both variants keep a separate answer still in the review folder.

## Scene construction

| Set | Composition and material |
| --- | --- |
| Optics Lab | Recessed dark instrument well, etched mirror field, rail lighting, vent panels and monospaced labels |
| Tidal Archive | Axonometric masonry, terraced plinths and ceramic signage. The ruins maze uses an extruded projection of its actual wall graph |
| Bureau of Evidence | Desk grain, layered file folio, clipped paper, red binding thread, magnifying glass and serif notes |
| Brass Works | Engineering grid, cast plates, slotted fasteners and mechanical teeth. Workshop covers place the diagram above the question |
| Form Studies | Oversized serif type and open page with color-block print geometry. Main subject and title sit on the same printed sheet |
| Pocket Arcade | Molded cabinet, recessed game screen, upper marquee, joystick and colored physical buttons |

The board painter uses semantic positions and shape geometry. All clue text is drawn on an opaque, high-contrast surface. Changing the set never substitutes a different logical relationship. Each set has an original synthesized sound palette. The seed selects pitches and the reveal adds a resolution phrase. The primary collection uses programmatic illustration. Mobile readability, dramatic impact and appeal are editorial judgments.

### Asset provenance and optional local backplates

The six procedural environments, geometric icons, cover art and audio synthesis were authored in this package for BlinkPuzz. The collection includes a per-world credit register under `assets/credits.json`. Runtime fonts come from the system DejaVu installation under the DejaVu / Bitstream Vera font licenses. Only rasterized lettering is exported. No third-party photos, audio recordings or external generation calls were used in the benchmark.

Both production commands accept an optional `--scene-pack path/to/pack.json`. A licensed, commissioned or separately approved provider image can be delivered through this same local adapter. A world entry has `file` (relative to the pack), `artist`, `source` (plain attribution), `license` and the image's full `sha256`. Supported declarations are `original-owned`, `CC0-1.0` and `CC-BY-4.0`. The supplier must establish reuse rights. The software verifies the declared file digest, strips embedded metadata, packages the cropped backplate and preserves its credit. A missing image falls back to procedural art and records the reason. Invalid attribution or a changed image stops the build.

Marginal external generation cost for this collection was zero. Higher-end assets require an actual quote, usage rights and owner approval before purchase. The local renderer can reuse approved art across compatible boards. Content review should screen any imported artwork for incidental text and misleading details.

## Output integrity

Package components live under `blinkpuzz2/`. Compact modules keep the contract, seed and validation functions together, with separate modules for each oracle/generator, game drawing, set construction, local assets, storyboard, media, planning and collection QA. The runtime imports no live automation modules.

A production run writes to a private sibling directory, validates full delivered media, writes the quality report and promotes the directory. The ZIP is CRC-tested before installation. A failed build leaves the published collection path free of partial output. A matching rerun revalidates stored media. SHA-256 hashes, solver replay, decoded-frame comparisons and cover comparisons all have to pass before the folder can be exported. Media and archive bytes belong under ignored `build/v2/`. Font files, Pillow, FreeType and encoder builds affect pixel and media hashes across machines. The stable board identity and oracle witness are independent of these libraries.
