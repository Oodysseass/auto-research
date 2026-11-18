# Research workflow: design overview

Read this first when working on `~/dotclaude`. It records what the workflow is for, how it is meant to work, why each part exists, and where the build stands. The code is the source of truth for mechanics; this file is the source of truth for intent. Where they disagree, flag it to the owner instead of silently following either. Intent that the code does not implement yet is marked *not built*; section 13 lists it.

## 1. Purpose

The owner is a blockchain consensus and security researcher (PhD on blockchain security, client work at a research company). He uses Claude Code for:

- **Client work**: security reviews, protocol design, advisory, scoped by a SoW.
- **Academic work**: new papers, revisions, literature reviews, proofs, protocol design and verification, attack search, open-ended exploration.

The workflow makes Claude Code a research partner with a team of specialist agents, an independent review pipeline (including Codex as a second model), and project memory on disk. Its main job is to keep work faithful to the brief, the contract, the model and his writing style, and then technically correct.

## 2. Principles

1. **Conversation first.** Research is not a pipeline. Most sessions are discussion and brainstorming; tasks emerge from them. The harness supports thinking by default and applies its machinery only to committed work.
2. **State on disk, sessions disposable.** Everything a project knows lives in `.work/`. Long sessions drift and forget rules, so any session must be able to start fresh from the files.
3. **Contract first.** Committed work is checked against a written brief, contract and model. The conformance gate (G1) runs before technical review, because a correct proof of the wrong statement or in the wrong model is the most expensive error.
4. **Blind review.** Reviewers see the artifact, brief, contract, model, glossary, claims and the inputs they point to, never the producer's working reasoning. Earlier rounds, with the producer's responses and rebuttals to each issue and any arbiter rulings, go to the next reviewer on purpose. Exceptions are explicit: the arbiter sees both sides; the counterexample-hunter may read dead ends; the summarizer reads all of `.work/`.
5. **Cheap first, escalate what survives.** Each agent starts at the cheapest tier that can do its task (Haiku, Sonnet or Opus) and climbs its ladder; some ladders end at maximum effort and then the human, not at Mythos. Mythos is used freely where deep reasoning is needed, and not on a first draft that has not survived a cheaper attack, except where the task is known to be hard: main theorems start at `prover-mythos`, hard designs at `protocol-designer-mythos`, refinement stages at `question-refiner-mythos`, and the final proof check of a main theorem runs at `proof-checker-mythos`. The routing table is in the `model-routing` skill.
6. **Questions to the human are about research only.** Content, scope and direction. Anything that needs technical knowledge of the system (tokens, budgets, models, effort, rounds, file formats) is decided by the system and logged.
7. **The human never opens files to operate the workflow.** Questions come as dialogs with decision cards; approvals come with packets. Reading full text of the model and main statements in chat at approval time is encouraged.
8. **Discussion is free, commitment is checked.** Anything that changes the paper, the deliverable or a claim's strength goes through the gates.
9. **Nothing of the workflow in shared history.** Workflow files never appear in a project's git history or in commit messages.

## 3. Modes of use

| Mode | Start | Behavior |
|---|---|---|
| Conversation (default, *not built*) | `claude` in a project | research discussion with project context; quick probes allowed; capture at natural breaks |
| Commitment | say "write it up", "prove it", "restructure", or accept the session's offer (*not built*: today every typed prompt is a commitment, see below) | request flow (`request` skill): record, assess impact, brief, agents, gates, packet |
| Autopilot | `rw` | works through committed threads (*not built*: today the playbook's stages, one stage per session) and deferred requests; restarts sessions itself; asks blocking decisions and checkpoints in session with a notification and continues; at the subscription limit waits for the reset and resumes; stops on project done, an error, a session that ends without a handoff, or a stage or session cap given at start |
| Outside the harness | prefix `raw:` or a folder without `.work/` | plain Claude Code. In a `.work/` project, `raw:` skips the request flow only: the rules card, digest and Stop and PreCompact guards still apply |

Prefixes `quick:` and `full:` override the default gate depth of a commitment.

**What runs today (direct mode).** Every prompt typed in a plain session in a `.work/` project, unless it starts with `raw:` or `/`, is a request handled by the `request` skill. The hooks, the global `CLAUDE.md` and each project's `CLAUDE.md` ("Direct mode" section, installed by `scripts/project_update.py`) say so. The words "quick" and "full review" in a request select the gate depth (section 6). Conversation first (history entry 10) replaces this; it is not built.

**Quick probes** (*not built*): cheap checks during conversation (counterexample attempt, literature check, model-conformance check). Labeled "probe, unverified". They never change claim statuses and are kept only if captured.

**Capture** (*not built*): a multi-select dialog listing ideas, open questions, dead ends, decisions and thread changes from the discussion. Only ticked items are saved, plus a one-page session summary. At exit a stub is written; the dialog is offered at the next session start.

## 4. Project layout

```
<project>/                      (may be a subfolder of a larger repo)
  resources/                    append-only drop folder for inputs; never tracked by the project repo
    BRIEF.md                    owner's intent (client or research template); requests appended under dated headings
  CLAUDE.md, .claude/           project instructions; never tracked by the project repo
  .work/                        its own git repo
    contract.md                 R-IDs (requirements), D-IDs (deliverables), N-IDs (out of scope, from the brief's G1 check rows), P-rows (position), each pointing to BRIEF or SoW lines; approval
    model.md                    assumptions A1, A2, ... with labels
    glossary.md                 terms, macros, notation for this project
    claims.md                   registry: status draft | provisional | checked | verified | refuted | legacy-unverified
    threads.md                  lines of inquiry: exploring | parked | committed | done (not built)
    ideas.md                    ideas and hypotheses with source and status (not built; the open-ended playbook keeps hypotheses.md)
    state.md                    playbook stage, active brief, project branch, revisions at last handoff, next actions,
                                pending decisions, requeued briefs; pointers to threads (not built)
    decisions.md, decisions/D<n>.md   log and decision cards
    deadends.md                 failed approaches with reasons
    approvals.md                decision classes, class table, append-only approval log
    requests.md                 request registry
    resources.manifest          per file in resources/: path, sha256, size, date seen, origin, how it was handled, anomaly, summary
    usage.tsv                   tokens per dispatch, by brief and stage type (PostToolUse hook)
    .rw/                        session-end marker for rw; ignored by the .work repo's own .gitignore
    briefs/ issues/ packets/ handoffs/ retro/
    sessions/                   session summaries (not built)
```

- Excludes go in `.git/info/exclude` (never a committed `.gitignore`, which would reveal the workflow), prefixed with the project's subfolder path when the project is not the repo root. They cover `.work/`, `CLAUDE.md`, `.claude/`, `resources/` and build `output/`.
- Inputs in `resources/` that the project repo already tracks may stay tracked if the owner chooses at intake. `CLAUDE.md`, `.claude/` and `resources/BRIEF.md` must not be tracked: `repos.py check` fails and `rw` refuses to start.
- `resources/` is append-only for the owner. A new file is read and checked against the contract: unrelated files are recorded; files that bear on the contract produce a checkpoint card; files that change scope or are a new SoW produce a blocking card. The scan runs at the start of each orchestrator session. Edits or deletions are anomalies: one warning per new version of a file; edits to `BRIEF.md` also warn once when a request is recorded.
- The workflow itself adds to `resources/`: request entries and addenda in `BRIEF.md`, request attachments in dated folders, producers' literature notes, and refreshed entries after an accepted change.

## 5. Agents

Dispatched only by the orchestrator (main session). Shared rules in the `agent-protocol` skill.

- **Producers**: literature-scout, modeler, property-writer, protocol-designer, theorem-writer, prover, attacker, exposition-writer, report-writer, simulator (only on request), question-refiner.
- **Reviewers**: conformance-reviewer (G1); assumption-auditor, proof-checker, counterexample-hunter, citation-verifier (G2); style-reviewer (G4).
- **Regression-checker**: after edits, lists the claims that depend on changed content and need rechecking. Bookkeeping, no gate; write-restricted like a reviewer.
- **Summarizer**: writes approval packets. No gate; may write only in `.work/packets/`.
- **Arbiter**: settles deadlocks; sees both sides.
- **Mythos variants**: `<base>-mythos.md` for prover, proof-checker, counterexample-hunter, attacker, protocol-designer, question-refiner and arbiter, generated by `scripts/build_mythos_variants.py`. A pre-commit check keeps them in sync once `git config core.hooksPath .githooks` is set in the clone; it checks the working tree, not the index. Needed because the per-call model override accepts only sonnet, opus, haiku, fable.
- **Orchestrator**: the main session. Under `bin/rw` it runs on Opus 5.5 high; in a plain session (direct mode) it runs on the global default model and effort.
- Reviewer writes are restricted to new files in `.work/issues/` whose names carry the reviewer's own prefix. A PreToolUse hook enforces this for file tools. The orchestrator also runs a `git status` check in both repos around every reviewer and arbiter dispatch (the Codex wrapper runs its own): any other change is reverted and the review discarded; a moved HEAD is reported, never reset, and needs a blocking card. A second violation reruns the reviewer one rung up; a third ends the session with `/handoff error`.

## 6. Review pipeline

| Gate | Checks | By |
|---|---|---|
| G0 | compile, lint (em dashes, `\Cref` and unresolved targets, banned words, macros, labels, sentence headings, leftover author notes) | `scripts/lint_tex.py` |
| G1 | brief, contract, scope, model, glossary, claim strength, position and out-of-scope checks | conformance-reviewer |
| G2 | assumption audit, then proof check, then counterexample search; citation check where the brief names it | escalating ladder |
| G3 | independent review | Codex (`gpt-6.1-sol`, high; highest effort for main results and deliverables), read-only sandbox |
| G4 | writing style | style-reviewer |
| G5 | human | per `approvals.md` |

- Gate depth for a commitment: prose or structure only runs G0, G1, G4; statements, proofs, model or findings run G0 to G4, with G3 for main results and deliverables. G0 runs only when a `.tex` file changed. "quick" runs G0 and G1 only and never raises a claim status; "full review" runs G0 to G4 and treats the artifact as critical. Under `/orch`, the playbook stage sets the gates.
- Stopping rules (computed by `scripts/review_status.py`, never by the orchestrator from memory): converged, deadlocked, stalled, round limit. One clean round converges; for main theorems, designs and final deliverables G1, G2 and G4 need two, and at G1 and G2 a clean G3 round at the same content counts as the second. "Same content" hashes the artifact plus model, glossary and the claims it depends on.
- Deadlock: `arbiter`, then `arbiter-mythos` (if needs_human or main theorem; for a main theorem its ruling governs), then the human. A producer who rejects an issue again after a reviewer-right ruling goes to the human.
- `verified` means G1 and G2 (and G3 where required) passed at recorded content. After any edit to LaTeX, pseudocode, the model or the glossary, the regression-checker lists the dependent claims and the orchestrator resets them. A loop that converges while a decision is still provisional leaves its claims `provisional`.

## 7. Decisions and approvals

- **Classes** (full table in `approvals.md`): blocking (asked now: contract and playbook approval, scope and contract changes, a request that changes a deliverable, a new SoW, main theorem statements, milestones and final deliverables, an unresolved deadlock on a main theorem, anything irreversible); checkpoint (recommendation taken provisionally, dependent claims marked `provisional`, confirmed in a batch; also stalled loops, round limits and other deadlocks); logged (routing, retries, budgets, minor fixes).
- **Decision card**: one-sentence question; 2 to 4 options with consequences; recommendation and reason; dependent claim and assumption IDs; evidence pointers. Dialogs show a compressed card (question, options, the recommendation's reason) and must be self-contained (never "as shown above").
- **Checkpoint**: one screen of pending provisional decisions, with "accept all" or individual reversal; reversal re-queues dependent work.
- **Approval packet** (summarizer): what was produced, what changed, review findings and resolutions, what is uncertain, what approval unlocks.
- **Budgets** are automatic per stage type and recalibrated from logged usage each time `rw` starts. Overrun: extend once by 50% if the last round found new issues, otherwise treat as stalled. Only the subscription limit reaches the human, as a notification.

## 8. Hooks

All hooks live in `hooks/rw_hooks.py`. Except the status line, they do nothing outside a project with `.work/` (found through `$CLAUDE_PROJECT_DIR`, so a session must start at the project folder), and fail open on script errors.

- SessionStart: binding files; the project digest (start of `state.md` and the latest handoff); outside `rw`, the direct-mode instructions and open or deferred requests; after compaction, an instruction to hand off and re-read the binding files. Records the baseline that Stop and PreCompact compare against. Pending capture from the previous session: *not built*.
- UserPromptSubmit: rules card every prompt. Outside `rw`, a prompt not starting with `raw:` or `/` is saved and routed to the `request` skill. Full digest on first prompt, after compaction and when memory changed, and relevant ideas and dead ends otherwise: *not built*.
- PreCompact: blocks manual compaction with unrecorded work; never blocks auto-compaction (writes a snapshot instead).
- Stop: blocks only for unrecorded changes to the paper, deliverable or claims. Never for discussion, never for the workflow's own bookkeeping. Under `rw` it also marks the session ended and, on an `/orch` turn, keeps the session from ending while it should ask or wait.
- PreToolUse on file tools and Bash: reviewer write guard, the summarizer's packets-only guard, and a push guard that refuses pushing `.work` or workflow branches.
- PreToolUse on AskUserQuestion: a desktop notification that input is needed.
- PostToolUse on Agent: logs tokens per dispatch to `.work/usage.tsv` and a global log; near the context limit, tells the orchestrator to finish the round and hand off.
- StopFailure on the usage limit: snapshot handoff if work is unrecorded, end marker with the reset time for `rw`, notification.
- Status line (every project): model, context use, current stage; caches the data the PostToolUse and StopFailure hooks need.
- SessionEnd: capture stub (*not built*).

## 9. Writing and domain knowledge

- `academic-writing` skill: mechanics (no hard sentence cap; avoid verbosity, keep rhythm), LaTeX conventions (llncs, `\Cref`, label prefixes, generic macro patterns), paper architecture (FC corpus rules), glossaries. Example slots are placeholders until prompt 02 Stage G fills them from the owner's papers.
- `domain` skill: filled by prompt 02 (corpus inventory, grounded per-paper notes, concept files, evidence-backed taste file, Stage G examples). Client material never enters it.
- Project glossaries override global ones.

## 10. Commits

- No AI attribution, co-author trailers or AI references anywhere. The owner's commit style is in the `commit-style` skill, derived from his own history.
- Project repo commits describe what changed in the project, with no workflow terms, and stage only files under the project's subfolder (never `git add -A`).
- Workflow state is committed in the `.work` repo. Workflow branches are local only.

## 11. Working on this repo

- Stage changes, show the plan, wait for OK on anything non-trivial.
- Show the exact diff and wait for OK before changing `~/.claude/settings.json`; back it up first.
- Run `scripts/run_tests.sh` before committing. Add tests for every behavior change.
- Any change that alters behavior updates this file in the same commit. A design change also gets a new entry in section 12 with the reason. The repo-level instructions (`.claude/CLAUDE.md`) load this file in every session started at the repo root.
- This file never names a client or a client project.
- No em dashes in any file. Commit in the owner's style.
- Nothing from client projects may enter this repo.
- `setup-prompts/` holds the original build prompts; do not modify them.
- `legacy/` holds pre-workflow files kept for migration.

## 12. Design history

Decisions that changed the design, with reasons. Append new entries.

1. Single orchestrator replaced by stateless sessions and `.work/`: long contexts drifted and forgot rules.
2. Project-specific examples removed from global files: examples will come from workspace inspection (prompt 02 Stage G).
3. Sentence-length cap removed: the rule is economy and rhythm, not a word count.
4. Mythos via generated agent files: per-call override cannot select Mythos.
5. Interaction redesign after the first pilot: sessions ended to ask questions, the human had to open files and restart sessions, approvals lacked context. Replaced by in-session dialogs, decision cards, checkpoints, packets and an `rw` loop.
6. Budgets removed from human view: the human cannot and should not reason about tokens.
7. No AI attribution in commits; owner's style.
8. `.work/` as its own repo, excludes via `.git/info/exclude`, `resources/` untracked and append-only with a manifest: workflow must not appear in shared history; resources are inputs, often confidential or non-redistributable.
9. Subfolder projects supported: real projects live inside larger repos.
10. Direct mode (every prompt a request) replaced by conversation first: research is mostly discussion; tasks emerge from it.
11. Design overview wired into the tooling: `.claude/CLAUDE.md` loads this file for sessions in this repo, and the `workflow-guide` skill answers questions about the workflow from it in any project: intent must stay next to the code and be answerable without opening files.

## 13. Status

- Built and tested: agents, gates, Codex wrapper, hooks, lint, review status, interaction redesign, commit style, repo separation, subfolder support, direct mode.
- Not built: conversation-first mode (history entry 10): conversation as default, commitment on request or offer, `quick:` and `full:` prefixes, quick probes, capture, threads, ideas, session summaries, the SessionEnd hook, digest and idea injection on prompts. Direct mode runs in its place.
- Pilot: first run exposed the interaction problems (history entry 5). Rerun of the proof stages (false lemma, forced deadlock) pending; until reviewed, `verified` is not fully trusted and the owner reads results himself.
- First real project migrated (a client project in a subfolder of a larger repo).
- Known open issues at time of writing: `review_status.py` ignoring legacy issues without a status field; `repos.py check` requiring a leading slash on exclude lines; checkpoint dialog not self-contained; template placeholder claim treated as real.
- Not started: prompt 02 (domain knowledge), migration of other projects.
