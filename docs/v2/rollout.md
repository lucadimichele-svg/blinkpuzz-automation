# Review, measurement and later rollout

The current deliverable ends at a local review packet. `review_handoff.json` contains relative media paths, caption, accessibility text, puzzle ID and editorial review status. The `enable_live_integration` adapter switch defaults to false. Enabling it fails explicitly until a separately reviewed integration exists. The existing production scheduler, queue and account configuration are independent.

1. Inspect the pilot and proof sheets, play the films on a phone, and replay a selection of the JSON proofs. Ask unfamiliar viewers to state the objective after two seconds. Record misread symbols, alternative interpretations and observed solve times.
2. Shadow-generate the candidate inventory with a separate output root. Review a sample against the existing schedule and media identifiers. Keep the candidate media in short-lived review storage.
3. A future, separately approved publisher change can map approved manifests to explicitly designated test slots. It must preserve duplicate protection, review state, existing posts and independent account targeting.
4. Compare actual Instagram Insights at equal post ages. A limited trial and gradual expansion each require owner approval. A rollback disables the new integration and resumes the existing generation choice for future empty slots. Previously scheduled items require individual owner review.

The CSV template in each collection includes puzzle ID, post age, views, average watch time, shares, comments and follows. Leave unmeasured rows blank. Protected account access is unnecessary.

```bash
python -m blinkpuzz2.cli insights --folder build/v2/pilots --csv build/v2/pilots/insights.csv
```

The importer computes watch fraction and per-hundred-view rates from real rows. Exploratory retest suggestions require more than one measured item of the same mechanic at the same post age. They are hypotheses susceptible to sample size, selection and timing effects. The benchmark contains no measurements of audience response.

The new read-only development workflow can validate pull requests targeting this development branch. Its optional full-render job uploads the ZIP with seven-day retention when an eligible workflow dispatch is available. GitHub may require a workflow on the default branch to expose manual dispatch. The documented local commands support the complete review independently. No hosted render is needed for this delivery. Local review artifacts persist until the workspace owner archives or removes them.
