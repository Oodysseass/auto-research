# Research workflow for Claude Code

This repo is a Claude Code setup for research work: papers, proofs, protocol design, security reviews and client reports.
It gives Claude Code a team of specialist agents, an independent review pipeline (Codex as a second model), and project
memory on disk. This README is the user guide: what to do, what to type, what to check. `DESIGN.md` explains why it is
built this way.

## The idea

Each project has a folder `.work/` that is the project's memory: what you were asked to do, the model, the claims,
decisions, the agenda, ideas. You never edit it; the sessions do. You work in two ways:

- **Plain `claude` in the project folder.** You are present. By default it is a discussion. When you ask for real work,
  the session runs it with reviews, shows a short summary, commits, and waits.
- **`rw` in the project folder.** Autopilot. It works through the agenda, one thread per session, each with fresh context.
  It asks you in dialogs (with a desktop notification) and keeps going.

Everything else is options on top of these two.

```
 new project                                   existing project
     |                                              |
 resources/ + /intake                        claude: raw: run project_update.py
     |                                              |
 approve contract + agenda  <-------------------------
     |
     v
 +--------------------- daily loop ----------------------+
 |  claude          discuss, quick probes, /capture      |
 |  /agenda         reorder, add, park, drop threads     |
 |  "do it"         commitment: work + reviews + summary |
 |  rw              autopilot through the agenda         |
 |  read summaries, answer questions, read diffs, push   |
 +-------------------------------------------------------+
```

## Starting a project

**New project.**
1. Make the project folder. Put every input in `resources/`: the SoW, papers, notes, drafts.
2. `claude` there, then `/intake`. It gives you a project brief template (`resources/BRIEF.md`, client or research). Fill it
   once: goal, your position (what you expect the answer to be), what you are not interested in, constraints, format.
   Run `/intake` again.
3. Intake sets up `.work/` as its own git repo, hides the workflow files from your project repo, classifies the project,
   writes the contract (requirements, deliverables, out of scope), seeds the agenda from a playbook, and asks you to approve
   the contract and the agenda. Read both.

**Existing project from before the workflow.** Migrate it once with `setup-prompts/03_migrate_project.md` (paste it in a
`claude` session in the project). It keeps everything: old instructions and memory go to `.work/legacy/`, inputs to
`resources/`, old claims are registered as `legacy-unverified`.

**Project made with an older version of the workflow.** In a session there, type:
`raw: run python3 ~/dotclaude/scripts/project_update.py and commit its .work changes`.
It is safe to run twice. `rw` also runs it by itself when the agenda is missing.

A project may live in a subfolder of a larger repo (several reports in one repo). Start sessions in the project folder,
the one that contains `.work/`.

## Your three levers for direction

| What you want to change | Where it lives | How | Cost |
|---|---|---|---|
| Order, what to work on next | agenda, `.work/threads.md` | `/agenda ...` or say it in conversation | applied at once, logged |
| What counts as done (requirements, deliverables, out of scope) | contract, `.work/contract.md` | say it ("add X as a deliverable") | a blocking question with the consequences first |
| Intent, approach, style | `resources/BRIEF.md` | say it in a session; it is recorded verbatim with the date | every artifact is checked against it |

Agenda statuses: **committed** (`rw` works on it), **exploring** (an idea under consideration; `rw` skips it), **parked**,
**done**, **dropped** (kept on record, never deleted). `rw` takes the first committed thread and re-reads the agenda every
session.

`/agenda` is planning only. It never starts work and never blocks on a contract question. If a thread would need a contract
change (for example a section the contract keeps out of scope), it gets a "decide first" question,
asked when that thread starts. Approach and style you give with it ("shorter", "the protocol section describes only the
algorithms") go into the brief and bind the later work.

```
/agenda                                     show it
/agenda make the safety proof first
/agenda park the simulation
/agenda add a thread: safety under a weaker network model, exploring
/agenda replace the slate with: check the proofs; then rewrite the analysis, shorter
```

## Everything you can type

| You type | What happens |
|---|---|
| `claude`, then talk | Discussion. The session reads the contract, model, claims and agenda, reminds you of related ideas and dead ends, and changes nothing. |
| "write it up", "prove it", "restructure section 5", "yes, do it" | Commitment. Recorded in the brief with the scope you agreed, then the work, the reviews, a short summary, commits, and it waits. |
| `quick: <task>` | Commitment with light checks (lint and the conformance check). Never raises a claim's status. For wording and small fixes. |
| `full: <task>` | Commitment with every check: lint, conformance, proof check, counterexample search, Codex, style. |
| `raw: <anything>` | Plain Claude Code: nothing recorded, no reviews. |
| `/agenda [change]` | Show or change priorities (above). |
| `/capture` | Keep ideas, open questions, dead ends and decisions from the discussion. Only what you tick is kept. |
| `/wstatus` | One screen: current thread, agenda, open issues, claims by status, pending questions, both repos, new inputs. |
| `/why <ID or file or commit>` | Why something is the way it is, from the files: a claim, decision, request, thread, idea, issue. |
| `/gate <file[#label]> [G1,G2]` | Run the reviews on one artifact on demand. |
| `/escalate <claim or issue>` | Rerun the last review of it one level stronger. |
| `/retro` | After a milestone: proposals for the domain knowledge, playbooks or rules from what went wrong. You approve each. |
| `/workflow-guide <question>` | How the workflow itself works, answered from this README and `DESIGN.md`. |
| `/intake [framing]` | Start a new project (once). |
| `rw` | Autopilot through the agenda. |
| `rw --stop-before T6` | Autopilot, stopping before thread T6 (or playbook stage S6). |

Stopping `rw`: quit the Claude session (the loop stops with it), or Ctrl+C between sessions. At the subscription limit it
waits for the reset and resumes; Enter resumes early.

## When to discuss, commit, or run rw

- **Discuss** when you are thinking: is this attack real, how to model X, which design is better. Ask for a quick probe
  ("try a counterexample to this") when a cheap check would settle it; it is labeled "probe, unverified" and changes
  nothing. End with `/capture`, or accept the session's offer to commit.
- **Commit** when you know what you want done and want to watch it: fix this proof, write this section, restate this lemma.
- **`rw`** when the agenda is right and the work is long: a proof pass, the attack pass, the report. Check `/agenda` first.
  Use `rw --stop-before` to look before a given step.
- **`raw:`** for anything unrelated to the project.

A good rhythm: discuss, capture, fix the agenda, run `rw`, read the summaries and approvals, push.

## When it asks you something

Questions are always about research content, scope or direction, in plain words. IDs (C36, R13, D1, ...) appear only in a
trailing "Refs:" so you can ask `/why` about them.

| You see | What it is | Check before answering |
|---|---|---|
| "Shall I commit this? It would ..." | an offer to turn discussion into work | is the scope sentence what you mean, and does it touch only what you expect? |
| a dialog with 2 to 4 options, one Recommended | a decision. **Blocking**: work waits. **Checkpoint**: work continues on the recommendation, you confirm later | read each option's consequence, not just its label; pick Other and type "why" if unsure |
| checkpoint screen, then "Make these provisional decisions final?" | a batch of choices taken provisionally | "Review individually" if any surprises you; a reversal re-queues the work that depended on it |
| approval summary, then an approval question | end of a milestone, or the model, contract or main statements | read "Review findings" and above all "What remains uncertain"; approve only what you would sign |
| capture dialog (tick boxes) | ideas, questions, dead ends, decisions from the discussion | tick only what you would want to see again in a month |
| short summary after a commitment (Changed, Review, Uncertain, Commits) | the work is done and committed | open the changed sections; note anything provisional or not checked |
| "Capture pending from an earlier session" | the last session ended without saving the discussion | yes if it was a real discussion |
| "Unprocessed inputs in resources/" | you dropped files | confirm what it says each file is about |

When you disagree with the recommendation, pick another option or "Other" and say why. Your reason is recorded.

## What you do by hand

**Inventory you keep.**
1. `resources/`: drop every input here, each new SoW version, papers, the client's notes, your notes. Never edit or delete a
   file in it; add a new version instead. New files are noticed at the next session. Unrelated files are recorded; a file
   that touches the contract gets a question; a new SoW gets a blocking question.
2. `resources/BRIEF.md` at the start (intake gives the template). Later intent: just say it in a session.
3. Anything outside the workflow's view (a `git stash`, an email, a call with the client): tell a session, so it is recorded.

**What you check.**
1. Commits in your project repo before you push. The workflow commits locally on your branch and never pushes. Read
   `git log` and the diff, then push. If you want every project commit asked first, add the row
   "A commit in the project repo | blocking" to the project's `.work/approvals.md` (ask a session to do it).
2. The model and the main statements at approval time: the most expensive things to get wrong. Read them in full.
3. Claim statuses before you rely on them: `verified` (passed conformance, proof check, counterexample search, and Codex for
   main results), `checked`, `provisional` (waits on a decision of yours), `legacy-unverified` (from before the workflow),
   `draft`. Until the pilot rerun is done, read main proofs yourself even when `verified`.
4. Before anything goes to a client: the deliverable itself, and the "Uncertain" line of the last summary.

**What you never do.** Edit files in `.work/`, commit workflow files, push `.work`, or decide about tokens, models or review
rounds. If a session asks you about those, it is a bug.

## Example: a research paper

1. Folder with `resources/` (related papers, notes, a draft). `claude`, `/intake`, fill the research brief, `/intake`.
2. Intake picks the new-paper playbook and seeds the agenda: question, literature, refine question, model, properties,
   design, theorem statements, proofs, attacks and tightness, exposition, full review. Approve.
3. `/agenda park the literature review` if you know the field; `/agenda add a thread: impossibility under partial synchrony, exploring`.
4. Discuss the model. When it settles: "write the model up". Approve it when the summary comes; read the assumptions.
5. `rw`. It works through the agenda and asks at decision points.
6. New idea mid-project: discuss it, `/capture` it (it becomes an exploring thread), later `/agenda` commit it and move it up.

## Example: a client report

1. `resources/`: the SoW, the client's materials, earlier reports. `/intake`, fill the client brief (milestones, what is out
   of scope even if the SoW is vague, format). Intake writes one requirement per SoW item with its source.
2. Restructure the agenda around the milestones: `/agenda replace the slate with: first milestone design; its evaluation; final report`.
3. Discuss each design in plain sessions; commit the parts you settle; run `rw` for the long passes.
4. A new SoW version: drop it in `resources/`. The next session asks a blocking question before anything changes.
5. Before delivery: `/wstatus` (nothing open or provisional you did not accept), read the report, push, send.

## Weekly routine

1. `/wstatus`: what is next, what is blocking, what waits for you.
2. Answer pending questions and checkpoints.
3. Read the summaries since last time and the paper diff. Push.
4. Discuss anything new, `/capture`, adjust `/agenda`.
5. `rw`.

## How a commitment is checked

| Check | What it looks at |
|---|---|
| G0 lint and build | em dashes, `\Cref`, banned words, macros, labels, headings; the paper compiles |
| G1 conformance | the brief, contract, scope, model, glossary, claim strength, your position and out-of-scope rows |
| G2 technical | assumptions used, the proof line by line, a counterexample search; citations where asked |
| G3 Codex | an independent second model, for main results and deliverables |
| G4 style | your writing style (the `academic-writing` skill) |
| G5 you | approvals per `.work/approvals.md` |

Prose changes run G0, G1, G4. Statements, proofs, the model and findings run G0 to G4, with G3 for main results and
deliverables. Reviewers never see the producer's reasoning, only the artifact and the binding files.

## Files in a project

```
<project>/
  resources/          your inputs, append-only; BRIEF.md is your intent
  CLAUDE.md           project instructions (not tracked by the project repo)
  .work/              the workflow's memory, its own local git repo, never pushed
    contract.md       requirements, deliverables, out-of-scope checks
    model.md          the assumptions
    claims.md         every result and its status
    threads.md        the agenda
    ideas.md          ideas and open questions you kept
    decisions/        one file per question asked to you
    state.md          where the work stands
```

The project repo never tracks `.work/`, `CLAUDE.md`, `.claude/`, `resources/` or `output/` (`.git/info/exclude`), and
commit messages there carry no workflow terms, so coauthors see only the paper.

## Setup of this repo

- `~/.claude/CLAUDE.md`, `~/.claude/rules-card.md`, `~/.claude/agents`, `~/.claude/hooks` and each folder of `skills/` in
  `~/.claude/skills/` are symlinks into this repo.
- `~/.claude/settings.json` runs `hooks/rw_hooks.py` on SessionStart, UserPromptSubmit, PreCompact, Stop, PreToolUse,
  PostToolUse, StopFailure and SessionEnd, and as the status line.
- `bin/` is on `PATH` for `rw`.
- Codex CLI, logged in with the ChatGPT subscription, for G3.
- `git config core.hooksPath .githooks` once per clone (keeps the generated agent variants in sync).
- Tests: `scripts/run_tests.sh`.

Working on this repo: `.claude/CLAUDE.md` and `DESIGN.md`. Any change that alters behavior updates `DESIGN.md` in the same
commit.
