# Playbook: paper-revision

Revise an existing paper: reviewer comments, a new venue, or requested changes.

## S1 Ingest paper
- goal: the paper builds; its structure, macros and labels are recorded.
- agent: orchestrator; G0 lint.
- output: `glossary.md` macros; build log; list of sections and labels in the brief Result.
- acceptance: `latexmk` builds; every macro used in the paper is in the glossary.
- gates: G0.

## S2 Claims and assumptions registry
- goal: every definition, lemma, theorem and assumption of the paper in `claims.md` and `model.md`.
- agent: `modeler` (A-IDs from the model section), then `theorem-writer` (claims, statements as pointers).
- output: `model.md`; `claims.md` with status `legacy-unverified`; dependency edges.
- acceptance: every labelled statement has an entry; every proof's dependencies are recorded.
- gates: G1, G5 (model).

## S3 Targeted changes
- goal: the changes listed in the contract (R-IDs), one brief per change.
- agent: the producer that owns the content (`prover`, `property-writer`, `exposition-writer`, ...).
- output: edited LaTeX; updated `claims.md` entries.
- acceptance: each change traces to an R-ID; nothing outside the listed changes is edited.
- gates: G0, G1, G2 for changed claims, G3 for changed main theorems.

## S4 Regression review
- goal: every claim affected by the changes is re-reviewed.
- agent: `regression-checker`, then G2 verifiers on each listed claim.
- output: list of affected claims; issue reports.
- acceptance: every affected claim is back at `checked` or `verified`; legacy claims touched by a change are reviewed, not left legacy.
- gates: G0, G1, G2, G3 for main theorems, G4, G5 (deliverable).
