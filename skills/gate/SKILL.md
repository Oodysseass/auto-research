---
name: gate
description: Run the review gates G0 to G4 on one artifact on demand, in a research workflow project (.work/). Usage /gate <artifact[#label]> [G1,G2,...].
argument-hint: "<artifact path[#label]> [gates, e.g. G1,G2]"
disable-model-invocation: true
---

# Gate on demand

Arguments: `$ARGUMENTS`. First token: the artifact (path, with `#label` for one claim). Second, optional: a comma-separated gate list.
Default: every gate that applies to the artifact, in order (review-gates skill, "Gates").

1. Load the `review-gates` and `model-routing` skills. Read `.work/contract.md` and `.work/claims.md`.
2. Find the brief that produced the artifact (`.work/briefs/`, Output section). If there is none, write `.work/briefs/adhoc-<slug>.md`
   from the template: goal "review <artifact>", acceptance criteria from the contract requirements and claims the artifact covers,
   budget 1 round per gate. Commit it.
3. Slug: the artifact slug used in earlier reports in `.work/issues/`, or a new one from the file name and label.
   Round: one more than the highest existing round for that slug, gate and reviewer.
4. Run each gate once, in order, with the write guard around every dispatch. Stop at the first gate that is not clean.
   Do not dispatch producers. Do not loop. Do not change claim statuses, except `verified` to `checked` when a gate is not clean.
5. Commit the reports. Reply with one line per gate: gate, reviewer, model, verdict, counts by severity, report path.
