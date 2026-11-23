# Working on dotclaude

Project instructions for this repo only. The root `CLAUDE.md` is the owner's global file (symlinked to `~/.claude/CLAUDE.md`); never put repo-only rules there.

## Design overview

`DESIGN.md` is the design overview of the workflow: intent, principles, decisions with reasons, status. It is imported below. The code is the source of truth for mechanics; `DESIGN.md` is the source of truth for intent. Where they disagree, flag it to the owner instead of silently following either.

@../DESIGN.md

## Keeping DESIGN.md current

- Any change that alters behavior updates `DESIGN.md` in the same commit, and `README.md` (the user guide) when it
  changes what the owner types, sees or checks.
- A design change also gets a new entry in section 12 (design history), with the reason.
- `DESIGN.md` and `README.md` never name a client or a client project.
