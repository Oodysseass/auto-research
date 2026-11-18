# D<n>

File name: `decisions/D<n>.md`. One card per question to the human, and per checkpoint decision taken provisionally.
The orchestrator writes it. `python3 ~/dotclaude/scripts/decisions.py` lints it, shows it in a dialog, and applies the answer
to `claims.md`, the briefs, `state.md` and `decisions.md`. No tokens, budgets, model tiers, effort levels, review round counts
or file formats in a card: those are never the human's decision.

- class: <blocking | checkpoint>  (from the Class table in approvals.md)
- status: <open | provisional | accepted | reversed>
- event: <the row of the Class table in approvals.md>
- header: <at most 12 characters, the dialog chip>
- question: <one sentence, ending with "?">
- recommendation: <option letter>
- reason: <one line: why the recommendation>
- depends: <C-IDs and A-IDs whose content depends on the answer | none>
- evidence: <pointers, semicolon-separated: resources/notes.md:24; .work/model.md#OP4; issue G1/conformance-reviewer/2>
- answer: <option letter | none>
- answered: <YYYY-MM-DD by human | none>

## Options

Two to four. Label: 1 to 5 words. Consequence: one line, what happens to the project if this option is chosen.

- A | <label> | <consequence>
- B | <label> | <consequence>
