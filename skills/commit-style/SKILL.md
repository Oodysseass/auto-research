---
name: commit-style
description: The human's git commit message style. Load before writing any commit message, in any repo, including workflow commits made by /orch, /handoff, /intake, /gate, /escalate, /retro and the codex-review skill.
---

# Commit style

Derived from 265 of the human's own commits (before 2026-09-15, no trailer). Applies to every commit in every repo.

## Rules

1. Subject line only. No body, unless the change cannot be described without one (rare).
2. Lowercase first word. No trailing period.
3. Bare imperative verb first: `add`, `update`, `fix`, `re-write`, `remove`, `move`, `refine`, `clarify`, `revise`, `state`, `prove`.
4. No prefixes or scopes: no `feat:`, no `S4:`, no `handoff:`.
5. Short: aim for 30 to 50 characters. Several changes go in one comma-separated list, not in a body.
6. Name the content that changed (section, lemma, proof, model, algorithm), not the tool, agent, reviewer or model that changed it.
7. Unfinished work may end with `, wip` or start with `[wip]`.
8. Never: a `Co-Authored-By` or any other trailer; the words Claude, AI, agent, generated, assistant, model names
   (Opus, Sonnet, Mythos, Codex) or reviewer role names; "Generated with" lines in PR text.

## Examples (real)

- `refine write up and safety proof, add liveness proof`
- `add a liveness attack, complete a proof and add comment`
- `add linebreaks, fix off-by-1 in proof of theorem C.3, fix typo in algorithm 2`
- `update structure to include paper subfolder, update analysis (without liveness)`
- `re-write impossibilities section`

## Research workflow commits

A workflow project has two repos (`~/dotclaude/scripts/repos.py`). Each commit goes to the repo that holds the files it changes.

- Project repo (the paper and code, shared with coauthors): only content changes, on the human's current branch. The message
  reads like the human's own commits and names no workflow terms: never brief, review, round, gate, playbook, a stage ID (`S4`),
  handoff, approve or approval, provisional, workflow, orchestrator, `.work`, the workflow's contract or decision cards, nor any
  agent, reviewer, model or tool. (A smart contract or a lemma's claim in the paper is content, not a workflow term.)
  Never commit `.work/`, `CLAUDE.md`, `.claude/`, `resources/` or `output/` there; `.git/info/exclude` keeps them out.
  Commit there only with `python3 ~/dotclaude/scripts/repos.py commit -m "<message>" [paths]`, which stages files under the
  project directory only. Never `git add -A` or `git commit -a`: the repo may hold coauthors' folders or sibling projects.
- `.work` repo (local only, never pushed): workflow state. The table below.
- Workflow branches (`work/*`, `workflow-migration`) are local only and never pushed. Prefer the current branch; create one only when
  the work must stay apart from it.

| Event | Repo | Message |
|---|---|---|
| producer output in the paper or code | project | `add proof of lemma 2`, `add model section` |
| producer revision in the paper or code | project | `revise proof of lemma 2`, `fix off-by-1 in lemma 2` |
| contract written | .work | `add contract and playbook` |
| brief written | .work | `plan proof of lemma 2` |
| producer output in `.work/` (model, glossary, notes) | .work | `add model`, `revise model assumptions` |
| review reports and review log | .work | `review proof of lemma 2, round 2` |
| claims registered or statuses changed | .work | `register lemma statements`, `mark lemma 1 verified` |
| decision recorded | .work | `decide adversary chain knowledge` |
| approval recorded | .work | `approve model` |
| new inputs recorded | .work | `record new inputs` |
| handoff | .work | `update project state after proofs` |

Use the artifact's plain name (from the brief's goal), e.g. "proof of lemma 2", "model".
Never put a reviewer, gate, tier or tool name in any message. The issue files and `decisions.md` record who did what.
