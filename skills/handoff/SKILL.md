---
name: handoff
description: End an orchestrator session in a research workflow project (.work/). Writes .work/handoffs/<timestamp>.md, updates .work/state.md, commits, and marks the session end for bin/rw. Usage /handoff <stage-done | context | project-done | error>. Run at the end of every /orch session and whenever a hook asks for it.
argument-hint: "<stage-done | context | project-done | error> [reason]"
---

# Handoff

Run from the project root. Do it even if the session did little: the next orchestrator knows only what is on disk.
Outcome: the first word of `$ARGUMENTS` (`stage-done`, `context`, `project-done` or `error`); default `context` if the stage is not done.

Two repos: the project repo (paper, code) and the `.work` repo (`~/dotclaude/scripts/repos.py`).

1. Collect: commits since the last handoff in both repos (`python3 ~/dotclaude/scripts/repos.py log <revs at last handoff>`, from
   `state.md`; or the session's commits),
   changed files, claims whose status changed, open issues (`python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>`
   per artifact with reports), decision cards asked, answered, provisional or reversed (`decisions.py list`), requeued briefs.
2. Write `.work/handoffs/<YYYYMMDD-HHMM>.md` from `.work/handoffs/_template.md`. Every section filled; `none` where empty.
   "Must not forget" holds only what no other `.work/` file records. No token counts or budgets: usage is in `.work/usage.tsv`.
3. Update `.work/state.md`: `updated`, `stage`, `active brief`, `project branch`, `revs at last handoff` (`repos.py rev`, taken after
   the paper commits of step 5), `last handoff`, "Next actions", "Pending decisions", "Requeued".
4. If a snapshot handoff `*-auto-*.md` exists from this session, fold its facts into the new handoff. Keep the snapshot file.
5. Commit in the `.work` repo: `git -C .work add -A && git -C .work commit -m "update project state after <what the session did>"`,
   per the `commit-style` skill (e.g. "update project state after model review"). Do not commit in the project repo here.
   If it has dirty paths (`repos.py status`), leave them and list them under "Must not forget". Never push either repo.
6. Mark the session end: `python3 ~/dotclaude/scripts/rw_end.py <outcome> "<one-line reason>"`.
7. Reply in at most 3 lines: the handoff path, the outcome, the next step. Then end the turn. Under `rw`, the session ends by itself
   and the next one starts (`stage-done`, `context`). Never tell the human to restart anything.
