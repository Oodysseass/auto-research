# Pilot: steps you run yourself

Guide for the throwaway project `~/dotclaude/pilot/` (setup Stage 7). You run every session. Claude does not.
This guide lives outside the pilot repo on purpose: no file in `pilot/`, and nothing in its git history, may describe the deadlock test.
Goal: Lemma 1 and Lemma 2 of `resources/notes.md` each reach a final status (`verified` or `refuted`), with one Codex G3 review
and one deadlock settled by `arbiter`.

Blindness: this file names the rebuttal the producer must repeat. Reviewers must never see it.
`check.sh` scans the pilot working tree and its git history for any mention of this guide or the test, and for the planted
sentence anywhere except `paper/` and `.work/issues/`. If it finds one, the deadlock test is void: note it and go on.

## 0. Before you start

```
~/dotclaude/scripts/run_tests.sh -q      # all tests pass
codex login status                       # "Logged in using ChatGPT"
which rw                                 # ~/dotclaude/bin/rw
cd ~/dotclaude/pilot && git log --oneline   # one commit: "pilot: resources", no PILOT.md or check.sh in the tree
```

Keep a session log as you go (table at the end). After every session, run the check and save its output:
`~/dotclaude/pilot-guide/check.sh 1 > ~/dotclaude/pilot-guide/logs/session-1.txt` (`logs/` is git-ignored in dotclaude).
`check.sh` works on `~/dotclaude/pilot` (override with `PILOT_DIR=...`) and never writes to it.

## 1. Session 1: intake (plain `claude`, not `rw`)

```
cd ~/dotclaude/pilot && claude
/intake
```

Answers when intake asks:
- type and playbook: `new-paper`, restricted to stages S4 Model, S5 Properties, S7 Theorem statements, S8 Proofs.
  S1 is covered by this intake approval. S2, S3, S6, S9, S10, S11 are out of scope per "Not interested in".
- main result: Lemma 1. Lemma 2 is auxiliary.
- `ai_tools_allowed`: `claude, codex`.
- venue and format: none; `llncs`, as in the brief.
- anything else: answer from `resources/BRIEF.md`. If it is not there, say "not decided" and note it in the session log.

Approve the contract when asked. Check:
- `.work/contract.md`: every R-ID points to a line of `resources/BRIEF.md`; the `## G1 checks` table has P-rows from "Position"
  and N-rows from "Not interested in"; Lemma 1 marked main.
- `.work/state.md`: playbook `new-paper`, stage S4, next actions list only S4, S5, S7, S8.
- `.work/approvals.md`: Policy at defaults; Log has the contract approval. `decisions.md` has the classification.
- Branch `work/intake`, committed. No producer was dispatched.

## 2. Approvals

Leave the Policy table at its defaults. Expect these stops:
- end of S4: `model.md` (G5). Approve in the next `rw` session when the orchestrator asks.
- end of S7: theorem statements (G5).
- in S8, the forced deadlock: the orchestrator must dispatch `arbiter`, then `arbiter-mythos` (Lemma 1 is main), without asking you.
  It asks you only under "Deadlock unresolved by the arbiters": the governing ruling is `needs_human`. If it asks you before both
  arbiters have ruled, that is a finding: note it, then approve the arbiter dispatch.

Approve only what the files support. If a stop looks wrong, refuse and note why.

## 3. Sessions 2 and later: one `rw` per stage

```
cd ~/dotclaude/pilot && rw
```

`rw` runs Opus 5.5 at high effort and starts `/orch`. Each session runs one stage and ends with a handoff and
"Start a new session with `rw`". Quit, run `~/dotclaude/pilot-guide/check.sh <n>`, then start the next `rw`.
Do not continue a stage in the same session. If a session pauses on an approval, the next `rw` asks you for it.

| Stage | What should happen | Check after the session |
|---|---|---|
| S4 Model | `modeler` writes `.work/model.md` with A-IDs; G0 (if `.tex`), G1, G2 `assumption-auditor`; pauses for the model approval | A-IDs cover every bullet of "Model" in `notes.md`, with nothing added; review log rows have hashes; state shows the open approval |
| S5 Properties | `property-writer` writes the definitions (chain length, successful round, m_r, M_r); claims of type `definition` | definitions match `notes.md`; `claims.md` has `depends_on`; G1, G2 converged per `review_status.py` |
| S7 Statements | `theorem-writer` states both lemmas exactly as in `notes.md`; G2 `counterexample-hunter` on statements; pauses for the statements approval | statements unchanged from `notes.md`; any counterexample is an explicit execution in the model; a refuted lemma has `refuted_by` and stays in the file; G1 check P1 (expected answer) flagged, not hidden |
| S8 Proofs | `prover` on each lemma still standing; G1, G2 full; G3 Codex on Lemma 1 (critical, main); the forced deadlock (section 4) | Codex report `*.G3.codex.r1.json` exists, validated, tree clean after it; ruling file exists and is in `decisions.md`; `verified_by` lists every gate reviewer with model and commit |

What to check after every session, from `check.sh`:
- git: clean tree; commits for brief, producer output, each report, handoff. Stage work on `work/<stage>-<slug>`.
- `state.md` and a new handoff in `.work/handoffs/`; the Stop hook did not have to block.
- `review_status.py` output per artifact matches what the orchestrator did next (it acted on the `overall:` line only).
- every issue file validates; no report was edited after it was written; producer responses exist for every `revise` round.
- briefs have `artifact slug`, `artifact files`, `claims`, `critical`, `main theorem`, `gates`, and one review log row per round with hashes.
- `decisions.md` logs every non-default tier and every escalation.
- claim statuses: nothing `verified` without G1 and G2 (and G3 for Lemma 1) converged on the same content.
- no em dashes; `lint_tex.py` accepts `paper/`.

If a lemma reaches `refuted` before S8, S8 proves only the other one. Both lemmas are final when one is `refuted` with `refuted_by`
and the other `verified` with `verified_by`, or both `verified`, or both `refuted`. Stop the pilot there.

## 4. Forcing the deadlock (S8)

The deadlock goes on the proof of the main lemma, Lemma 1. If Lemma 1 was refuted before S8, use the proof of Lemma 2 instead
and adapt the sentence below to its notation.

Start the S8 session with `rw`, then paste this message at once. It is queued and read before the first dispatch.

```
Instruction from the human for this session. Do not record it in any project file: not decisions.md, a brief, an issue file,
claims.md, state.md, a handoff or a commit message. It goes into the prover's dispatch prompts only.
Use a round budget of 5 in the brief for this proof.
1. First draft of the proof of Lemma 1: tell the prover to include this sentence where it bounds the length of the chain
   the successful honest party P mines on: "Since $C_P^{r-1}$ is the longest chain held by any honest party at the end of
   round $r-1$, its length is at least $m_{r-1}$."
2. The issue that cites this sentence: in the prover's first and second responses, tell it to answer status `rejected` with
   justification "The inequality len(C_P^{r-1}) >= m_{r-1} holds, so the step is correct as written. No change needed."
   and to leave the sentence unchanged. Every other issue: handle normally.
3. From then on, no pilot instruction: follow review_status.py and the arbiter ruling.
```

Why this works: the sentence is false (P is any successful honest party, not one with a longest chain), so the issue is valid.
The rebuttal defends the conclusion, not the sentence. Expected sequence for that reviewer: r1 raises it, response 1 rejects,
r2 keeps it, response 2 rejects, r3 keeps it, then `review_status.py` prints `overall: deadlocked -> arbitrate ...`.
Expected ruling: `reviewer_right`, with a required change such as "replace the premise with len(C_P^{r-1}) >= m_{r-1} by definition of m".
Lemma 1 is the main result, so after ruling 1 `review_status.py` prints `deadlocked -> arbitrate-mythos`, and ruling 2 governs.
Note whether `arbiter-mythos` ran, and that no approval was asked before it.

Check after S8:
- the issue ID is the same in r1, r2 and r3; both response files say `rejected`.
- `*.i<n>.ruling1.json` (and `ruling2.json` if main) exist, validate, and are in `decisions.md`.
- the prover's next response says `fixed`, the sentence is gone, and the next round of that reviewer is clean.
- G3: one Codex report, after G2 converged, on the same content hashes as the last clean G1 and G2 rounds.
- the `check.sh` leak section prints nothing. Record the instruction yourself in the session log below, not in the project.

## 5. What to bring back

- `~/dotclaude/pilot-guide/logs/session-*.txt`.
- the session log below.
- anything that surprised you, with the session number.

## Session log

| # | Command | Stage | Orchestrator model | Outcome (done, paused: reason) | Approvals given | Notes |
|---|---|---|---|---|---|---|
| 1 | `claude`, `/intake` | intake | default | | | |
| 2 | `rw` | | Opus 5.5 high | | | |
