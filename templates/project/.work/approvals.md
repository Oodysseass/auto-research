# Approvals

Every question to me has a class. The orchestrator looks up the class here, writes a decision card
(`.work/decisions/D<n>.md`) for every blocking and checkpoint decision, and asks me inside the session with a dialog.
I loosen or tighten this file per project. Agents never edit the Class table.

Questions to me are about research content, scope and direction only. Anything that needs technical knowledge of the
system (tokens, budgets, model tiers, effort levels, review round counts, file formats) is decided by the system and logged.

## Classes

- `blocking`: ask now. The orchestrator writes the card, shows the approval packet if there is one, asks, and waits.
- `checkpoint`: proceed with the recommendation provisionally (`decisions.py provisional D<n>`). Dependent claims become
  `provisional`. Asked in a batch at the next checkpoint (end of stage, or before a blocking approval). Reversing it requeues
  the dependent work automatically.
- `logged`: decided by the orchestrator, no card. One `decisions.md` entry with `- class: logged`. Listed in the checkpoint digest.

## Class table

| Event | Class |
|---|---|
| Contract and playbook | blocking |
| Any change to the contract or the scope after approval | blocking |
| Main theorem statements, before proving starts | blocking |
| Each milestone or final deliverable | blocking |
| Deleting or overwriting existing files | blocking |
| Deadlock unresolved by the arbiters, on a main theorem | blocking |
| `model.md`, and model details after approval | checkpoint |
| Definitions and property statements | checkpoint |
| Lemma statements (not main theorems) | checkpoint |
| Design choices | checkpoint |
| Deadlock unresolved by the arbiters, other claims (the arbiter's recommended answer is taken provisionally) | checkpoint |
| A stalled review loop or a round limit, with a research question to settle | checkpoint |
| Routing, model tiers, Mythos escalation | logged |
| Retries and reruns | logged |
| Budget extensions | logged |
| Minor fixes | logged |

## Log

Append-only. One line per approval granted or refused, with the commit it applies to. The summarizer diffs from this commit.

- <YYYY-MM-DD> | <event> | <artifact or file> | <approved | refused> | <commit> | <D-ID or note>
