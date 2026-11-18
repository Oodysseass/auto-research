# Routing

## Where tiers are set

Default tiers for Claude are set in two places. Per-call overrides (below) change a tier for one dispatch only.

- Orchestrator: the `RW_MODEL=... RW_EFFORT=...` line in `~/dotclaude/bin/rw` (default `claude-opus-5-5`, `high`).
  `rw` starts `claude --model "$RW_MODEL" --effort "$RW_EFFORT" /orch`. A session started with plain `claude` runs on the global default instead.
- Agents: the `model` and `effort` frontmatter of each base file in `~/dotclaude/agents/`.
  The `-mythos` variants are generated: their tier is the `MODEL` and `EFFORT` constants in `scripts/build_mythos_variants.py`.
  Edit the base file or the script, never a variant, then run the script.

Codex tiers are set by the codex-review skill defaults and the flags below.

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
- Research-question refinement after a literature review: `question-refiner-mythos`.
- Resolving a deadlock before it reaches the human: `arbiter-mythos`, per the deadlock ladder below.

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
| question-refiner | Opus, high | Refinement stages start at `question-refiner-mythos`. `question-refiner` only when a brief says the refinement is minor |

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
| summarizer | none (approval packets) | Sonnet, medium | `summarizer` -> `summarizer` with `model: opus, effort: medium` if `check_packet.py` fails twice |
| Codex | G3 | `gpt-6.1-sol`, `high` | Critical artifacts: `--effort highest` (no ladder below it) |

`counterexample-hunter` climbs on survival: after an accept with an empty `issues` list at one rung, the next round runs one rung up,
until the top rung that the claim's importance warrants (lemma: Opus rung; main theorem or design: Mythos rung).
`regression-checker` moves up only if its output is inconsistent with `claims.md` dependencies.

### Codex (G3)

- Default: model `gpt-6.1-sol`, effort `high`.
- Main theorems, designs and final deliverables (critical artifacts): the highest effort Codex lists for the model.
  Pass `--effort highest`; the script reads the level from `~/.codex/models_cache.json` (for `gpt-6.1-sol`: `ultra`).
- Other G3 runs a brief asks for: the default.

### Deadlocks

Deadlock as defined in the review-gates skill (same canonical issue rejected twice and kept twice).

`arbiter` -> `arbiter-mythos` -> human.

- Always start at `arbiter`.
- Call `arbiter-mythos` if `arbiter` rules `needs_human`, or if the issue concerns a main theorem (then always, and its ruling governs).
- Escalate to the human only if the governing ruling is `needs_human`.

## Budget

Budgets are never a human decision. They never appear in a question, card, packet or approval.

- Automatic budget per stage type, for one brief: `python3 ~/dotclaude/scripts/budgets.py get <stage type>`.
  Defaults: [budgets.default.json](budgets.default.json). Calibrated values: `budgets.json` next to it (git-ignored), rewritten by
  `budgets.py recalibrate` from the usage logged in past runs (90th percentile of brief totals x 1.25, at least 3 briefs).
  `rw` recalibrates when it starts.
- The brief records `rounds` (at most 5), `tokens` (the automatic budget) and `extended`.
- Usage is logged by the PostToolUse hook after every dispatch: `.work/usage.tsv` and `~/.claude/rw-usage.tsv`. Never by hand.
- Overrun: `review_status.py` decides. New issues in the latest round: `extend-budget`, once by 50%, logged. Otherwise the loop is
  stalled (review-gates rule 3). Round limits and stall detection are the real stops.
- The only usage event that reaches the human is the subscription limit: `rw` pauses, notifies, and resumes after the reset.
- Token usage reaches the human only in the checkpoint screen, as information.
- A T3 dispatch needs no approval. It is logged like every routing choice.

## Logging

Every dispatch whose tier differs from the agent file default, and every T3 dispatch, gets a `decisions.md` entry:

```
## <YYYY-MM-DD> | route <claim or brief> to <agent> (<rung>)
- made by: orchestrator
- class: logged
- card: none
- reason: <one line, e.g. "survived counterexample-hunter at Opus rung, r3">
- routing: <agent>, <model ID>, <effort>
```

Default-tier dispatches are recorded in the brief header (`assigned agent`, `model`, `effort`) only.
