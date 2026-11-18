---
name: review-gates
description: Review gates G0 to G5 for the research workflow. Gate order, which verifier runs each gate, stopping rules for review loops, rebuttals, deadlock arbitration, the issue schema, the reviewer write guard, and when a claim becomes verified. Load in the orchestrator before running any review.
---

# Review gates

The orchestrator runs every gate. Verifiers are blind (see the agent-protocol skill). Tiers per [model-routing](../model-routing/routing.md).
Around every reviewer or arbiter dispatch, at every gate and tier, follow [write-guard.md](write-guard.md).

## Gates

Gates run in this order. A gate runs only after the previous gate has converged.

| Gate | Reviewer | Runs on |
|---|---|---|
| G0 mechanical | `python3 ~/dotclaude/scripts/lint_tex.py --artifact <path> --out <report> [--previous <last report>]`. No model. | every `.tex` change |
| G1 conformance | `conformance-reviewer` | every artifact, before any technical review |
| G2 technical | `assumption-auditor`, then `proof-checker`, then `counterexample-hunter`; `citation-verifier` for artifacts with citations | definitions, statements, proofs, designs, findings |
| G3 cross-model | Codex, via the codex-review skill | critical artifacts (below) |
| G4 style | `style-reviewer` | prose and LaTeX after G1 to G3 converge |
| G5 human | the human, per `.work/approvals.md` | events marked `yes` there |

G1 runs before G2 so that a correct proof of the wrong statement, or in the wrong model, is caught before technical review is spent on it.
Inside G2, `proof-checker` runs only after `assumption-auditor` converges, and `counterexample-hunter` only after `proof-checker` converges.

Critical artifacts: main theorems, designs, and final deliverables (milestone or final). The brief marks an artifact as critical.
Main theorems are the claims the contract or the brief marks as main.

## Dispatching a reviewer

The prompt names: the brief path, the artifact path (with `#label` if it is one claim), the artifact slug, the gate, the round,
the claim IDs in scope, and the paths of arbiter rulings on this reviewer's issues for this artifact. Nothing else.
Never pass producer reasoning, drafts or chat.

## Issue reports

- Schema: `~/dotclaude/schemas/issue-report.schema.json`. Producer responses: `issue-response.schema.json`.
- File names and stable IDs: `.work/issues/README.md` in the project.
- Validate every report: `python3 ~/dotclaude/scripts/validate_issue_json.py ~/dotclaude/schemas/issue-report.schema.json <file>`.
  An invalid report does not count; rerun the reviewer once, then escalate to the human.
- Duplicates across reviewers: the orchestrator sets `duplicate_of` on the later issue (README, "Duplicates").

## Review loop

One round = the producer's revision (or the first draft), then the gate's reviewers, then the producer's response JSON.
A clean round is a round with zero blocking and zero major issues (minor issues allowed).

- Rebuttals: the producer may answer an issue with `rejected` and an argument. The rebuttal goes to the next round's reviewer,
  who keeps the issue (same ID) or drops it. The orchestrator never resolves a rebuttal itself.
- `needs_human`: the issue goes to "Open approvals" in `state.md`. The loop pauses for that issue.
- Record each round in the brief's `## Review log` table (columns fixed by the brief template): round, gate, reviewer, model,
  commit, verdict, counts by severity, and `git hash-object` of each artifact file. The hashes decide "same content" and "edit":
  commits move with every report commit, so the rules below compare content by hash, not by commit.

## Stopping rules

Check after every round, in this order, by running `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>`.
The script applies these rules to each gate reviewer, then gate, then the artifact, and prints a last line
`overall: <status> -> <action> [gate reviewer issue]`. Never apply them by hand. If the script fails, escalate to the human.

1. Converged:
   - Non-critical artifact: one clean round of the gate.
   - Critical artifact: two consecutive clean rounds of the gate. For G1 and G2, a clean G3 round counts as the second round:
     the gate converges when its first clean round and the clean G3 round are on the same content, with no edit in between.
     After the first clean round of G1 or G2 the script prints `open -> next-gate`: run the next gate.
     G3 converges with one clean round. Any edit after a clean round voids it, and the gates rerun from G1.
2. Deadlock: the producer rejects the same canonical issue twice, and the reviewer keeps it twice. Arbitrate (below).
3. Stalled: the producer's revision has no diff, or an artifact hash repeats an earlier round's hash. Escalate to the human.
4. Round limit: 5 rounds per gate reviewer per artifact, or the brief's budget if smaller. Escalate to the human.

Escalating means: set the brief status to `escalated`, add the event to "Open approvals" in `state.md`, log it in `decisions.md`, stop the loop.

## Deadlock arbitration

1. Dispatch `arbiter` on the canonical issue. Prompt: the issue ID, the review and response files that contain it, the brief, the artifact,
   and the ruling file name `.work/issues/<slug>.<gate>.<reviewer>.i<n>.ruling1.json`.
2. Dispatch `arbiter-mythos` (ruling file `...ruling2.json`, plus the path of ruling 1) if ruling 1 is `needs_human`,
   or the issue concerns a main theorem. For a main theorem, ruling 2 governs, even when it differs from ruling 1.
3. Escalate to the human if the governing ruling is `needs_human`. Put its `human_question` in "Open approvals".
4. Validate each ruling against `~/dotclaude/schemas/arbiter-ruling.schema.json`. Log each ruling in `decisions.md`.

Effect of the governing ruling:
- `reviewer_right`: the issue stands, with the ruling's `required_change`. The producer may not reject it again. A further rejection goes to the human.
- `producer_right`: the issue is closed. The reviewer gets the ruling path and must not raise the issue again unless the cited text changes.

## Verified claims

A claim becomes `verified` only when G1 and G2 have converged, and G3 where required, all at one commit with no edits in between.
The orchestrator then writes `verified_by` in `claims.md`, one item per gate reviewer: `<gate>:<reviewer>:<model>@<commit>`.
A claim that converged at an earlier commit, then was edited, is `checked` until the gates converge again.
After every edit, dispatch `regression-checker` and reset the claims it lists from `verified` to `checked`.
An accepted counterexample sets `refuted` with `refuted_by` pointing to the issue ID. Refuted claims are never deleted.
