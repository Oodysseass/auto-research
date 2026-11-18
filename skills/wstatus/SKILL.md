---
name: wstatus
description: Status of a research workflow project (.work/). Playbook stage, open issues by severity, claims by status, pending decisions, requeued work, both git repos, new inputs in resources/. Read-only. Named wstatus because /status is a built-in command.
disable-model-invocation: true
---

# Workflow status

Read-only. Never edit or commit.

1. Read `.work/state.md`, `.work/claims.md`, `.work/approvals.md` (Log), the latest handoff, and `python3 ~/dotclaude/scripts/decisions.py list`.
2. Issues: for each artifact slug in `.work/issues/`, run `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>`.
   Its `open issues:` line counts open canonical issues by severity; sum them.
3. Repos: `python3 ~/dotclaude/scripts/repos.py check`. Resources: `python3 ~/dotclaude/scripts/resources.py scan` (without `--warn`).
4. Reply as one short block:
   - stage: `<id> <name>`, active brief, branch, last handoff
   - issues: blocking / major / minor open, and per non-converged artifact its status (`open | deadlocked | stalled | max_rounds | converged-provisional`)
   - claims: count per status (`draft checked provisional verified refuted legacy-unverified`)
   - decisions: open and provisional cards, one line each (D-ID, class, question); requeued briefs
   - repos: project repo clean or dirty, `.work` repo clean or dirty; workflow files tracked by the project repo: `none`
     (anything else is a fault: say so first); missing exclude lines if any. For a project in a subdirectory of the
     project repo (`project:` line), name the subdirectory: every check covers it only, and changes elsewhere in the repo
     (coauthors' folders, sibling projects) are not reported. Each `also loaded:` line (a `CLAUDE.md` above the project,
     e.g. `reports/CLAUDE.md`) is reported once, as "also loaded", never as an error
   - resources: new files not yet processed (the next `/orch` session handles them), unwarned edits or deletions, and
     `resources/` files still tracked by the project repo
   - no tokens or budgets: those are never the human's concern
