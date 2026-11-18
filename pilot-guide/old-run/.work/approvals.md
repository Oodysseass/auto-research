# Approvals

Events marked `yes` stop the workflow until I approve. The orchestrator lists them under "Open approvals" in `state.md`.
I loosen this file per project. Agents never edit the Policy table.

## Policy

| Event | Needs approval |
|---|---|
| Contract and playbook | yes |
| `model.md` | yes |
| Property and theorem statements, before proving starts | yes |
| Each milestone or final deliverable | yes |
| Any change to the contract or model after approval | yes |
| Deadlock unresolved by the arbiters | yes |
| Deleting or overwriting existing files | yes |
| Mythos escalation | no (log in `decisions.md`) |

## Log

Append-only. One line per granted or refused approval.

- <YYYY-MM-DD> | <event> | <artifact or file> | <approved | refused> | <commit> | <note>
- 2026-11-18 | Contract and playbook | .work/contract.md, new-paper trimmed (S1, S4, S7, S8, S11) | approved | 29c7db6 | approved at intake
