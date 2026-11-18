# Claims registry

One entry per definition, lemma, theorem, corollary, assumption-dependent remark and finding.
No text may state a claim more strongly than its status here.

## Status values

- `draft`: written, no review round passed.
- `checked`: passed at least one review round with no open blocking or major issue, but not all required gates at the current commit.
- `verified`: G1 and G2 passed, and G3 where required, at the commit recorded in `verified_by`.
- `refuted`: an error or counterexample was accepted. `refuted_by` must point to it. A refuted claim is never deleted.
- `legacy-unverified`: imported from existing work, never reviewed under this workflow.

## Reset rule

Editing a claim, or any claim it depends on (transitively), resets `verified` to `checked`.
The regression-checker lists affected claims after every edit. The orchestrator applies the reset.

## Entry format

Keys are fixed. Lists are comma-separated. `none` for empty.
`verified_by` is a semicolon-separated list of `<gate>:<reviewer>:<model>@<commit>`.
`refuted_by` is `none` unless status is `refuted`, and then it is required.

## C1
- label: def.honest-corrupted
- type: definition
- statement: paper/lemmas.tex#def.honest-corrupted (honest party and corrupted party)
- status: draft
- assumptions: none
- depends_on: none
- verified_by: none
- refuted_by: none
- notes: proposed by modeler, S4 revision r2

## C2
- label: def.chain-length
- type: definition
- statement: paper/lemmas.tex#def.chain-length (chain and length len(C); len(G) = 0)
- status: draft
- assumptions: none
- depends_on: none
- verified_by: none
- refuted_by: none
- notes: proposed by modeler, S4 revision r2

## C3
- label: def.successful-round
- type: definition
- statement: paper/lemmas.tex#def.successful-round (successful round)
- status: draft
- assumptions: none
- depends_on: C1
- verified_by: none
- refuted_by: none
- notes: proposed by modeler, S4 revision r2

## C4
- label: def.chain-at
- type: definition
- statement: paper/lemmas.tex#def.chain-at (C_P^r, the chain of honest party P at the end of round r)
- status: draft
- assumptions: none
- depends_on: C1, C2
- verified_by: none
- refuted_by: none
- notes: proposed by modeler, S4 revision r2

## C5
- label: def.min-max-len
- type: definition
- statement: paper/lemmas.tex#def.min-max-len (m_r and M_r)
- status: draft
- assumptions: none
- depends_on: C4, C2
- verified_by: none
- refuted_by: none
- notes: proposed by modeler, S4 revision r2
