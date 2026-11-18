# Contract

Written by `/intake`. Binding for every agent. Changing it after approval needs human approval (see `approvals.md`).

## Project

- type: new-paper
- playbook: new-paper, trimmed (stages S1, S4, S7, S8, S11 only; see `state.md`)
- client or venue: none (internal pilot)
- format: LaTeX `llncs`, one file `paper/lemmas.tex` with a `paper/main.tex` wrapper
- ai_tools_allowed: claude, codex

## Question or SoW summary

In the model of `resources/notes.md` (section "Model"), do Lemma 1 (Chain growth) and Lemma 2 (Bounded honest spread) of
`resources/notes.md` (section "Statements") hold, exactly as stated? Each lemma is settled by a pen-and-paper proof or by an
explicit counterexample execution in the model. Source: `resources/BRIEF.md:7`.

Main result: **Lemma 1 (Chain growth)** (`resources/BRIEF.md:24`, `resources/notes.md:40`). Lemma 2 is auxiliary.

## Requirements

| ID | Requirement | Source | Deliverable |
|---|---|---|---|
| R1 | **Main.** Settle Lemma 1 (Chain growth) as stated in `resources/notes.md:40`: a proof that passes the gates, or an explicit counterexample execution in the model. | resources/BRIEF.md:7, resources/BRIEF.md:17, resources/BRIEF.md:24 | D1, D2 |
| R2 | Settle Lemma 2 (Bounded honest spread) as stated in `resources/notes.md:42`: a proof that passes the gates, or an explicit counterexample execution in the model. | resources/BRIEF.md:7, resources/BRIEF.md:17 | D1, D2 |
| R3 | Use the model of `resources/notes.md`, section "Model", without changes. | resources/BRIEF.md:23 | D1 |
| R4 | Use the statements exactly as in `resources/notes.md`, section "Statements". No rewording that changes meaning. | resources/BRIEF.md:24 | D1 |
| R5 | A refuted lemma stays in the document as stated, with its counterexample. It is never weakened silently. | resources/BRIEF.md:18 | D1, D2 |
| R6 | Neither lemma is used in the proof of the other. | resources/notes.md:44, resources/BRIEF.md:24 | D1 |
| R7 | Output is LaTeX in `llncs` format: `paper/lemmas.tex` with a `paper/main.tex` wrapper. | resources/BRIEF.md:35 | D1 |
| R8 | Final verdict per lemma is its status in `.work/claims.md` (`verified` or `refuted`). No separate verdict report. | resources/BRIEF.md:52 | D2 |
| R9 | Codex runs G3 on Lemma 1 and on the final deliverable. | resources/BRIEF.md:50 | D1 |

## Scope

In scope:
- Formalising the model of `resources/notes.md` as A-IDs in `model.md` (R3)
- Stating both lemmas in LaTeX, verbatim in meaning (R4)
- A proof or a counterexample execution for each lemma (R1, R2, R5, R6)
- Review through the gates; final claim statuses (R8, R9)

Out of scope:
- Literature review, related work, citations
- New protocols or any change to the protocol or model
- Probabilistic bounds
- Attacks beyond a counterexample that refutes a lemma
- Introduction, exposition, abstract, or a full paper

## G1 checks

| ID | Check | Source |
|---|---|---|
| P1 | The artifact does not contradict the expected answer (both lemmas hold) without saying so explicitly and flagging it for the human. A refutation of either lemma is flagged, not buried. | resources/BRIEF.md:11, resources/BRIEF.md:13 |
| P2 | Any argument that relies on "every honest party sees every honest chain within one round" cites the specific model assumptions (A-IDs) it uses, and does not assume more than the network rules of the model give. | resources/BRIEF.md:12 |
| N1 | The artifact does not contain or pursue a literature review. | resources/BRIEF.md:39 |
| N2 | The artifact does not propose new protocols or change the protocol of `resources/notes.md`. | resources/BRIEF.md:41 |
| N3 | The artifact does not state or prove probabilistic bounds: both lemmas are about every execution. | resources/BRIEF.md:42 |
| N4 | The artifact does not contain attacks beyond what is needed to refute a lemma. | resources/BRIEF.md:43 |
| N5 | The artifact contains no introduction, exposition or full-paper structure. | resources/BRIEF.md:44 |

## Deliverables

| ID | Deliverable | Covers | Milestone | Due |
|---|---|---|---|---|
| D1 | `paper/lemmas.tex` (+ `paper/main.tex` wrapper, `llncs`): both statements, each with a proof or a counterexample execution | R1, R2, R3, R4, R5, R6, R7, R9 | M1 | none |
| D2 | Final statuses of both lemmas in `.work/claims.md` | R1, R2, R5, R8 | M1 | none |

## Approval

- status: approved
- approved by: human
- date: 2026-11-18
- commit: 29c7db6
- changes since approval: none
