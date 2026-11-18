# Task: Migrate this existing project into my research workflow, without losing information

## Context

My global Claude Code setup in `~/dotclaude` (symlinked into `~/.claude`) defines a research workflow: a project keeps its state in `.work/` (contract, model, glossary, claims registry, state, decisions, deadends, approvals, briefs, issues, handoffs), using the templates in `~/.claude/templates/project/`. Read those templates, the `intake` skill, the `review-gates` skill and the `domain` skill index before you start.

A project has two git repos. The project repo holds the paper and code and is shared with coauthors. `.work/` is its own, local
git repo. Workflow files never appear in the project repo's history: its `.git/info/exclude` (never a committed `.gitignore`,
which would reveal the workflow) keeps out `.work/`, `CLAUDE.md`, `.claude/`, `resources/` and `output/`.
`~/dotclaude/scripts/repos.py` sets this up and checks it. `resources/` is an append-only drop folder for inputs, listed in
`.work/resources.manifest` (`~/dotclaude/scripts/resources.py`).

This project already exists and has history. Your job is to build its `.work/` from what is already here, **without modifying or losing anything that exists.**

## Safety rules

1. Before anything else: check that the project root is a git repo. If it is not, stop and ask me. Note the current branch.
   Do not create a branch: the migration writes only excluded files, so the project repo gets no commit from it, except an
   untracking commit I approve (step 4 below). If a workflow branch (`work/*`, `workflow-migration`) exists or is ever needed, it is
   local only: never push it.
2. Make a tarball backup of the project dir to `../<project>.pre-migration-<date>.tar.gz`.
3. Back up this project's Claude Code state that lives outside the repo (its entry under `~/.claude/projects/`, including any memory or notes files) into `.work/legacy/claude-state/`.
4. **Do not edit, move or delete any existing file.** The only allowed writes are: new files under `.work/`, the project `CLAUDE.md`,
   and the lines `repos.py init` adds to `.git/info/exclude`. If a `CLAUDE.md` already exists, copy it verbatim to `.work/legacy/CLAUDE.md` first, then write the new one so that every project-specific rule from the old file is preserved (quote them; do not paraphrase rules).
5. Same for any local `writing_style.md` or other instruction files: copy to `.work/legacy/`, diff against the global academic-writing skill, and put only the project-specific differences into `.work/glossary.md` or the project `CLAUDE.md`. Show me the diff.
6. Never mark anything `verified`. Every extracted claim gets status `legacy-unverified`.
7. Every extracted item carries a source pointer (`file:line`, or commit hash, or note filename). If you cannot point to a source, it does not go in; it goes in the questions file.

## Stage 0: Two repos

1. Run `python3 ~/dotclaude/scripts/repos.py init`. It makes `.work/` its own git repo and adds the exclude lines. It never untracks
   anything; it lists what the project repo already tracks under `.work/`, `CLAUDE.md`, `.claude/`, `resources/` and `output/`.
2. Already-tracked files, per project. Never untrack anything automatically. Ask me, with the list:
   - `resources/` files: keep them tracked, or untrack them with `git rm -r --cached resources`.
   - `CLAUDE.md`, `.claude/`: the same question. If `CLAUDE.md` stays tracked, the workflow's project instructions go to
     `.claude/CLAUDE.md` (if `.claude/` is untracked), and the tracked `CLAUDE.md` is left exactly as it is.
   For an untracking option, show me the exact commit message first (my `commit-style`, no workflow terms, e.g.
   `stop tracking resources folder`) and say that coauthors who pull it lose those files from their working tree. Commit only
   after my answer, on the current branch.
3. A project already in the one-repo layout (`.work/` tracked by the project repo, from an earlier migration or intake):
   list the commits that touch `.work/` and the branches that hold them (`git log --all --oneline -- .work`), and whether any
   of them is on a remote (`git branch -r --contains <commit>`). Ask me before anything changes. The default plan to propose:
   copy the current `.work/` into the new `.work` repo as one commit ("import project state"), then untrack `.work/` in the project
   repo with `git rm -r --cached .work` (message shown first). Old commits stay where they are. Never rewrite or force-push history
   without my explicit answer; if workflow commits were pushed, tell me which ones and leave the remedy to me.
4. `python3 ~/dotclaude/scripts/repos.py check` must print `workflow files tracked by the project repo: none` before Stage 1.

## Stage 1: Inventory

Produce `.work/legacy/inventory.md`: every file in the project grouped by kind (LaTeX sources, macros, bib, figures, algorithms, notes, `resources/`, code, reviews received, submission files, old instruction files), plus a summary of the git log (date range, main phases, branches, coauthors from commit authors). Read `resources/` fully. Stop and show me.

## Stage 2: Extraction

Write drafts of each `.work/` file, each marked at the top `EXTRACTED: needs human review`:

- `contract.md`: project type and playbook (classify with the intake skill), research question or SoW, venue or client, deliverables and deadlines, from notes, README, submission files, `resources/`, commit messages. Unknown fields are left empty and listed in questions.
- `model.md`: from the model section of the paper. One A-ID per assumption, with its LaTeX label or `file:line`.
- `glossary.md`: from `macros.tex` (every macro and what it expands to), terminology tables in old instruction files, and terms defined in the paper. If `~/dotclaude/legacy/` contains a glossary or examples that belong to this project (for podovery: the old macro list, terminology table and reference excerpts), use them too. Project macros that `skills/academic-writing/latex.md` lists as global patterns are not repeated in the project glossary.
- `claims.md`: one entry per `definition`, `lemma`, `theorem`, `corollary`, `assumption`, `remark` environment, with its label, status `legacy-unverified`, assumptions used (extracted from the proof text where it cites them, otherwise empty and flagged), and `depends on` from the `\Cref` references inside its proof.
- `decisions.md`: decisions found in notes, commit messages, comments, old instruction files, each attributed `human` with source pointer.
- `deadends.md`: abandoned approaches found in notes, commented-out LaTeX, deleted sections in git history (with commit hash).
- `state.md`: where the project stands, based on the latest commits and notes, and which playbook stage that corresponds to.
- `issues/legacy-open.json`: open items from `\todo{}`, author-note macros (`\odysseas{}`, `\giorgos{}`, ...), TODO comments, and unanswered reviewer comments, as issues with severity `major` unless clearly minor.
- `approvals.md`: copy the default template.
- `resources.manifest`: `python3 ~/dotclaude/scripts/resources.py init`, after you have read `resources/` in full. From then on
  `resources/` is append-only: `/orch` reports new files at session start and warns once about edited or deleted ones.
- `.work/migration-questions.md`: everything you could not determine, as short questions. Prefer asking to guessing.

Use subagents for large papers (one per section file), routed per the model-routing skill: Sonnet 5.5 for extraction, Opus 5.5 high for the model and claims dependency graph.

Stop. Show me a summary: counts per file, the questions, and anything surprising (claims without proofs, assumptions used but never stated, labels referenced but missing).

## Stage 3: Human review

Walk me through the questions and the `EXTRACTED` files one at a time. Apply my answers. Remove the `EXTRACTED` marker from each file only after I approve it.

## Stage 4: Baseline review (optional, ask me first)

Offer a baseline run, with a cost estimate per option:

- G0 lint only (no model cost).
- G0 + G1 conformance of the whole paper against the approved contract and model.
- Plus assumption audit of the main theorems (Opus 5.5 high).
- Plus full proof check of the main theorems (Mythos 5.2 xhigh) and Codex review.

Findings go to `.work/issues/`. Nothing in the paper is changed in this stage.

## Stage 5: Finish

Write the first handoff. Commit `.work/` in the `.work` repo (`git -C .work add -A && git -C .work commit`), in my `commit-style`.
There is nothing to merge: the project repo has no workflow commit. Then `rw` and `/wstatus` work in this project. Run `/wstatus`
to confirm; its repos line must say both repos are clean and no workflow file is tracked by the project repo.

## Constraints

- No edits to existing files. No deletions. No em dashes in anything you write.
- Never push the `.work` repo or a workflow branch. Never write workflow terms in a project repo commit message.
- If the project is under anonymous submission, do not add author names to any new file that could end up in a submission artifact.
