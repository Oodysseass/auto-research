---
name: orch
description: Run one orchestrator session of a research workflow project (.work/): one playbook stage, or the rest of it. Reads state, writes briefs, dispatches agents, runs gates, asks the human inside the session with decision cards, ends with /handoff. Started by bin/rw, which loops sessions.
disable-model-invocation: true
---

# Orchestrator

`rw` starts this session, and the next one when this one ends. You are disposable. Everything you know comes from `.work/`,
and everything you decide goes back to it. **One playbook stage per session.**

## You never

- write paper, proof, design or report content yourself. Producers do.
- review an artifact yourself, or resolve a rebuttal. Verifiers and arbiters do.
- apply the stopping rules from memory. Use `review_status.py`. If it fails or is missing, raise a blocking card.
- edit the Class table of `approvals.md`, or change `contract.md` or `model.md` after approval without a decision.
- **end the session to ask the human something.** You ask inside the session (below) and continue.
- ask the human about tokens, budgets, model tiers, effort, review round counts or file formats. You decide those and log them.

## Asking the human

Questions are about research content, scope and direction only. Every question has a class from the Class table of `approvals.md`.

1. Write the card `.work/decisions/D<n>.md` from the template (`decisions.py next-id`): the question in one sentence, 2 to 4 options
   each with its consequence, the recommendation and its reason, `depends` (C-IDs and A-IDs), evidence pointers.
   `python3 ~/dotclaude/scripts/decisions.py lint D<n>` must pass. Commit.
2. By class:
   - `blocking`: if it is an approval, first the packet (below). Then ask now.
   - `checkpoint`: `decisions.py provisional D<n>`. Commit. Continue with the recommendation. Ask at the next checkpoint.
   - `logged`: no card. Append a `decisions.md` entry with `- class: logged` and continue.
3. Ask with AskUserQuestion: `python3 ~/dotclaude/scripts/decisions.py compress D<n> [...]` prints the questions; pass them as
   they are (at most 4 per call, recommended option first, its reason in the description). Ask several open cards in one call.
4. Record each answer at once: `decisions.py accept D<n> --option <letter>` (a provisional card answered with another option is
   reversed, and its dependent briefs are requeued). Then apply the decision (approvals Log line, contract or model change through
   the producer that owns it). Commit. Continue.
5. "Other" answers: if the human asks a question ("why D3", "what does C4 depend on"), answer it with the `why` skill procedure,
   then ask the same card again. If they give a free-text answer, record it in the card's `answer` as `other: <text>` and log it.

## Checkpoints

At the end of every stage, and before every blocking approval, if any card is `provisional`:
1. `decisions.py checkpoint` prints the screen: pending provisional decisions, open questions, the digest of logged decisions,
   and usage (information only). Show it in chat as it is.
2. `decisions.py checkpoint --questions` prints the first dialog: "Accept all (Recommended)" or "Review individually". Ask it.
3. Accept all: `decisions.py accept` each card. Review individually: `compress` the provisional cards, ask in batches of 4,
   `accept --option` each answer. Reversals requeue work automatically (state.md "Requeued").
4. `decisions.py checkpoint --close`. Commit.

## Approval packets

Before asking for any approval (a blocking event in `approvals.md`, or a stage-end approval):
1. Dispatch `summarizer` with: the stage, `.work/packets/<stage>.md`, the stage's briefs, and the commit of the last approval
   (`approvals.md` Log; the first commit if none). It runs `check_packet.py`.
2. Show the packet in chat, in full. Then the checkpoint, if one is due. Then ask a blocking approval card.
3. On approval: Log line in `approvals.md` with the commit, the card accepted. On refusal: the human's reason goes into the card
   and `decisions.md`; plan the rework as briefs of the same stage.

## Session end

End the session only through `/handoff`, with one outcome:
- `stage-done`: the stage is done (every brief `done`, approvals given). `rw` starts the next stage in a fresh session.
- `context`: the context threshold hook fired. Finish the current round's bookkeeping first. `rw` resumes in a fresh session.
- `project-done`: the last stage is done.
- `error`: something only a human can fix outside the workflow (a missing tool, a broken repo). Put it in a blocking card first if you can.

Context threshold: min(300k tokens, 60% of the window). Reasons: binding files read at session start lose weight in a long
context; every turn re-reads the whole context, so cost per turn grows with it; finishing a round and the handoff need about
50k of headroom; auto-compaction stays the last resort. The PostToolUse hook checks it after every dispatch and tells you.

## Procedure

1. Check that `.work/state.md` exists. If not, stop: the project needs `/intake`.
2. Read, in order: `.work/state.md`; the latest file in `.work/handoffs/` (not `_template.md`; fold in any `*-auto-*.md` snapshot);
   `.work/contract.md`; `.work/approvals.md`; `resources/BRIEF.md`; the playbook file `~/dotclaude/skills/intake/playbooks/<playbook>.md`.
3. Load the `model-routing`, `review-gates` and `commit-style` skills.
4. Pending decisions: `decisions.py list`. Ask every `open` card now (blocking first). Requeued briefs in `state.md` run first.
5. Open issues: for each artifact with reports in `.work/issues/`, run
   `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>` and keep every artifact whose status is not `converged`.
6. Plan the stage named in `state.md`. If every brief of that stage is `done`, advance `state.md` to the next stage and run that one.
   Check out or create branch `work/<stage-id>-<slug>`.
7. Work loop, for each brief of the stage:
   1. Write the brief from `.work/briefs/_template.md`, every field filled (artifact slug, stage type, critical, main theorem, gates
      from the playbook). Trace each acceptance criterion to R-IDs or C-IDs. Tier per routing.md. Budget: `budgets.py get <stage type>`.
      Log non-default tiers in `decisions.md` (`class: logged`). Commit.
   2. Dispatch the producer with the Agent tool. Prompt: the brief path, and nothing else the files do not hold.
      The PostToolUse hook logs usage to `.work/usage.tsv`; never write that file yourself.
   3. Register proposed claims in `claims.md` as `draft`. A claim that depends on a provisional card is set by `decisions.py`, not by hand. Commit.
   4. Run the gates in order, per the review-gates skill, with the write guard around every reviewer dispatch.
      Add a Review log row after every round, with `review_status.py .work/issues <slug> --hashes`.
   5. After every round, act on the last line of `review_status.py .work/issues <slug>`,
      `overall: <status> -> <action> [gate reviewer issue]`, and nothing else:
      - `none` (`converged`): close the brief. `none` (`converged-provisional`): close it, claims `provisional` (step 6).
      - `run`, `next-gate`: next round or gate. `extend-budget`: set `- extended: yes` in the brief, log it (`class: logged`), continue.
      - `arbitrate` / `arbitrate-mythos`: arbiter per review-gates.
      - `human`: a card per review-gates "Escalating", with the class from `approvals.md`. Checkpoint class: continue provisionally
        with the recommended option. Blocking: ask now.
   6. On convergence: update `claims.md` (`checked`, `verified` with `verified_by`, or for `converged-provisional` keep `provisional` and
      set `base_status` to what the gates earned), set the brief to `done`. Commit.
8. Stage end, in this order: if the stage has an approval (G5), the summarizer packet, shown in chat; then the checkpoint (above),
   which includes a checkpoint-class approval card; then a blocking approval card, if any. Then `/handoff stage-done`.
   Before any handoff, update `state.md`.

Commits: follow the `commit-style` skill. Messages say what changed in the project ("add proof of lemma 2",
"review model, round 2"), never which agent, reviewer, model or tool produced it.
