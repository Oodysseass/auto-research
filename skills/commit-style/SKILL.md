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

Describe what changed in the project. Use the artifact's plain name (from the brief's goal), e.g. "proof of lemma 2", "model".

| Event | Message |
|---|---|
| contract written | `add contract and playbook` |
| brief written | `plan proof of lemma 2` |
| producer output | `add proof of lemma 2`, `add model and model section` |
| producer revision | `revise proof of lemma 2`, `revise model assumptions` |
| review reports and review log | `review proof of lemma 2, round 2` |
| claims registered or statuses changed | `register lemma statements`, `mark lemma 1 verified` |
| decision recorded | `decide adversary chain knowledge` |
| approval recorded | `approve model` |
| handoff | `update project state after proofs` |

Never put a reviewer, gate, tier or tool name in the message. The issue files and `decisions.md` record who did what.
