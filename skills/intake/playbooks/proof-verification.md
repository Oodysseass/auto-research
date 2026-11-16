# Playbook: proof-verification

Check existing statements and proofs. No new results. Deliverable: a verdict per claim.

## S1 Ingest statements
- goal: every statement in scope in `claims.md`, every assumption in `model.md`.
- agent: `modeler` (A-IDs), then `theorem-writer` (claims as pointers, dependencies).
- output: `model.md`; `claims.md` with status `legacy-unverified`.
- acceptance: every in-scope statement has an entry with label and dependencies; implicit assumptions are listed and marked as implicit.
- gates: G1, G5 (model).

## S2 Assumption audit
- goal: every proof uses only listed assumptions and listed claims.
- agent: `assumption-auditor`, one brief per proof.
- output: G2 reports.
- acceptance: every proof audited; each silent assumption reported.
- gates: G2 (`assumption-auditor`).

## S3 Step-by-step check
- goal: every proof checked line by line.
- agent: `proof-checker`; `proof-checker-mythos` for main theorems.
- output: G2 reports.
- acceptance: every step either justified or reported.
- gates: G2 (`proof-checker`).

## S4 Counterexample search
- goal: explicit counterexamples to statements or proof steps.
- agent: `counterexample-hunter`, ladder per routing.md.
- output: G2 reports; `.tried.md`; counterexample files.
- acceptance: every statement attacked at the rung its importance warrants.
- gates: G2 (`counterexample-hunter`), G3 for main theorems.

## S5 Verdict per claim
- goal: a verdict per claim: `verified`, `refuted` (with counterexample), or open with the gap.
- agent: `report-writer`.
- output: verdict report named in the contract; final `claims.md` statuses.
- acceptance: every in-scope claim has a verdict tied to issue IDs; no verdict stronger than the gates support.
- gates: G0, G1, G4, G5 (deliverable).
