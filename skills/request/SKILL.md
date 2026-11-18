---
name: request
description: Commitment in a research workflow project (.work/). Runs one piece of work the human committed in a plain claude session (asked for it, accepted the session's offer, or typed a quick: or full: prompt) as a request - record it in resources/BRIEF.md with its attachments and the agreed scope, assess its impact on the contract, model, claims and agenda, execute it through producers and proportional gates, report a short packet, commit in both repos, then wait. Not for discussion (converse skill). Not under rw.
---

# Request

You are the orchestrator for one request: work the human committed. They are present. Discussion before it was free
(`converse` skill); from here on the work is recorded and checked. The orch skill's rules hold
(`~/dotclaude/skills/orch/SKILL.md`: "You never", "Two repos", "Asking the human"), except its procedure: you run this one.
Load `model-routing`, `review-gates` and `commit-style` when step 3 dispatches or commits.
Script: `R=~/dotclaude/scripts/request.py` (`python3 $R ...`, from the project root).

Never a step for the human: recording, saving attachments, the manifest, the registry, commits. Never ask about tokens,
budgets, tiers, effort, rounds or file formats. A `raw:` prompt never reaches this skill.

## 1. Record

Before anything else, run the record command the prompt hook gave you:
`python3 $R record --session <id> --slug <2-4 word slug> --title "<one-line title>" [--scope "<agreed scope>"]`.
It records the human's last prompt verbatim. When the commitment came out of a discussion ("yes, do it"), pass `--scope`
with the scope agreed in the discussion, in one or two sentences, so the record stands on its own.
A prompt that only continues the request in progress (an answer to your question, a correction, "also do X to it") is
`--follow-up RQ<n>`: same request, text appended. If the hook gave no command (it failed), write the prompt verbatim to
a scratch file and pass `--text-file`.
It appends the prompt verbatim to `resources/BRIEF.md` under `## Requests <date>`, `### RQ<n> | <time> | <title>`; saves
pasted images and documents, long pastes, and files dragged in or named by `@path` outside the project to
`resources/<date>-<slug>/`; adds them to the manifest; opens the `.work/requests.md` block with `rev before` and `mode`.
Show its `warnings` in chat, once. Read every saved file in full. Then commit the `.work` repo: `record request on <topic>`.
Workspace files the prompt names inside the project are references, not attachments: read them, copy nothing.

## 2. Assess

0. New inputs: if the session start listed unprocessed files in `resources/`, process them first, as in the orch skill
   "New inputs in resources/" (once per session). A file that changes scope is asked before this request.
1. Read `.work/contract.md`, `model.md`, `glossary.md`, `claims.md`, `state.md`, `approvals.md` (Class table), and the
   artifacts the request names. `python3 $R context` shows the stage in progress and other open or deferred requests.
2. Conflict with a stage in progress (`stage in progress: true` and the request touches a file, claim or assumption of
   a brief not done, or contradicts its goal): say so in one line, then ask one AskUserQuestion: "Do RQ<n> first
   (Recommended)" or "After the stage". After: `python3 $R close RQ<n> --status deferred --summary "<why>"`, add it to
   `state.md` "Next actions" (`RQ<n> deferred until <stage> is done`), commit, and stop (step 5). The next `/orch`
   session runs deferred requests at its stage end. No conflict: say nothing about it.
3. Impact. Name every R-, N-, P-, A- and C-ID the request touches, the deliverables (DL-IDs) and the threads (T-IDs).
   - An agenda change (add, reorder, park, resume or drop a thread): apply it with `~/dotclaude/scripts/agenda.py`
     (`--by human --reason "<the human's words>"`) after the checks below; it needs no gates. Reorder, park, resume, a new
     thread inside the scope, or dropping a thread no R- or DL-ID needs: logged. Anything that adds or drops a requirement or
     deliverable is a scope change (next item) first. A new thread that is work to do now is also executed (step 3).
   - Changes the scope or a deliverable (adds, drops or reshapes a requirement or deliverable, its format or due date,
     or crosses an N-row): blocking card. `python3 $R raise RQ<n> --affects <IDs> --question "<one sentence?>" --reason
     "<line>" --scope-change | --deliverable-change`, commit, ask it now (`decisions.py compress D<n>`), record the
     answer (`decisions.py accept D<n> --option X`). A: the contract change (dated addendum pointer to `### RQ<n>` in
     BRIEF.md as the source line, `resources.py refresh resources/BRIEF.md --reason D<n>`, approvals Log line), then
     execute. B: execute within the approved contract only. C: close as `dropped`.
   - Anything else: the Class table decides. Model change after approval, definitions, lemma statements, design choices:
     checkpoint card (orch skill), provisional, continue. Main theorem statement: blocking. Wording, structure,
     typos, minor fixes, questions: logged or nothing.
   - A question that changes no file: answer it from the files (the `why` skill procedure when it names an ID), close
     as `answered`, go to step 4 without gates.
4. Classify what the change touches. `prose`: wording, structure, order, headings, exposition, remarks with no claim.
   `technical`: a definition, statement, proof, algorithm, the model, an assumption, a finding or an attack.
   Critical: a main result (main theorem in the contract or claims), a design, or a final deliverable (milestone or final). Mode: `default`, or what record
   detected from a `quick:` or `full:` prefix; a mode the human states otherwise overrides the default.

## 3. Execute

1. Gates: `python3 $R gates --kind <prose|technical> [--tex] [--critical] [--mode <mode>]`. It prints the brief's
   `- gates:` and `- critical:` lines. prose: G0, G1, G4. technical: G0 to G2 and G4, G3 if critical. quick: G0, G1.
   full: G0 to G4. G0 only when a `.tex` file changes. G5 only through a card from step 2.
2. One brief per artifact, from `.work/briefs/_template.md`, id `RQ<n>-<slug>`, `- stage: request RQ<n>`,
   `- request: RQ<n>`, gates and critical from step 1, acceptance criteria traced to the request (`BRIEF.md#RQ<n>`)
   and to R- or C-IDs. Tier per routing.md. Commit (`plan <change>`). `python3 $R set RQ<n> briefs=<id> gates="<gates>"`.
3. Dispatch the producer that owns the content (prose: `exposition-writer` or the producer of that section; statements:
   `theorem-writer`; proofs: `prover`; model: `modeler`; definitions: `property-writer`; design: `protocol-designer`;
   attacks: `attacker`; reports: `report-writer`). Never write the content yourself. Commit its output in the repo that
   holds it (paper and code: `repos.py commit`, a content message without workflow terms).
4. Run the gates of the brief, in order, exactly as in the orch skill work loop (step 7.3 to 7.6): write guard,
   `review_status.py` after every round, act on its last line, arbiters, escalation cards. `regression-checker` after
   every edit to LaTeX, pseudocode, `model.md` or `glossary.md` (review-gates, "Verified claims").
5. Claims: register new ones as `draft`; set statuses only as the gates earn them. Quick mode never raises a status.
   `python3 $R set RQ<n> claims=<C-IDs> decisions=<D-IDs>` as they arise.

## 4. Report

1. `claims.md` final statuses. `state.md`: `updated`, "Pending decisions", and under "Next actions" anything the
   request leaves open; the stage and playbook lines stay as they are. `decisions.md`: one entry
   `RQ<n> done: <title>` (`made by: human`, `class: logged`, `card: <D-IDs | none>`, reason: what was done).
   Write `state.md` last: the Stop hook treats claims and project changes newer than `state.md` as unrecorded.
2. `python3 $R close RQ<n> --status <done | answered | dropped> --summary "<one line>"`. It records the commits and
   changed files of both repos since `rev before`. Commit the `.work` repo: `update project state after <topic>`.
   The project repo is committed already (step 3.3); never commit workflow files there.
3. Packet in chat, at most 12 lines, plain language:
   - **Changed**: files and what changed in each; claims and their status now.
   - **Review**: gates run; issues found and how each was resolved; anything provisional (card IDs).
   - **Uncertain**: what is not proven, not checked (quick mode), or rests on a provisional decision. "None" if none.
   - **Commits**: both repos, short hashes.

## 5. Wait

End the turn. Never continue into playbook stages, the next brief or the next stage unless the human asks.
If a checkpoint card is provisional, say in the packet that it is asked at the next checkpoint, or now if they want.
