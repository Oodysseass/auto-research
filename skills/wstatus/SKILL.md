---
name: wstatus
description: Status of a research workflow project (.work/). Playbook stage, open issues by severity, claims by status, pending decisions, requeued work. Read-only. Named wstatus because /status is a built-in command.
disable-model-invocation: true
---

# Workflow status

Read-only. Never edit or commit.

1. Read `.work/state.md`, `.work/claims.md`, `.work/approvals.md` (Log), the latest handoff, and `python3 ~/dotclaude/scripts/decisions.py list`.
2. Issues: for each artifact slug in `.work/issues/`, run `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>`.
   Its `open issues:` line counts open canonical issues by severity; sum them.
3. Reply as one short block:
   - stage: `<id> <name>`, active brief, branch, last handoff
   - issues: blocking / major / minor open, and per non-converged artifact its status (`open | deadlocked | stalled | max_rounds | converged-provisional`)
   - claims: count per status (`draft checked provisional verified refuted legacy-unverified`)
   - decisions: open and provisional cards, one line each (D-ID, class, question); requeued briefs
   - no tokens or budgets: those are never the human's concern
