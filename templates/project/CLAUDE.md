# Project: <name>

- type: <project type>
- playbook: <playbook name>
- inputs: `resources/` (read fully before producing anything)

## Workflow state

All state lives in `.work/`. Read these before any work:

- `.work/contract.md`: scope, requirements (R-IDs), deliverables. Binding.
- `.work/model.md`: model and assumptions (A-IDs). Binding.
- `.work/glossary.md`: terms, macros, notation. Wins over global glossaries.
- `.work/claims.md`: claim registry. Never state a claim stronger than its status.
- `.work/state.md`: current stage, next actions, open approvals.
- `.work/approvals.md`: what needs my approval.
- `.work/briefs/`, `.work/issues/`, `.work/handoffs/`, `.work/decisions.md`, `.work/deadends.md`.

Start a session with `/orch`. End it with `/handoff`.

## Build

<e.g. `latexmk -synctex=1 -pdf -outdir=output main.tex` in `paper/`>

## Project-specific rules

- <rule | none>
