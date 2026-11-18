---
name: agenda
description: Show and change the agenda of a research workflow project (.work/threads.md) - the threads of work in priority order that rw works through. Add, reorder, park, resume, drop. Usage /agenda [what to change, in plain words].
argument-hint: "[e.g. \"make the overlap proof first\", \"drop the simulation\", \"add a thread on partial overlap\"]"
disable-model-invocation: true
---

# Agenda

Script: `A=~/dotclaude/scripts/agenda.py` (`python3 $A ...`, from the project root). It is the only writer of `threads.md`.
Request: `$ARGUMENTS`.

1. `python3 $A list`. Show it as a short numbered table: position, ID, title, status, next step. Say that `rw` works on the
   first `committed` thread and re-reads the agenda at every session.
2. No request: ask what to change, or stop.
3. A request: classify each change with the Class table of `.work/approvals.md` and `contract.md`:
   - reorder, park, resume, a new thread inside the contract scope, or dropping a thread that no R- or DL-ID needs: `logged`.
     Apply at once: `move T<n> --top|--before T<m>|--after T<m>`, `set T<n> status=parked|committed`, `add --title ... --goal ...
     [--covers IDS] [--status committed|exploring]`, `drop T<n> --reason "<why>"`. Pass `--by human --reason "<the human's words>"`.
   - adds or drops a requirement or deliverable, or crosses an N-row: this is a scope change. Load the `request` skill and run it
     as a commitment (it records the request and asks a blocking card). Apply the agenda change only after option A.
   - a thread whose work is in progress under `rw` (the `- stage:` line of `state.md`): say that the change takes effect at the
     next `rw` session.
4. Commit the `.work` repo per the `commit-style` skill, e.g. `reorder agenda, park simulation`.
5. Show the new table.
