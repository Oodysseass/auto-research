# Approval packets

One file per approval: `packets/<stage>.md`, written by the `summarizer` agent before the orchestrator asks for any approval.
The orchestrator shows the packet in chat, then asks. Checked by `python3 ~/dotclaude/scripts/check_packet.py <packet>`.
