# State

Updated by the orchestrator at the end of every session (`/handoff`). Read first by every new orchestrator.

- updated: 2026-11-18
- playbook: new-paper, trimmed (S1, S4, S7, S8, S11)
- stage: 2 (S4 Model)
- active brief: S4-model (open, paused on needs_human)
- git branch: work/S4-model
- last handoff: .work/handoffs/20261118-1248.md

## Next actions

Stages of the trimmed new-paper playbook. Skipped: S2 Literature review, S3 Refine question, S5 Properties,
S6 Design, S9 Attacks and tightness, S10 Exposition (`resources/BRIEF.md:38-44`, `resources/BRIEF.md:49`).

1. S1 Question: done. Contract approved 2026-11-18 at 29c7db6.
2. S4 Model (in progress, paused on needs_human OP4; brief S4-model, round 1 done, revision r2 committed, rerun from G0 next): `modeler` writes `.work/model.md` from `resources/notes.md` "Model", without changes, as A-IDs; model section in `paper/lemmas.tex`. Gates G0, G1, G2 (`assumption-auditor`), G5 (model).
3. S7 Statements: `theorem-writer` states Lemma 1 (main) and Lemma 2 verbatim in meaning in `paper/lemmas.tex`; `claims.md` entries; roadmap. Gates G0, G1, G2 (`counterexample-hunter` on statements, ladder per routing; Lemma 1 at the main-theorem rung), G5 (statements).
4. S8 Proofs: `prover-mythos` for Lemma 1, `prover` for Lemma 2. If S7 or S8 produces an accepted counterexample, the lemma is marked `refuted` and the counterexample execution is written in `paper/lemmas.tex` under the unchanged statement (R5). Gates G0, G1, G2 full (`proof-checker-mythos` for Lemma 1), G3 (Codex) for Lemma 1.
5. S11 Full review, limited to `paper/lemmas.tex`: all gates at one commit, Codex at G3; final `claims.md` statuses. G5 (deliverable).

## Open approvals

- needs_human, blocks S4: G1/conformance-reviewer/2 (canonical; duplicate G2/assumption-auditor/1, major). Decide OP4 in `.work/model.md`: what a successful corrupted mining attempt produces. Then the glossary Terms row "mining attempt" is aligned to the decision (it currently says the corrupted success extends the chosen chain by one block, which `resources/notes.md` does not state). Response: `.work/issues/model.G1.conformance-reviewer.r1.response.json`.
- Before G5 (model): decide or explicitly leave open OP1 to OP7 in `.work/model.md`, "Open points". OP4 and OP5 decide which adversarial chains exist. Any decision that becomes an A-ID is a model change and is recorded in `approvals.md`.

## Budget used

| Brief | Rounds used / budget | Tokens used / budget (rough) |
|---|---|---|
| S4-model | G0 r1, G1 r1, G2 r1 / 5 | ~226k / 300k (modeler 87k + 51k, G1 41k, G2 44k) |
