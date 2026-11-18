# Project: Two longest-chain lemmas under one-round synchrony (pilot)

- type: new-paper
- playbook: new-paper, trimmed (S1, S4, S7, S8, S11)
- inputs: `resources/` (read fully before producing anything)
- intent: `resources/BRIEF.md` (project brief) is authoritative. The SoW governs scope; the project brief governs approach.

## Workflow state

All state lives in `.work/`. Read these before any work:

- `.work/contract.md`: scope, requirements (R-IDs), deliverables. Binding.
- `.work/model.md`: model and assumptions (A-IDs). Binding.
- `.work/glossary.md`: terms, macros, notation. Wins over global glossaries.
- `.work/claims.md`: claim registry. Never state a claim stronger than its status.
- `.work/state.md`: current stage, next actions, open approvals.
- `.work/approvals.md`: what needs my approval.
- `.work/briefs/`, `.work/issues/`, `.work/handoffs/`, `.work/decisions.md`, `.work/deadends.md`.

Start a session with `rw` from the project root (runs `/orch` on the orchestrator tier). End it with `/handoff`.

## Build

`latexmk -synctex=1 -pdf -outdir=output main.tex` in `paper/`

## Project-specific rules

- The model and the lemma statements of `resources/notes.md` are fixed. Never change or weaken them; a refuted lemma keeps its statement and gets a counterexample.
- Neither lemma may be used in the proof of the other.
