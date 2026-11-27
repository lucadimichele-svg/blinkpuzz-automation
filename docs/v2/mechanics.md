# Games and oracle witnesses

The playable objective is printed on the opening frame. Each instance has three choices. To inspect one pilot, find its numbered JSON in `specs/`, read `board` and `rules`, then open the matching file in `proofs/`. The `validate` command recomputes the answer directly from the board. Directions, marks, shapes, gaps, labels and widths carry meaning in monochrome.

| Engine | Public problem | Oracle and replay |
| --- | --- | --- |
| laser | Follow an eastbound beam through diagonal mirrors to a crystal | Trace position and direction until a receiver, boundary or repeated state. Require two or more reflections. Replay visits in order |
| maze | Pick the entrance connected to the flag through open passages | Reverse BFS from the exit tests all three gates and recovers the corridor. Walls between adjacent cells correspond exactly to closed graph edges |
| circuit | Flip one displayed switch to light the output | Evaluate the initial state and each single-toggle state through the shown inverters and two gates. Proof includes the three post-inverter bits, intermediate output and lamp bit for each state |
| pipes | Insert one spare without rotating it to join IN and OUT | Test all three candidates using reciprocal compass ports, grid boundaries and loop termination. The successful trace must pass through the gap |
| routes | Choose the first stop of the cheapest left-to-right trip | Enumerate every complete directed path and its sum. Reject all ties, including two optimum paths through the same first stop |
| lock | Choose the ordering of four recognizable objects satisfying all three notes | Enumerate all 24 permutations before testing displayed strips. Reject contradictory, redundant and underdetermined note sets. Store the per-candidate truth matrix |
| pattern | Continue the indicated sequence of clockwise quarter-turns | Rotate the actual nine-bit tile by coordinate permutation. Verify the displayed example, exclude symmetric cycles and match the target exactly |
| balance | Use two level scales to match a third load | Enumerate all 216 assignments of three integer shape masses from one to six. Require agreement across all compatible models. Each individual scale alone must leave the winning equality unresolved |
| nonogram | Identify the four-by-four print that satisfies all row and column runs | Enumerate row-compatible bitmaps, then enforce every column clue. Require a unique full bitmap before examining the offered prints |
| gears | Find the marked wheel turning clockwise with the drive | Derive contacts from positions of equally sized wheels. Propagate and cross-check direction and depth over the full connected assembly. Show the direction groups in the replay |

These puzzles use the specific displayed game models. Background scenery supplies no physical assumptions. The benchmark includes two rendered instances and five additional verified specs of each engine. The test suite also checks visible structural variability independently of seed identifiers.
