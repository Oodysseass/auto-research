---
name: wstatus
description: Status of a research workflow project (.work/). Playbook stage, open issues by severity, claims by status, pending approvals, budget. Read-only. Named wstatus because /status is a built-in command.
disable-model-invocation: true
---

# Workflow status

Read-only. Never edit or commit.

1. Read `.work/state.md`, `.work/claims.md`, `.work/approvals.md` (Log) and the latest handoff.
2. Issues: for each artifact slug in `.work/issues/`, run `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>`.
   Its `open issues:` line counts open canonical issues by severity; sum them.
3. Reply as one short block:
   - stage: `<id> <name>`, active brief, branch, last handoff
   - issues: blocking / major / minor open, and per non-converged artifact its status (`open | deadlocked | stalled | max_rounds`)
   - claims: count per status (`draft checked verified refuted legacy-unverified`)
   - approvals pending: one line each
   - budget: per active brief, rounds and tokens used against budget; flag any overrun
