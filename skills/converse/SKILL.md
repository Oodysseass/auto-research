---
name: converse
description: Conversation mode of a research workflow project (.work/). How a plain claude session discusses research with the project's context, offers to commit work, runs quick probes, and offers the capture dialog at natural breaks. Load at the start of a plain session in such a project, when the session-start note says so. Not under rw.
---

# Conversation

A plain session in a `.work/` project is a research discussion. Most of it is thinking: questions, ideas, counterexamples,
directions. Discussion is free; commitment is checked (DESIGN.md, principles 1 and 8).

## Context

- Read `.work/contract.md`, `model.md`, `glossary.md` and `claims.md` before the first substantive answer, and `threads.md`
  for the agenda. The prompt hook adds the agenda, open questions, ideas and dead ends, or the items related to the prompt.
- Answer inside the project model. Name assumptions (A-IDs) and claims (C-IDs) when you use them. Say when something goes
  beyond the model or the contract scope. Never state a claim stronger than its status.
- Check `deadends.md` before proposing an approach; say if one was tried.

## Never during discussion

- Change the paper, code, `claims.md`, `contract.md`, `model.md` or `threads.md`, or commit in either repo.
- Dispatch producers or run gates. Only quick probes (below).
These need a commitment: the `request` skill.

## Commitment

Work is committed when the human asks for it ("write it up", "prove it", "restructure", "add a section on X", "drop the
liveness part", "make Y first") or accepts your offer. Offer at most once per topic, in one line, when the discussion has
settled something worth doing: "Shall I commit this? It would <what changes, which files or agenda items>."
On a commitment, load the `request` skill. Its step 1 records the human's prompt with the agreed scope (`--scope`).
Agenda changes (add, reorder, park, drop threads) are commitments too: the request skill classifies them.
Before a commitment that ends a long discussion, offer the capture dialog first (below), so ideas from it are not lost.

## Quick probes

A cheap check of an idea during discussion, when the human asks or when it would settle a question fast:
- counterexample attempt: `counterexample-hunter` (Sonnet, default effort) on the stated claim and the project model;
- literature check: `literature-scout` on one narrow question;
- model check: `conformance-reviewer` on whether a statement fits the model and contract.
Dispatch one agent with a short prompt that names the statement, the binding files, and the output path
`.work/issues/probes/<YYYYMMDD-HHMM>-<slug>.md` (ignored by the `.work` repo). Report the result in chat, labeled
"probe, unverified". A probe never changes a claim status, writes no other file, and is kept only if the human ticks it in
a capture (as an idea or a dead end). Never run a probe the human did not ask for if it costs more than one cheap dispatch.

## Capture at natural breaks

At a topic change, before a commitment, and when the human signs off, offer: "Capture this discussion?" On yes, or on
`/capture`, follow the `capture` skill. Never write ideas, dead ends or decisions without the dialog.
