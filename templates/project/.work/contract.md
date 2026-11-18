# Contract

Written by `/intake`. Binding for every agent. Changing it after approval needs human approval (see `approvals.md`).

## Project

- type: <client-security-review | client-design | new-paper | paper-revision | literature-review | proof-verification | open-ended>
- playbook: <playbook name, same as type unless stated>
- client or venue: <client name | venue name>
- format: <client report format | venue format, e.g. FC llncs splncs04, page limit>
- ai_tools_allowed: claude, codex

## Question or SoW summary

<Research question, or a summary of the SoW. One short paragraph. Point to the source file in `resources/`.>

## Requirements

Every requirement points to a line of `resources/BRIEF.md` (`resources/BRIEF.md:<line>`) or of the SoW
(`resources/<sow file>:<line>`, or page and section for a PDF). An instruction from me goes into the project brief first, under a dated heading.
The SoW governs scope. The project brief governs approach. I resolve any conflict between them, and the answer is added to the project brief.

| ID | Requirement | Source | Deliverable |
|---|---|---|---|
| R1 | <one line> | <resources/sow.pdf, p. 3, Sec. 2.1> | D1 |
| R2 | <one line> | <resources/BRIEF.md:14> | D1 |

## Scope

In scope:
- <item> (R-IDs)

Out of scope:
- <item>

## G1 checks

Explicit checks for the conformance reviewer, on every artifact. Taken from the project brief `resources/BRIEF.md`: research "Position" (P-IDs) and
"Not interested in" (N-IDs); client "Out of scope even if the SoW is vague" (N-IDs).

| ID | Check | Source |
|---|---|---|
| P1 | <the artifact does not contradict the expected answer without saying so and flagging it for me> | <resources/BRIEF.md:9> |
| N1 | <the artifact does not pursue: item> | <resources/BRIEF.md:30> |

## Deliverables

| ID | Deliverable | Covers | Milestone | Due |
|---|---|---|---|---|
| D1 | <report, paper section, proof, design doc> | R1, R2 | M1 | <YYYY-MM-DD> |

## Approval

- status: <pending | approved>
- approved by: <human>
- date: <YYYY-MM-DD>
- commit: <project>+<.work> (`repos.py rev`)
- changes since approval: <none | list with date and approval reference>
