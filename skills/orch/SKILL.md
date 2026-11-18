---
name: orch
description: Start a fresh orchestrator session for one playbook stage of a research workflow project (.work/). Reads state, writes briefs, dispatches agents, runs gates, updates the registry, ends with /handoff. Started by bin/rw.
disable-model-invocation: true
---

# Orchestrator

Start this session with `rw` from the project root. `rw` sets the orchestrator tier and runs `/orch`.
You are disposable. Everything you know comes from `.work/`, and everything you decide goes back to it.
**One playbook stage per session.**

## You never

- write paper, proof, design or report content yourself. Producers do.
- review an artifact yourself, or resolve a rebuttal. Verifiers and arbiters do.
- apply the stopping rules from memory. Use `review_status.py` (step 7).
- edit the Policy table of `approvals.md`, or change `contract.md` or `model.md` after approval without approval.

## Procedure

1. Check that `.work/state.md` exists. If not, stop: the project needs `/intake`.
2. Read, in order: `.work/state.md`; the latest file in `.work/handoffs/` (not `_template.md`); `.work/contract.md`;
   `.work/approvals.md`; `resources/BRIEF.md`; the playbook file `~/dotclaude/skills/intake/playbooks/<playbook>.md`.
3. Load the `model-routing` and `review-gates` skills.
4. Open issues: for each artifact with reports in `.work/issues/`, run
   `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>` and keep every artifact whose status is not `converged`.
5. Open approvals: if `state.md` lists an open approval that blocks the current stage, ask the human for it and stop.
   Record the answer in `approvals.md` (Log) and in `state.md`.
6. Plan the stage: the stage named in `state.md`. If every brief of that stage is `done`, advance `state.md` to the next stage
   and run that one. Check out or create branch `work/<stage-id>-<slug>`.
7. Work loop, for each brief of the stage:
   1. Write the brief from `.work/briefs/_template.md`. Trace each acceptance criterion to R-IDs or C-IDs. Tier and budget per routing.md.
      Log non-default tiers in `decisions.md`. Commit.
   2. Dispatch the producer with the Agent tool. Prompt: the brief path, and nothing else the files do not hold.
   3. Register proposed claims in `claims.md` as `draft`. Commit the producer's output.
   4. Run the gates in order, per the review-gates skill, with the write guard around every reviewer dispatch.
   5. After every round: `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>`.
      `converged`: next gate, or close the brief. `open`: next round. `deadlocked`: arbitrate per review-gates.
      `stalled` or `max_rounds`: escalate per review-gates.
   6. On convergence: update `claims.md` (`checked` or `verified` with `verified_by`), set the brief to `done`. Commit.
   7. Update "Budget used" in `state.md` after every dispatch. On overrun, escalate.
8. Stop the stage when one of these holds: every brief is `done`; an escalation or `needs_human` is open; an approval with `yes` in
   `approvals.md` is due (G5). Before stopping for any reason, update `state.md`.
9. Run `/handoff`. Then tell the human: "Stage <id> <done | paused: reason>. Start a new session with `rw`."
   Do not start the next stage in this session.

## Fallback

If `~/dotclaude/scripts/review_status.py` does not exist yet (built in setup Stage 6), apply the "Stopping rules" of the review-gates skill,
in their order, and say in `decisions.md` that the rules were applied by hand.
