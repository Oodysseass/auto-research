---
name: review-gates
description: Review gates G0 to G5 for the research workflow. Gate order, which verifier runs each gate, stopping rules for review loops, rebuttals, the issue schema, the reviewer write guard, and when a claim becomes verified. Load in the orchestrator before running any review.
---

# Review gates

The orchestrator runs every gate. Verifiers are blind (see the agent-protocol skill). Tiers per [model-routing](../model-routing/routing.md).
Around every reviewer dispatch, at every gate and tier, follow [write-guard.md](write-guard.md).

## Gates

Gates run in this order. A gate runs only after the previous gate has no open blocking or major issue.

| Gate | Reviewer | Runs on |
|---|---|---|
| G0 mechanical | `scripts/lint_tex.py` (Stage 6). No model. | every `.tex` change |
| G1 conformance | `conformance-reviewer` | every artifact, before any technical review |
| G2 technical | `assumption-auditor`, then `proof-checker`, then `counterexample-hunter`; `citation-verifier` for artifacts with citations | definitions, statements, proofs, designs, findings |
| G3 cross-model | Codex, via the codex-review skill | main theorems, designs, every final deliverable |
| G4 style | `style-reviewer` | prose and LaTeX after G1 to G3 pass |
| G5 human | the human, per `.work/approvals.md` | events marked `yes` there |

G1 runs before G2 so that a correct proof of the wrong statement, or in the wrong model, is caught before technical review is spent on it.
Inside G2, `proof-checker` runs only after `assumption-auditor` accepts, and `counterexample-hunter` only after `proof-checker` accepts.

## Dispatching a reviewer

The prompt names: the brief path, the artifact path (with `#label` if it is one claim), the artifact slug, the gate, the round,
and the claim IDs in scope. Nothing else. Never pass producer reasoning, drafts or chat.

## Issue reports

- Schema: `~/dotclaude/schemas/issue-report.schema.json`. Producer responses: `issue-response.schema.json`.
- File names and stable IDs: `.work/issues/README.md` in the project.
- Validate every report: `python3 ~/dotclaude/scripts/validate_issue_json.py ~/dotclaude/schemas/issue-report.schema.json <file>`.
  An invalid report does not count; rerun the reviewer once, then escalate to the human.
- Duplicates across reviewers: the orchestrator sets `duplicate_of` on the later issue (README, "Duplicates").

## Review loop

One round = the producer's revision (or the first draft), then the gate's reviewers, then the producer's response JSON.

- Rebuttals: the producer may answer an issue with `rejected` and an argument. The rebuttal goes to the next round's reviewer,
  who keeps the issue (same ID) or drops it. The orchestrator never resolves a rebuttal itself.
- `needs_human`: the issue goes to "Open approvals" in `state.md`. The loop pauses for that issue.
- Record each round in the brief under `## Review log`: round, gate, reviewer, model, commit, verdict,
  counts by severity, and `git hash-object` of each artifact file.

## Stopping rules

Check after every round, in this order.

1. Converged: zero blocking or major issues in 2 consecutive rounds of the same gate. Move to the next gate.
2. Deadlock: the producer rejects the same canonical issue twice, and the reviewer keeps it twice.
   First rerun the deadlocked role at T3 if routing.md allows it. Otherwise, or if the deadlock persists, escalate to the human.
3. Stalled: the producer's revision has no diff, or an artifact hash repeats an earlier round's hash. Escalate to the human.
4. Round limit: 5 rounds per gate per artifact, or the brief's budget if smaller. Escalate to the human.

Escalating means: set the brief status to `escalated`, add the event to "Open approvals" in `state.md`, log it in `decisions.md`, stop the loop.

## Verified claims

A claim becomes `verified` only when G1 and G2 have converged, and G3 where required, all at one commit with no edits in between.
The orchestrator then writes `verified_by` in `claims.md`, one item per gate reviewer: `<gate>:<reviewer>:<model>@<commit>`.
A claim that converged at an earlier commit, then was edited, is `checked` until the gates converge again.
After every edit, dispatch `regression-checker` and reset the claims it lists from `verified` to `checked`.
An accepted counterexample sets `refuted` with `refuted_by` pointing to the issue ID. Refuted claims are never deleted.
