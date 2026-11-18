# Decisions

Append-only. Never edit or delete an entry. Correct a decision with a new entry that references the old one.
`made by` is `human` or an agent name. `class` is from the Class table in `approvals.md`.
`card` is the D-ID of the decision card, `none` for logged decisions. `routing` is filled only for model and effort routing.
Entries for cards are written by `decisions.py`. Logged decisions are written by the orchestrator and listed in the checkpoint digest.

## <YYYY-MM-DD> | <decision in one line>
- made by: <human | agent name>
- class: <blocking | checkpoint | logged>
- card: <D-ID | none>
- reason: <one line>
- routing: <model, effort | n/a>
