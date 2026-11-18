# Claims registry

One entry per definition, lemma, theorem, corollary, assumption-dependent remark and finding.
No text may state a claim more strongly than its status here.

## Status values

- `draft`: written, no review round passed.
- `checked`: passed at least one review round with no open blocking or major issue, but not all required gates at the current commit.
- `verified`: G1 and G2 passed, and G3 where required, at the commit recorded in `verified_by`.
- `refuted`: an error or counterexample was accepted. `refuted_by` must point to it. A refuted claim is never deleted.
- `legacy-unverified`: imported from existing work, never reviewed under this workflow.
- `provisional`: depends on a checkpoint decision that the human has not confirmed (`provisional_on`). Never stated as more
  than `checked`. Accepting the decision restores `base_status`; reversing it sets the claim to `draft` and requeues its brief.
  Set and cleared only by `python3 ~/dotclaude/scripts/decisions.py`.

## Reset rule

Editing a claim, or any claim it depends on (transitively), resets `verified` to `checked`.
The regression-checker lists affected claims after every edit. The orchestrator applies the reset.

## Entry format

Keys are fixed. Lists are comma-separated. `none` for empty.
`verified_by` is a semicolon-separated list of `<gate>:<reviewer>:<model>@<commit>`.
`refuted_by` is `none` unless status is `refuted`, and then it is required.
`provisional_on` lists D-IDs, `none` unless status is `provisional`. `base_status` is the status the claim returns to.

## C1
- label: <lem.name | none>
- type: <definition | lemma | theorem | corollary | remark | finding>
- statement: <one line, or pointer to file and label>
- status: draft
- assumptions: <A1, A2 | none>
- depends_on: <C2, C3 | none>
- verified_by: none
- refuted_by: <issue ID, e.g. G2/counterexample-hunter/2, or counterexample file | none>
- provisional_on: none
- base_status: none
- notes: none
