# State

Updated by the orchestrator at the end of every session (`/handoff`). Read first by every new orchestrator.

- updated: <YYYY-MM-DD HH:MM>
- playbook: <name>
- stage: <stage number and name from the playbook>
- active brief: <briefs/<id>.md | none>
- project branch: <the project repo's current branch>
- revs at last handoff: <project>+<.work> (`repos.py rev`)
- last handoff: <handoffs/<timestamp>.md | none>

## Next actions

1. <action>

## Pending decisions

Cards in `.work/decisions/` that are `open` or `provisional` (`python3 ~/dotclaude/scripts/decisions.py list`).

- <D-ID, class, status, one-line question | none>

## Requeued

Briefs requeued by a reversed decision. Run them first.

- none
