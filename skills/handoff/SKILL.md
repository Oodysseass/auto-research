---
name: handoff
description: End an orchestrator session in a research workflow project (.work/). Writes .work/handoffs/<timestamp>.md, updates .work/state.md, commits. Run at the end of every /orch session and whenever a hook asks for it.
---

# Handoff

Run from the project root. Do it even if the session did little: the next orchestrator knows only what is on disk.

1. Collect: commits since the last handoff (`git log --oneline <last handoff commit>..HEAD`, or the session's commits),
   changed files, claims whose status changed, open issues (`python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>`
   per artifact with reports), open approvals, budget used.
2. Write `.work/handoffs/<YYYYMMDD-HHMM>.md` from `.work/handoffs/_template.md`. Every section filled; `none` where empty.
   "Must not forget" holds only what no other `.work/` file records.
3. Update `.work/state.md`: `updated`, `stage`, `active brief`, `git branch`, `last handoff`, "Next actions", "Open approvals", "Budget used".
4. If a snapshot handoff `*-auto-precompact.md` exists from this session, fold its facts into the new handoff. Keep the snapshot file.
5. Commit `.work/` only: `git add .work && git commit -m "handoff: <YYYYMMDD-HHMM> <stage>"`.
   If other paths are dirty, do not commit them. List them under "Must not forget" and tell the human.
6. Reply in at most 5 lines: the handoff path, the stage status, the next step, and "start a new session with `rw`" if the stage is finished or paused.
