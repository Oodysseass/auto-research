# Task: Build my global Claude Code research workflow

## Who I am and what this is for

I am a blockchain and distributed systems researcher (consensus, proof-of-work, security proofs). I use Claude Code for two kinds of work:

- **Client work** for Common Prefix: security reviews, protocol design, advisory. Usually scoped by a SoW with scope, milestones and deliverables.
- **Academic research**: new papers, revisions of existing papers, literature reviews, proofs, protocol design, protocol verification, attack search against properties, open-ended exploration.

You will build a global setup in this repo (`~/dotclaude`, symlinked into `~/.claude`) that turns Claude Code into a multi-agent workflow with:

1. An intake step that classifies a project and picks a playbook.
2. Specialist producer agents and specialist verifier agents.
3. A review pipeline whose main job is to make sure every output **respects the brief, the contract or SoW, the scope, the model and the writing style**, and then that it is technically correct.
4. Codex (OpenAI Codex CLI, signed in with my ChatGPT workspace subscription) as an independent cross-model reviewer.
5. Model and effort routing that saves tokens: cheap models first, Mythos 5.2 for hard reasoning.
6. State on disk, so orchestrators and subagents are disposable and easy to restart. Long-lived orchestrators drift and forget rules; this design must not depend on them.

## How to work

- Work in the stages below. After each stage, show me what you built (file tree + key excerpts) and stop. Wait for my OK before the next stage.
- **Before writing anything that depends on Claude Code or Codex features, verify the feature against the current docs and `--help` output. Do not rely on memory.** Specifically confirm:
  - subagent file format in `~/.claude/agents/` and the accepted frontmatter fields, in particular the exact accepted values of `model` (my `/model` menu shows: Opus 5.5, Fable 5.2, Sonnet 5.5, Haiku 5.5, Mythos 5.2; find the alias or ID that selects each one) and whether an `effort` field exists. If effort cannot be set in frontmatter, find how the orchestrator sets it when spawning a subagent.
  - whether subagents can spawn subagents (design so that only the main session dispatches if they cannot).
  - skills format (`~/.claude/skills/<name>/SKILL.md`, frontmatter, supporting files).
  - slash commands format.
  - hooks: event names (SessionStart, UserPromptSubmit, PreCompact, Stop, SubagentStop, ...), how they receive input, and how they inject context or block.
  - `codex exec` flags: model selection, read-only sandbox, output schema or last-message file, JSON output.
- Use subscriptions only. Hooks and scripts must never set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`; the Codex wrapper unsets `OPENAI_API_KEY` in its subprocess.
- Keep files short. Every file that is always loaded (global `CLAUDE.md`, the rules card) has a hard length budget given below. Everything else loads on demand through skills and agent files.
- Write no em dashes in any file you create.

---

## Stage 1: Repo, backup and consolidation of my existing style files

1. Back up the current `~/.claude` to `~/.claude.backup-<date>.tar.gz`. Never delete the backup.
2. Create `~/dotclaude` as a git repo. Plan the symlinks into `~/.claude` (CLAUDE.md, agents/, skills/, commands/, hooks/, settings). Show me the plan before switching any symlink. Keep any existing Claude Code state that is not configuration (project memory, history, credentials) untouched.
3. Locate my existing files: `~/.claude/CLAUDE.md`, `~/.claude/writing_style.md`, and `fc_writing_style.md` (search for it; ask me if not found).
4. Consolidate them as follows. **Preserve every rule and every quote. Move content, do not rewrite it**, except where noted.

| Source content | Destination |
|---|---|
| CLAUDE.md: identity, `resources/` rule, general rules | global `CLAUDE.md` (rewrite to max ~50 lines, pointers to skills) |
| writing_style.md: core principles, modeling and notation, economy and rhythm, titles, mechanics, sentence patterns, what to avoid, checklist | `skills/academic-writing/mechanics.md` |
| writing_style.md: LaTeX conventions (llncs, splncs04, structure, `\Cref`, labels, theorem envs, algorithms, build command) | `skills/academic-writing/latex.md` |
| writing_style.md: podovery macro list (`\tx`, `\pk`, `\nonce`, ...) and the terminology table (finalized, certificate, quorum, solver, CLOB, ...) | **Not global.** Move into `templates/project/glossary.podovery.md` as an example, and mark it as belonging to podovery. Migration (prompt 03) will place it in that project. |
| fc_writing_style.md sections 1 to 11, 13, 14, 15 | `skills/academic-writing/paper-architecture.md` |
| fc_writing_style.md section 12 (backbone vocabulary) | `skills/academic-writing/glossaries/backbone.md` |
| Precedence rule (mechanics beats architecture where they conflict) | top of `skills/academic-writing/SKILL.md` |

`skills/academic-writing/SKILL.md` says when to load which file: mechanics for any prose; latex for any `.tex`; paper-architecture for model sections, definitions, theorems, proofs, attacks, remarks; backbone glossary for PoW or longest-chain projects; the project's own `.work/glossary.md` always wins over global glossaries on terminology.

5. Write `rules-card.md` (max 15 lines): the rules that drift most when context grows. Include at least: no em dashes; `\Cref` only; use project macros and glossary terms, never synonyms; headings are noun phrases; never state a claim stronger than its status in `.work/claims.md`; stay inside `.work/contract.md` scope; write results to files, not only to chat; read the brief before producing; ask instead of inventing context.

---

## Stage 2: Project templates (`templates/project/`)

These are scaffolded into a project's `.work/` by `/intake` and by migration. Define exact formats.

- `contract.md`: project type, playbook, research question or SoW summary, requirements matrix (IDs R1, R2, ... each with source pointer to SoW or my instruction), in scope, out of scope, deliverables with milestone and due date, venue or client format, `ai_tools_allowed` (default: `claude, codex`), approvals section (see below).
- `model.md`: parties, timing and network, adversary (power and limits), oracle or setup, protocol pointer, notation paragraph. Every assumption has an ID (A1, A2, ...), a one-line statement and a pointer to its LaTeX label if one exists.
- `glossary.md`: terms with fixed meaning, macros with their meaning, notation conventions (indexing, prefix relation, length vs height).
- `claims.md`: registry. One entry per definition, lemma, theorem, corollary, assumption-dependent remark, finding. Fields: ID, LaTeX label, type, statement (or pointer), status (`draft` | `checked` | `verified` | `refuted` | `legacy-unverified`), assumptions used (A-IDs), depends on (claim IDs), verified by (gates, reviewer, model, commit hash), notes. Rule: editing a claim or any claim it depends on resets `verified` to `checked`.
- `state.md`: current playbook stage, active brief, next actions, open approvals, active git branch, budget used.
- `decisions.md`: append-only. Each entry: date, decision, made by (`human` | agent name), reason, model and effort used if it was a routing decision.
- `deadends.md`: append-only. Failed attacks, refuted approaches, abandoned designs, with one line on why.
- `approvals.md`: which events need my approval. **Default (I approve manually for now):** contract and playbook; `model.md`; property and theorem statements before proving starts; each milestone or final deliverable; any change to the contract or model after approval; deadlocks; deleting or overwriting existing files. Mythos escalations do not need approval but are logged in `decisions.md`. I will loosen this file later per project.
- `briefs/<id>.md`: task brief. Fields: goal, inputs (files), output (files and format), acceptance criteria (each traced to R-IDs or claim IDs), constraints (model assumptions in force, style), budget, assigned agent, model and effort.
- `issues/`: one JSON per review, schema `{gate, reviewer, model, artifact, commit, issues:[{id, severity: blocking|major|minor, location, claim, evidence, suggested_fix}], verdict: accept|revise}`. Issue IDs stable across rounds. Producer responses: `{issue_id, status: fixed|rejected|needs_human, justification}`.
- `handoffs/<timestamp>.md`: what was done, what changed (files, commits), open issues, next step, anything the next orchestrator must not forget.
- `CLAUDE.md` (project): type, playbook, pointers to `.work/` files and `resources/`, project-specific rules. Max ~40 lines.

---

## Stage 3: Agents (`agents/`)

One file per agent. Each file states: role, when to use it, inputs it must read, files it may write, output format, and what it must never do. Default model and effort are listed; the routing skill may override them.

**Shared rules for all agents:** read the brief first; read `.work/contract.md`, `.work/model.md`, `.work/glossary.md`; load the academic-writing skill when producing prose or LaTeX; load the relevant domain skill files (built by prompt 02); never claim a result is proven unless its status says so; write outputs to files named in the brief.

**Producers**

| Agent | Role | Default |
|---|---|---|
| literature-scout | finds and summarizes papers; per-paper notes with verbatim quotes and section pointers | Sonnet 5.5, medium |
| modeler | writes or edits `model.md` and the model section; assumptions with IDs | Opus 5.5, high |
| property-writer | definitions and security properties as parametrised predicates | Opus 5.5, high |
| protocol-designer | protocol design and pseudocode | Opus 5.5, high; Mythos 5.2 for hard designs |
| theorem-writer | theorem and lemma statements, proof roadmap, typical-execution structure | Opus 5.5, high |
| prover | proofs, pen-and-paper style in LaTeX | Opus 5.5 high for lemmas; Mythos 5.2 xhigh for main theorems |
| attacker | constructs attacks against a design or a claimed property, as named strategies with numbered steps | Sonnet 5.5 first, escalating |
| exposition-writer | introduction, intuition paragraphs, remarks, contributions, abstract | Sonnet 5.5, high |
| report-writer | client reports and findings in the client format | Sonnet 5.5, high |
| simulator | optional Python simulation to sanity-check a numeric bound. Only when a brief asks for it. | Sonnet 5.5, medium |

**Verifiers** (blind: they get the artifact, the brief, the contract, the model and the glossary; never the producer's reasoning or conversation)

| Agent | Checks | Default |
|---|---|---|
| conformance-reviewer | output matches brief and acceptance criteria; every SoW requirement in scope is covered and nothing out of scope is added; uses the project model, notation, glossary and macros; no claim stronger than its registry status | Opus 5.5, medium |
| assumption-auditor | every proof step uses only listed assumptions (A-IDs) and listed claims; flags silent model drift, e.g. a synchronous step in a partially synchronous model | Opus 5.5, high |
| proof-checker | line by line: each step justified by a named source; cases labelled and closed; boundary cases (genesis, empty range, first round); quantifiers; round arithmetic | Opus 5.5 high; Mythos 5.2 xhigh for main theorems |
| counterexample-hunter | builds explicit adversary strategies or counterexample executions against statements and designs | Sonnet 5.5 → Opus 5.5 → Mythos 5.2 (escalation ladder) |
| citation-verifier | each citation supports the claim attached to it, checked against sources in `resources/`; flags citations it cannot check | Sonnet 5.5, medium |
| style-reviewer | full academic-writing skill compliance | Sonnet 5.5, medium |
| regression-checker | after edits, lists claims in `claims.md` that depend on changed content and need rechecking | Haiku 5.5, low |

Every verifier returns the issue JSON from Stage 2. Severity is required.

---

## Stage 4: Skills (`skills/`)

1. **academic-writing** (from Stage 1).
2. **intake**: classification procedure and `playbooks/*.md`. Intake reads `resources/` fully first (my existing rule: if `resources/` is missing, say so and ask). It classifies the project, asks me what it cannot determine, writes the contract and approvals, picks a playbook, and stops for my approval. Playbooks, each a list of stages with the brief template and gates per stage:
   - `client-security-review`: SoW matrix → threat model → property list → attack search per property → findings (severity, argument or PoC) → report → conformance vs SoW.
   - `client-design`: SoW matrix → requirements → design → property arguments or proofs → attack pass → report.
   - `new-paper`: question → literature review → refine question → model → properties → design → theorem statements → proofs → attacks and tightness → exposition → full review.
   - `paper-revision`: ingest paper → claims and assumptions registry → targeted changes → regression review.
   - `literature-review`: search → per-paper notes → citation verification → synthesis → question refinement.
   - `proof-verification`: ingest statements → assumption audit → step-by-step check → counterexample search → verdict per claim.
   - `open-ended`: hypothesis log → time-boxed exploration rounds → each round ends in promote (new contract, needs my approval), park, or kill (logged in `deadends.md`).
3. **review-gates**: gate definitions, stopping rules, issue schema.
   - G0 mechanical: the lint script from Stage 6. No model.
   - G1 conformance: conformance-reviewer. **Runs before technical review**, so a correct proof of the wrong statement or in the wrong model is caught early.
   - G2 technical: assumption-auditor → proof-checker → counterexample-hunter, with escalation.
   - G3 cross-model: Codex, for main theorems, designs and every final deliverable.
   - G4 style: style-reviewer.
   - G5 human: per `approvals.md`.
   - Stopping rules for a review loop: zero blocking or major issues for 2 consecutive rounds → converged; max 5 rounds; same issue rejected twice by the producer → deadlock, escalate to me; no diff or repeated content hash → stalled, escalate to me.
   - Producer may rebut issues with arguments; rebuttals go to the next review round.
   - A claim becomes `verified` only after G1, G2 (and G3 where required) pass at a specific commit. Record gates, reviewers, models and commit in `claims.md`.
4. **model-routing**: `routing.md` with the table below, the escalation ladder, and budget rules. The orchestrator itself runs on Opus 5.5 high (one line to change). Mythos 5.2 is available and should be used wherever deep reasoning is required.
   - Haiku 5.5 or a script: lint, regression scans, formatting, file bookkeeping.
   - Sonnet 5.5: literature notes, exposition drafts, style review, first-pass attacks, citation checks.
   - Opus 5.5 high: model, properties, statements, lemma proofs, conformance, assumption audit.
   - Mythos 5.2 xhigh: proofs of main theorems; final proof-check of headline results; attack search on designs or statements that survived Opus-level attacks; hard protocol design; research-question refinement after a literature review; resolving deadlocks before they reach me.
   - Escalation: a claim moves up one tier when it survives the current tier's attack. Do not spend Mythos on a first draft that has not survived a cheap attack, unless the task is known to be hard (main theorem, deep design question).
   - Each brief has a budget (rounds and rough token size). Overrun → stop and escalate to me.
   - Every routing choice is logged in `decisions.md` with a one-line reason.
5. **codex-review**: `SKILL.md` + `codex_review.sh`. Runs `codex exec` in the project dir with a read-only sandbox, a configurable model, the reviewer prompt template, and the issue JSON schema. Validates the JSON, re-asks once on invalid output, writes to `.work/issues/`. Afterwards checks `git status` and aborts loudly if Codex changed any file. Refuses to run if `codex` is not in `ai_tools_allowed` in the contract (default allows it).
6. **domain**: empty skeleton with `SKILL.md` and an index file. Prompt 02 fills it.

---

## Stage 5: Commands and hooks

**Commands (`commands/`):**

- `/intake`: run the intake skill in the current project; scaffold `.work/` from templates.
- `/orch`: start a fresh orchestrator: read `state.md`, latest handoff, contract, approvals, open issues; pick the next stage of the playbook; write a brief; dispatch producers; run gates; update `claims.md`, `state.md`, `decisions.md`; finish with `/handoff`. **One playbook stage per session.** When it finishes a stage, it tells me to start a new session.
- `/handoff`: write `handoffs/<timestamp>.md`, update `state.md`, commit.
- `/gate <artifact>`: run gates on an artifact on demand.
- `/status` (built as `/wstatus`: a skill named `status` would replace the built-in `/status`): stage, open issues by severity, claims by status, pending approvals, budget.
- `/escalate <claim-or-issue>`: rerun a review one tier up.
- `/retro`: after a milestone, propose additions to the domain skill, the playbooks or the rules card, based on issues found and deadends. Proposals only; I approve each.

**Hooks (`hooks/`):**

- SessionStart: if `.work/` exists, inject `state.md` and the latest handoff (short).
- UserPromptSubmit: inject `rules-card.md`.
- PreCompact: force a handoff before compaction.
- Stop: if the session produced commits or edited `.work/` files but did not update `state.md`, block and ask for `/handoff`.

Wire hooks in `settings.json`. Test each hook with a dry run and show me the output.

---

## Stage 6: G0 lint script

`scripts/lint_tex.py` (Python, no dependencies beyond stdlib):

- em dashes (`—`, `---` in text mode)
- `\ref{` or `\eqref{` instead of `\Cref{`
- banned words: clearly, obviously, it is easy to see, straightforward, trivially, intuitively, the key insight
- `\paragraph{}` and `\section{}` titles that look like sentences (contain a finite verb from a small list, end with punctuation, or exceed 6 words) as warnings
- raw words where a macro exists, using the macro list from the project's `glossary.md`
- labels without the allowed prefixes (`def. lem. cor. thm. asm. rem. alg. sec. fig. line.`)
- unresolved `\Cref` targets (parse labels across files)
- author notes left (`\odysseas{`, `\todo{`, other note macros from glossary) as warnings
- runs `latexmk -synctex=1 -pdf -outdir=output main.tex` if `--build` is passed

Output: the issue JSON format with gate `G0`. Write pytest tests with small fixture `.tex` files.

**Added in Stage 5: convergence script.** `scripts/review_status.py` (stdlib only), built in this stage with pytest tests.
Usage: `review_status.py .work/issues <artifact-slug>`. It reads every report, response and ruling for the artifact and prints one of
`converged | deadlocked | stalled | max_rounds | open` per gate, applying the review-gates "Stopping rules" exactly, in their order:
including the two-round rule for critical artifacts (main theorems, designs, final deliverables), where a clean G3 round at the same commit
counts as the second clean round of G1 and G2; duplicates (`duplicate_of`); arbiter rulings; artifact hashes from the brief's Review log for
stalls; the brief's round budget. The orchestrator (`/orch`), `/handoff` and `/wstatus` call it instead of applying the rules from memory.
Tests: one fixture directory per outcome, plus the G3-as-second-round case, an edit between the two clean rounds, and a duplicate-only issue.

---

## Stage 7: Pilot

Create a throwaway project `~/dotclaude/pilot/` with a tiny `resources/` (a two-paragraph problem statement for a toy longest-chain lemma). Run `/intake`, then two `/orch` sessions, end to end, including one Codex review. Show me the resulting `.work/` folder, the issue files, and the decisions log. List anything that did not work as designed and fix it before finishing.

## Constraints

- Never delete or overwrite my existing files outside `~/dotclaude` without showing me the change first.
- No em dashes in anything you write.
- Keep always-loaded files within their length budgets.
- Commit after each stage with a descriptive message.
