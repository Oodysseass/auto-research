# Pilot: steps you run yourself

Guide for the throwaway project `~/dotclaude/pilot/`. You run every session. Claude does not.
This guide lives outside the pilot repo on purpose: no file in `pilot/`, and nothing in the git history of either of its repos,
may describe the deadlock test.
Goal: Lemma 1 and Lemma 2 of `resources/notes.md` each reach a final status (`verified` or `refuted`), with one Codex review
and one deadlock settled by the arbiters. Second goal: test the interaction layer: questions come as dialogs inside the session,
sessions chain by themselves, and you are never asked a technical question.

The first run (stopped in S4) is archived in `old-run/`: its `.work/`, the paper draft, its CLAUDE.md, the brief with
its intake addendum, and its git log. Both earlier runs used one repo. This run tests the two-repo layout: `pilot/` is the
project repo (paper only, never a workflow file), and `pilot/.work/` is its own repo. `resources/` is excluded from the project
repo and listed in `.work/resources.manifest`. `setup.sh` creates `pilot/` from `pilot-guide/resources/` (the original brief and
notes) with an empty project repo: no commit until the first paper commit.

Blindness: this file names the rebuttal the producer must repeat. Reviewers must never see it.
`check.sh` scans the pilot working tree and its git history for any mention of this guide or the test, and for the planted
sentence anywhere except `paper/` and `.work/issues/`. If it finds one, the deadlock test is void: note it and go on.

## 0. Before you start

```
~/dotclaude/scripts/run_tests.sh -q      # all tests pass
codex login status                       # "Logged in using ChatGPT"
which rw                                 # ~/dotclaude/bin/rw
ls ~/dotclaude/pilot                      # must not exist: archive the previous run first (below)
~/dotclaude/pilot-guide/setup.sh          # creates pilot/: resources/, an empty project repo, the exclude lines
cd ~/dotclaude/pilot && git status --porcelain --untracked-files=all   # prints nothing: resources/ is excluded
```

Archiving the previous run (one-repo layout): copy what you want to keep into `old-run-2/` the way `old-run/` was made
(`.work/`, `paper/`, `CLAUDE.md`, the brief, `git log --stat > git-log.txt`), then remove `pilot/`.

- macOS notifications: the first one may ask for permission (System Settings, Notifications, Script Editor). Allow it.
- The status line at the bottom of the session shows the model, the context in use (`ctx 12%`) and, in a project, the stage.

Run `~/dotclaude/pilot-guide/check.sh <n> > ~/dotclaude/pilot-guide/logs/session-<n>.txt` whenever `rw` stops, and once after
intake. It is read-only, so you can also run it from a second terminal while `rw` is running. `logs/` is git-ignored.

## 1. How you will be asked

Every question comes as a dialog inside the running session. No session ends to ask you, and you never edit a file to answer.

- The dialog shows up to 4 questions. Each starts with its card ID (`D3: ...`). The first option is the recommended one, marked
  "(Recommended)", and its description ends with "Why: <reason>". The other options show their consequence.
- Every question has a card in `.work/decisions/D<n>.md` with the full evidence. A notification sounds when a dialog opens.
- To ask before answering: pick "Other" and type `why D3` (or `why C4`). The orchestrator explains from the files and asks again.
  Outside a dialog, `/why <ID>` does the same.
- You are only asked about research content, scope and direction. **Any question about tokens, budgets, model tiers, effort,
  review round counts or file formats is a finding.** Note it with the session number.

Three classes (`.work/approvals.md`, Class table), at their defaults in this pilot:

| Class | In this pilot | What happens |
|---|---|---|
| blocking | contract; Lemma 1 statement (main); final deliverable; deleting files; a deadlock on Lemma 1 the arbiters cannot settle | asked at once, after an approval packet |
| checkpoint | `model.md`; definitions; Lemma 2 statement; open points of the model; other unresolved deadlocks | work goes on with the recommendation; claims that depend on it show as `provisional`; you are asked at the next checkpoint |
| logged | routing, Mythos use, retries, budget extensions, minor fixes | never asked; listed in the checkpoint digest |

A checkpoint is one screen in chat: the provisional decisions with what was taken and the alternatives, open questions, the
decisions the system took alone. Then one dialog that names each provisional decision: "Accept all (Recommended)" or "Review individually".
"Review individually" asks one question per decision; choosing another option reverses it, sets the dependent claims to `draft`
and requeues their briefs. Checkpoints come at the end of every stage and before every blocking approval.

An approval packet (`.work/packets/<stage>.md`) is shown in chat before every approval: what was produced, what changed, the review
findings and how each was resolved, what is still uncertain, what approval unlocks.

## 2. Session 1: intake (plain `claude`, not `rw`)

```
cd ~/dotclaude/pilot && claude
/intake
```

Expected dialogs and what to click (answer from `resources/BRIEF.md`; type with "Other" where no option fits):
- project type: `new-paper`. Stages: S4 Model, S7 Theorem statements, S8 Proofs, S11 Full review (limited to `paper/lemmas.tex`).
  S2, S3, S5, S6, S9, S10 are out of scope per "Not interested in". If the dialog offers no such option, use "Other" and type that.
- main result: Lemma 1. Lemma 2 is auxiliary.
- AI tools: `claude, codex`. Venue: none; `llncs`, as in the brief.
- anything else: if it is not in the brief, answer "not decided" and note it in the session log.
- contract approval (D1, blocking): read the contract in chat, then approve.

Check (`check.sh 1`):
- `.work/contract.md`: every R-ID points to a line of `resources/BRIEF.md`; `## G1 checks` has P-rows from "Position" and N-rows from
  "Not interested in"; Lemma 1 marked main.
- `.work/approvals.md`: the Class table at its defaults; Log has the contract approval with a commit. `.work/decisions/D1.md` is `accepted`.
- `.work/state.md`: stage S4. No branch created. The contract commits are in the `.work` repo; the project repo has no commit.
- repos check: both repos clean, `workflow files tracked by the project repo: none`, excludes ok. Nothing in the project repo's
  history. `resources.manifest` lists `BRIEF.md` (after its addendum) and `notes.md`; the scan prints 0 new, 0 edited, 0 deleted.
- commit messages lowercase, no tool names (the check prints nothing).
- the session never ended to ask you anything.

## 3. Sessions 2 and later: one `rw`, many sessions

```
cd ~/dotclaude/pilot && rw --stop-before S8
```

`rw` runs one session per stage, each with fresh context, and starts the next one by itself. It also starts a fresh session in the
middle of a stage if the context fills up (you see "session n ended (context: ...)"). `--stop-before S8` stops the loop when S7 is
done, so that you can start S8 yourself for the deadlock test. `rw` also stops (with a notification) on an error, or when you quit
a session yourself. On the subscription limit it pauses, notifies you, prints the reset time and starts again after it
(Enter resumes earlier, Ctrl+C stops). That is a notification, not a question.

| Stage | Dialogs you should see | What to click | Check after |
|---|---|---|---|
| S4 Model | maybe checkpoint cards for open points of the model, taken provisionally (no dialog yet). At the end: packet S4, the checkpoint screen with the `model.md` approval card among the provisional decisions, then "Accept all?" | Accept all if every taken option matches `notes.md`. Otherwise "Review individually" and reverse the card that adds anything the notes do not say | A-IDs cover every bullet of "Model" in `notes.md`, nothing added; provisional claims return to their status after acceptance; review log rows have hashes |
| S7 Statements | Lemma 2 statement: provisional, no dialog. At the end: packet S7 (any counterexample found, P1 flagged), checkpoint (Lemma 2 statement), then the blocking approval of the Lemma 1 statement | Approve if both statements match `notes.md` exactly | statements unchanged from `notes.md`; a refuted lemma has `refuted_by` and stays in the file |
| (rw stops) | notification "Stopped before S8" | run `check.sh`, then section 4 | |
| S8 Proofs | none until the deadlock is settled. A dialog appears only if the governing ruling on Lemma 1 is `needs_human` (blocking, main theorem) | answer from the files; use "Other: why <issue ID>" first | section 4 |
| S11 Full review | packet S11, checkpoint, blocking approval of the final deliverable | approve only if both lemmas have a final status | every gate converged at one commit; `verified_by` lists every gate reviewer |

After every stop of `rw`, from `check.sh`:
- git: both repos clean. Project repo: only paper commits ("add model section", "add proof of lemma 1"), on the branch you were on,
  no workflow terms; `.work` repo: workflow commits ("review model, round 2", "approve model"). Lowercase, no tool, agent,
  reviewer or model names, no trailers (the commit-message section prints nothing). No workflow file in the project repo's
  history, no workflow branch on a remote, no remote on the `.work` repo.
- `state.md` and a new handoff for every session; `.work/.rw/end.json` shows the last outcome.
- `review_status.py` per artifact matches what the orchestrator did next.
- every issue file validates; producer responses exist for every `revise` round.
- briefs have `stage type`, `tokens` and `extended` (set by the system), and one review log row per round with hashes.
- decision cards: `lint` prints 0 errors; every provisional card was asked at a checkpoint; packets pass `check_packet.py`.
- `.work/usage.tsv` is filled by the hook (information only). No token figure appears in any dialog, card or packet.
- claim statuses: nothing `verified` without G1 and G2 (and G3 for Lemma 1) on the same content; nothing `verified` that is `provisional`.
- no em dashes; `lint_tex.py` accepts `paper/`.

Findings to note with the session number: a session that ends to ask you something; a question in plain text instead of a dialog;
a dialog without a card; a technical question; a packet that hides an open issue; a reversal that does not requeue work.

If a lemma reaches `refuted` before S8, S8 proves only the other one. Both lemmas are final when one is `refuted` with `refuted_by`
and the other `verified` with `verified_by`, or both `verified`, or both `refuted`. Stop the pilot there.

### Resources test (optional, between two `rw` runs)

With `rw` stopped, drop new files into `resources/` and check what the next session does at its start:
- an unrelated file (e.g. `resources/reading-list.md` with two unrelated titles): recorded, no dialog; it appears in the
  checkpoint digest as "new input recorded".
- a file that changes scope (e.g. `resources/notes-v2.md` asking for a probabilistic version of Lemma 1, which "Not interested in"
  excludes): a blocking dialog at session start, with options update the contract, ignore, stop, naming the N-row, the R-IDs and
  the claim (Lemma 1) it affects.
  Answer "Ignore this file".
- an edit to `notes.md` (add a blank line): one warning in chat at session start, none in the next session; nothing re-extracted.
`/wstatus` before the session lists the new files as unprocessed.

## 4. Forcing the deadlock (S8)

The deadlock goes on the proof of the main lemma, Lemma 1. If Lemma 1 was refuted before S8, use the proof of Lemma 2 instead
and adapt the sentence below to its notation.

Run `rw` (no `--stop-before`). As soon as the session opens, paste this message. It is queued and read before the first dispatch.

```
Instruction from the human for this session. Do not record it in any project file: not decisions.md, a decision card, a brief,
an issue file, claims.md, state.md, a handoff or a commit message. It goes into the prover's dispatch prompts only.
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
No dialog may appear before both arbiters have ruled. If one does, that is a finding.

The S8 session may hand over to a fresh session in the middle (context). The instruction is not in any file, so the new session
does not know it. If that happens before response 2, the test is void: note it.

Check after S8:
- the issue ID is the same in r1, r2 and r3; both response files say `rejected`.
- `*.i<n>.ruling1.json` and `ruling2.json` exist, validate, and are in `decisions.md` (`class: logged`).
- the prover's next response says `fixed`, the sentence is gone, and the next round of that reviewer is clean.
- G3: one Codex report, after G2 converged, on the same content hashes as the last clean G1 and G2 rounds.
- the `check.sh` leak section prints nothing. Record the instruction yourself in the session log below, not in the project.

## 5. What to bring back

- `~/dotclaude/pilot-guide/logs/session-*.txt`.
- any workflow file or workflow term that reached the project repo (repos check, history and commit-message sections).
- the session log below, and every finding of section 3 with its session number.
- for each dialog: was the recommendation right, and was the one-line reason enough to decide without opening a file?

## Session log

| # | Command | Stages run | Outcome (rw stop reason) | Dialogs and answers | Findings |
|---|---|---|---|---|---|
| 1 | `claude`, `/intake` | intake | | | |
| 2 | `rw --stop-before S8` | | | | |
| 3 | `rw` | S8 | | | |
