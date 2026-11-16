# Routing

## Orchestrator

- orchestrator: claude-opus-5-5, effort high

This line is the setting. Change it here to move the orchestrator to another model (e.g. `claude-mythos-5-2, effort xhigh`).
`/orch` (Stage 5) applies it.

## How a tier is selected

A dispatch is the Agent tool call `subagent_type: <agent>`, with optional per-call `model` and `effort`.

- Default tier: the agent file's frontmatter (`model`, `effort`). Pass no override.
- Per-call `model` accepts only `sonnet`, `opus`, `haiku`, `fable`. It selects the latest model of that family.
- Per-call `effort` accepts `low`, `medium`, `high`, `xhigh`, `max`. This file is the instruction that authorizes setting it.
- Mythos 5.2 is selected only by dispatching a generated `<base>-mythos` agent (`model: claude-mythos-5-2`, `effort: xhigh` in its file).
  Never pass a per-call `model` to a `-mythos` agent: that replaces Mythos with the named family.
- Whenever you pass a per-call `model`, also pass `effort`, so the log records the exact tier.
- A tier change never changes the role name. Issue IDs, file names and `reviewer` stay `<base>`.
- `fable` is not used by default. Use it only when a brief says so.

## Tiers

| Tier | Selected by | Use for |
|---|---|---|
| T0 | a script, or `regression-checker` (Haiku 5.5, low) | lint (G0), regression scans, formatting, file bookkeeping |
| T1 | Sonnet 5.5 agents at default tier | literature notes, exposition drafts, style review, first-pass attacks, citation checks |
| T2 | Opus 5.5 agents at default tier, or a Sonnet agent with `model: opus, effort: high` | model, properties, statements, lemma proofs, conformance, assumption audit |
| T3 | `<base>-mythos` agents (Mythos 5.2, xhigh) | see "When to use T3" |

## When to use T3

- Proofs of main theorems: `prover-mythos`.
- Final proof check of headline results: `proof-checker-mythos`.
- Attack search on a design or statement that survived T2 attacks: `attacker-mythos`, `counterexample-hunter-mythos`.
- Hard protocol design: `protocol-designer-mythos`.
- Research-question refinement after a literature review: no Mythos agent exists yet. Open decision, see the end of this file.
- Resolving a deadlock before it reaches the human: rerun the deadlocked role at T3 when a `-mythos` variant exists
  (the reviewer, the producer, or both). If no variant exists for either side, escalate to the human.

"Main theorem" and "headline result" mean a claim the contract or the brief marks as main. The orchestrator marks it in the brief.

## Escalation rule

A claim moves up one rung when it survives the current rung's attack or check (accept with no blocking or major issue).
Do not spend T3 on a first draft that has not survived a T1 or T2 attack, unless the task is known to be hard:
a main theorem, or a design question the brief marks as hard.
A rung that finds a blocking issue does not move the claim up. The producer revises, and the same rung reviews again.

## Ladders per agent

Each arrow is one rung. "human" means stop and escalate per `approvals.md`.

### Producers

| Agent | Default | Ladder |
|---|---|---|
| literature-scout | Sonnet, medium | `literature-scout` -> `literature-scout` with `model: opus, effort: high` |
| modeler | Opus, high | `modeler` -> `modeler` with `effort: max` -> human |
| property-writer | Opus, high | `property-writer` -> `property-writer` with `effort: max` -> human |
| theorem-writer | Opus, high | `theorem-writer` -> `theorem-writer` with `effort: max` -> human |
| protocol-designer | Opus, high | `protocol-designer` -> `protocol-designer-mythos`. Hard design: start at `protocol-designer-mythos` |
| prover | Opus, high | Lemma: `prover` -> `prover-mythos`. Main theorem: start at `prover-mythos` |
| attacker | Sonnet, high | `attacker` -> `attacker` with `model: opus, effort: high` -> `attacker-mythos` |
| exposition-writer | Sonnet, high | `exposition-writer` -> `exposition-writer` with `model: opus, effort: high` |
| report-writer | Sonnet, high | `report-writer` -> `report-writer` with `model: opus, effort: high` |
| simulator | Sonnet, medium | `simulator` -> `simulator` with `model: opus, effort: high` |

A producer moves up a rung when its output fails the same gate in two consecutive rounds on the same canonical issue,
or when the brief marks the task as hard. `prover` moves to `prover-mythos` when a lemma proof fails G2 twice.

### Verifiers

| Agent | Gate | Default | Ladder |
|---|---|---|---|
| conformance-reviewer | G1 | Opus, medium | `conformance-reviewer` -> `conformance-reviewer` with `effort: high` |
| assumption-auditor | G2 | Opus, high | `assumption-auditor` -> `assumption-auditor` with `effort: max` |
| proof-checker | G2 | Opus, high | `proof-checker` -> `proof-checker-mythos`. Main theorem: final check always at `proof-checker-mythos` |
| counterexample-hunter | G2 | Sonnet, high | `counterexample-hunter` -> `counterexample-hunter` with `model: opus, effort: high` -> `counterexample-hunter-mythos` |
| citation-verifier | G2 | Sonnet, medium | `citation-verifier` -> `citation-verifier` with `model: opus, effort: medium` |
| style-reviewer | G4 | Sonnet, medium | `style-reviewer`. No escalation; disputes go to the human |
| regression-checker | none | Haiku, low | `regression-checker` -> `regression-checker` with `model: sonnet, effort: medium` |
| Codex | G3 | see codex-review skill | `codex_review.sh` with the default model -> `--effort` one level higher |

`counterexample-hunter` climbs on survival: after an accept with an empty `issues` list at one rung, the next round runs one rung up,
until the top rung that the claim's importance warrants (lemma: Opus rung; main theorem or design: Mythos rung).
`regression-checker` moves up only if its output is inconsistent with `claims.md` dependencies.

## Budget

- Every brief has a budget: max review rounds (at most 5, per the review-gates skill) and a rough token size.
- Defaults when the brief does not say: T1 task 100k tokens, T2 task 300k, T3 task 800k; 5 rounds.
- The orchestrator updates "Budget used" in `state.md` after each dispatch, from the token count the Agent tool reports.
- Overrun of rounds or tokens: stop, set the brief status to `escalated`, and escalate to the human. Do not start another round.
- A T3 dispatch needs no approval. It is logged like every routing choice.

## Logging

Every dispatch whose tier differs from the agent file default, and every T3 dispatch, gets a `decisions.md` entry:

```
## <YYYY-MM-DD> | route <claim or brief> to <agent> (<rung>)
- made by: orchestrator
- reason: <one line, e.g. "survived counterexample-hunter at Opus rung, r3">
- routing: <agent>, <model ID>, <effort>
```

Default-tier dispatches are recorded in the brief header (`assigned agent`, `model`, `effort`) only.

## Open decision

No Mythos-tier agent covers research-question refinement after a literature review. Until one is added,
the orchestrator drafts the refined question and stops for human approval.
