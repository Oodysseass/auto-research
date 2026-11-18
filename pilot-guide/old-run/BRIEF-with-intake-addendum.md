# Brief: Two longest-chain lemmas under one-round synchrony

This project brief is the authoritative statement of my intent. It is a pilot of the research workflow.

## Research question

In the model of `resources/notes.md`, do Lemma 1 and Lemma 2 of `resources/notes.md` hold, as stated?

## Position

- expected answer: both lemmas hold in the model of `resources/notes.md`.
- why: with one-round delivery, every honest party sees every honest chain within one round.
- what would surprise me: a lemma that fails in this model.

## What counts as a result

- For each lemma: a pen-and-paper proof in LaTeX that passes the review gates, or an explicit counterexample execution in the model.
- A refuted lemma stays in the document as stated, with its counterexample. It is never weakened silently.

## Model I have in mind

Fixed:
- The model of `resources/notes.md`, section "Model", without changes.
- Statements exactly as in `resources/notes.md`, section "Statements". Lemma 1 is the main result.

Open:
- none

## Closest prior work

- none: this is a toy pilot, and no literature is needed.

## Target

- venue: none (internal pilot); LaTeX in `llncs` format, one file `paper/lemmas.tex` with a `paper/main.tex` wrapper.
- deadline: none

## Not interested in

- a literature review.
- new protocols or changes to the protocol of `resources/notes.md`.
- probabilistic bounds: both lemmas are statements about every execution.
- attacks beyond what is needed to refute a lemma.
- an introduction, exposition, or a full paper.

## Addendum 2026-11-18

Answers given at intake.
- project type: new-paper, trimmed to the stages that this brief needs (model, statements, proofs or counterexamples, review). No literature review, design, attacks-and-tightness or exposition stages.
- ai_tools_allowed: claude, codex. Codex runs G3 on Lemma 1 and on the final deliverable.
- approvals: keep every default of `.work/approvals.md`.
- deliverable: `paper/lemmas.tex` (with the `paper/main.tex` wrapper) plus the final statuses in `.work/claims.md`. No separate verdict report.
