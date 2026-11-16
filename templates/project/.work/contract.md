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

Every requirement has a source. Source is a file and section in `resources/`, or `human: <date>` for an instruction from me.

| ID | Requirement | Source | Deliverable |
|---|---|---|---|
| R1 | <one line> | <resources/sow.pdf, Sec. 2.1> | D1 |

## Scope

In scope:
- <item> (R-IDs)

Out of scope:
- <item>

## Deliverables

| ID | Deliverable | Covers | Milestone | Due |
|---|---|---|---|---|
| D1 | <report, paper section, proof, design doc> | R1, R2 | M1 | <YYYY-MM-DD> |

## Approval

- status: <pending | approved>
- approved by: <human>
- date: <YYYY-MM-DD>
- commit: <hash>
- changes since approval: <none | list with date and approval reference>
