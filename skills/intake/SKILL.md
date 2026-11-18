---
name: intake
description: Project intake for the research workflow (/intake [framing]). Reads resources/ and the project brief resources/BRIEF.md, makes .work/ its own git repo excluded from the project repo, classifies the project into one of seven types, writes .work/contract.md, approvals and the resources manifest, picks a playbook, and stops for human approval. Load when starting a new project, running /intake, or migrating a project into .work/.
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
3. If `.work/` holds anything besides `.git/` and `.gitignore` (an empty repo from `repos.py init` is fine), stop and ask.
   Intake never overwrites `.work/`. Migration of existing projects follows prompt 03.
   The project root is the directory where intake runs; `.work/` goes there. It may be a subdirectory of a larger repo
   (`reports/02-mitigations/`), and several projects may share one repo. If it is not inside any git repo, ask whether
   to run `git init` there. Stop until answered.
4. If a framing argument was given, append it verbatim to `resources/BRIEF.md` under a heading `## Addendum <YYYY-MM-DD>`.
   It is part of the project brief from then on.
5. Two repos. Run `python3 ~/dotclaude/scripts/repos.py init`: `.work/` becomes its own git repo, and the project repo's
   `.git/info/exclude` gets `.work/`, `CLAUDE.md`, `.claude/`, `resources/` and `output/`, prefixed with the project's path
   in the repo when it is a subdirectory (`/reports/02-mitigations/.work/`). Never write these into a committed
   `.gitignore`: that file would reveal the workflow. Never create or edit the project's `.gitignore` for the workflow.
   `repos.py init` lists what the project repo already tracks under those paths. Never untrack anything automatically:
   - Tracked `resources/` files: ask once for this project, options "Keep them tracked" and "Untrack them". Untracking is
     `git rm -r --cached resources` and one commit on the current branch, in the human's commit style, no workflow terms
     (e.g. `stop tracking resources folder`). Show the exact message in the option's description, and say that coauthors who pull
     the commit lose those files from their working tree (the files stay on disk here).
   - A tracked `CLAUDE.md` or `.claude/`: these must be untracked; `repos.py check` fails and `rw` refuses to start otherwise.
     Ask once, options "Untrack them" (same commit rules and coauthor note as above) and "Stop intake". Never put workflow text
     in a tracked file.
6. Scaffold `.work/` from `~/dotclaude/templates/project/.work/` (including `decisions/` and `packets/`), and the project `CLAUDE.md`
   from `~/dotclaude/templates/project/CLAUDE.md`. Never overwrite an existing project `CLAUDE.md`; propose a diff instead.
7. Classify the project. Use the table below. If two types fit, or the signals are weak, ask.

Asking, everywhere in intake: AskUserQuestion, at most 4 questions per call, recommended option first with "(Recommended)" and a one-line
reason in its description. Research content, scope and direction only: never tokens, budgets, model tiers, effort or file formats.
Never end the session to ask.
8. Check the project brief against the SoW, if there is one. The SoW governs scope; the project brief governs approach.
   List every conflict between them (an item the brief excludes that the SoW requires, a priority the SoW rules out, a deliverable format
   that differs). Ask the human to resolve each one. Do not resolve it yourself. Add each answer to the project brief under the dated heading.
9. Ask the human, in as few dialogs as possible, everything you cannot determine from `resources/`. Typical gaps: client or venue, format,
   deadlines, scope boundaries, which results count as main, whether `codex` is allowed. Do not guess. Answers go into the project brief
   under the dated heading, so that every requirement has a line to point to.
10. Write `.work/contract.md`. Every requirement gets an R-ID whose source is a line of `resources/BRIEF.md` or of the SoW
   (format in the contract template). No R-ID without a source line.
   Turn each item of the brief's "Position" and "Not interested in" sections (client: "Out of scope even if the SoW is vague")
   into a row of the contract's `## G1 checks` table, with its source line. The conformance reviewer checks every row at G1.
   Mark main theorems or headline results in the question or requirements, so routing can find them.
   Copy `ai_tools_allowed` from the brief's Constraints (client); default `claude, codex`.
11. Leave `.work/approvals.md` (Class table) at its defaults unless the human says otherwise.
12. Pick the playbook (same name as the type unless the human says otherwise). Copy its stage list into `state.md` as next actions; set stage 1.
13. Fill `.work/glossary.md` with terms and macros found in `resources/` (existing `.tex` macros, SoW terms). Leave `model.md` to the modeler.
14. Resources manifest, after the last addendum to `resources/BRIEF.md`: `python3 ~/dotclaude/scripts/resources.py init`.
    It lists every file in `resources/` with its sha256, size and date seen. From now on `resources/` is append-only: `/orch` reports
    new files and warns about edited or deleted ones.
15. Append to `decisions.md`: the classification and playbook, with a one-line reason (`class: blocking`, card `D1`).
    Commit in the `.work` repo (`git -C .work add -A && git -C .work commit`), message per the `commit-style` skill
    ("add contract and playbook"). Nothing is committed in the project repo, and no branch is created.
16. Approval (blocking): write card `D1` ("Approve the contract and the playbook stages?"; options approve / change scope / change
    playbook). Show the contract and the playbook stages in chat, then ask with `decisions.py compress D1`.
    Record the answer: `decisions.py accept D1 --option <x>`, a line in `approvals.md` (Log) with the commit
    (`python3 ~/dotclaude/scripts/repos.py rev`), and the contract's Approval section. Commit in the `.work` repo ("approve contract"). Then tell the human: run `rw` to start the workflow.

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
- Approval points come from `approvals.md`, not from the playbook. A stage marked "G5" asks for approval with the class `approvals.md`
  gives that event: `blocking` asks at once (with a packet), `checkpoint` proceeds provisionally and asks at the next checkpoint.
- One stage per orchestrator session. `rw` starts the sessions in a loop.
- A stage is done when every brief of the stage has converged at its gates. The orchestrator then advances `state.md`.
