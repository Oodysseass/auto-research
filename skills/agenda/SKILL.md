---
name: agenda
description: Show and change the agenda of a research workflow project (.work/threads.md) - the threads of work in priority order that rw works through. Add, reorder, park, resume, drop, or replace the whole slate. Planning only - never starts work. Usage /agenda [what to change, in plain words].
argument-hint: "[e.g. \"make the overlap proof first\", \"drop the simulation\", \"replace the slate with: verify all results, then rewrite sections 4 to 6\"]"
disable-model-invocation: true
---

# Agenda

Script: `A=~/dotclaude/scripts/agenda.py` (`python3 $A ...`, from the project root). It is the only writer of `threads.md`.
Request: `$ARGUMENTS`.

Planning is not doing. This skill changes the plan and stops. It never records a request, dispatches an agent, edits the
paper, or starts a thread, and it never blocks the plan on a contract question. Everything shown to the human follows
rules card 15: plain words, IDs only in a trailing `Refs:`.

1. `python3 $A list`. Show it as a short numbered table: position, title, status, next step (thread IDs in a last column).
   Say that `rw` works on the first `committed` thread and re-reads the agenda at every session.
2. No request: ask what to change, or stop.
3. Apply the plan the human states, in the order they give, with `--by human --reason "<the human's words, short>"`:
   - New threads: `add --title ... --goal ... [--covers <R-, DL- IDs it serves>]`, `committed` unless the human says to
     explore it first. Write goals in the human's terms (the section, what it should contain).
   - Reorder, park, resume: `move`, `set T<n> status=parked|committed`.
   - Threads the new plan replaces ("clean up the slate", "instead of"): `drop T<n> --reason "<replaced by ...>"`. If it is
     unclear whether an old open thread is replaced, ask once, in one dialog that lists them in plain words
     (options: drop them, park them, keep them).
   - Approach, style, outline or intent in the request (how sections should read, what to cut, what each section holds):
     append it verbatim to `resources/BRIEF.md` under `## Addendum <YYYY-MM-DD> (agenda)`, then
     `python3 ~/dotclaude/scripts/resources.py refresh resources/BRIEF.md --reason "agenda <date>"`. It binds later work
     through the conformance check.
4. Contract check, without asking: compare each new or moved thread with `contract.md` (scope, out-of-scope rows,
   deliverables) and the project rules in `CLAUDE.md`.
   - A thread that would need a contract or rule change to be done as stated: set
     `set T<n> next="decide first: <the question, one plain sentence>"`. It is asked when the thread starts (orch skill,
     step 6), as a blocking card. Tell the human in one line per thread, and offer to ask it now instead.
   - A dropped thread that leaves a requirement or deliverable without any thread: say so in one line. The contract
     itself does not change.
5. Commit the `.work` repo per the `commit-style` skill, e.g. `reorder agenda, park simulation`, `replace agenda`.
6. Show the new table, then the deferred questions, then stop. Do not start any thread.
