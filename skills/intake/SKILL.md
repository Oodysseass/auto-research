---
name: intake
description: Project intake for the research workflow (/intake [framing]). Reads resources/ and the project brief resources/BRIEF.md, classifies the project into one of seven types, writes .work/contract.md and approvals, picks a playbook, and stops for human approval. Load when starting a new project, running /intake, or migrating a project into .work/.
argument-hint: "[extra framing, appended to resources/BRIEF.md]"
---

# Intake

Intake runs in the main session. It produces no paper content and dispatches no producers.

## Procedure

`/intake [framing]`. The optional argument is extra framing from the human: `$ARGUMENTS`.

1. Read `resources/` fully, every file. If `resources/` does not exist, say so and ask whether to create it. Stop until answered.
2. Read `resources/BRIEF.md`, the project brief. It is the authoritative statement of the human's intent.
   If it is missing, stop. Say so, and offer the matching template from `~/dotclaude/templates/project/resources/`:
   `BRIEF.client.md` if `resources/` holds a SoW or the request is client work, `BRIEF.research.md` otherwise (ask if unclear).
   On a yes, copy it to `resources/BRIEF.md` for the human to fill in. Do not fill it in yourself. Stop.
3. If `.work/` exists, stop and ask. Intake never overwrites `.work/`. Migration of existing projects follows prompt 03.
4. If a framing argument was given, append it verbatim to `resources/BRIEF.md` under a heading `## Addendum <YYYY-MM-DD>`.
   It is part of the project brief from then on.
5. Scaffold `.work/` from `~/dotclaude/templates/project/.work/` and the project `CLAUDE.md` from `~/dotclaude/templates/project/CLAUDE.md`.
   Never overwrite an existing project `CLAUDE.md`; propose a diff instead.
6. Classify the project. Use the table below. If two types fit, or the signals are weak, ask.
7. Check the project brief against the SoW, if there is one. The SoW governs scope; the project brief governs approach.
   List every conflict between them (an item the brief excludes that the SoW requires, a priority the SoW rules out, a deliverable format
   that differs). Ask the human to resolve each one. Do not resolve it yourself. Add each answer to the project brief under the dated heading.
8. Ask the human, in one message, everything you cannot determine from `resources/`. Typical gaps: client or venue, format,
   deadlines, scope boundaries, which results count as main, whether `codex` is allowed. Do not guess. Answers go into the project brief
   under the dated heading, so that every requirement has a line to point to.
9. Write `.work/contract.md`. Every requirement gets an R-ID whose source is a line of `resources/BRIEF.md` or of the SoW
   (format in the contract template). No R-ID without a source line.
   Turn each item of the brief's "Position" and "Not interested in" sections (client: "Out of scope even if the SoW is vague")
   into a row of the contract's `## G1 checks` table, with its source line. The conformance reviewer checks every row at G1.
   Mark main theorems or headline results in the question or requirements, so routing can find them.
   Copy `ai_tools_allowed` from the brief's Constraints (client); default `claude, codex`.
10. Leave `.work/approvals.md` at its defaults unless the human says otherwise.
11. Pick the playbook (same name as the type unless the human says otherwise). Copy its stage list into `state.md` as next actions; set stage 1.
12. Fill `.work/glossary.md` with terms and macros found in `resources/` (existing `.tex` macros, SoW terms). Leave `model.md` to the modeler.
13. Append to `decisions.md`: the classification and playbook, with a one-line reason. Commit on a new branch `work/intake`.
14. Stop. Show the contract and the playbook stages, and ask for approval. Record the answer in `approvals.md` (Log) and in the contract's Approval section.

## Classification

| Type | Signals in `resources/` or the request |
|---|---|
| client-security-review | SoW asking to review, audit or assess an existing protocol, spec or code |
| client-design | SoW asking to design or improve a protocol or mechanism |
| new-paper | a research question or idea, no draft paper |
| paper-revision | an existing paper draft plus reviews, a new target venue, or requested changes |
| literature-review | a request to survey or compare work on a topic |
| proof-verification | existing statements and proofs to check, no new results asked for |
| open-ended | a hunch or direction without a fixed question or deliverable |

## Playbooks

One file per playbook in `playbooks/`. Each stage lists: goal, agent, output, acceptance criteria and gates.
The orchestrator turns one stage into one or more briefs from `.work/briefs/_template.md`. Tiers per the model-routing skill.

- [client-security-review](playbooks/client-security-review.md)
- [client-design](playbooks/client-design.md)
- [new-paper](playbooks/new-paper.md)
- [paper-revision](playbooks/paper-revision.md)
- [literature-review](playbooks/literature-review.md)
- [proof-verification](playbooks/proof-verification.md)
- [open-ended](playbooks/open-ended.md)

Common to all playbooks:
- Approval points come from `approvals.md`, not from the playbook. A stage marked "G5" stops for approval only if `approvals.md` says `yes` for that event.
- One stage per orchestrator session.
- A stage is done when every brief of the stage has converged at its gates. The orchestrator then advances `state.md`.
