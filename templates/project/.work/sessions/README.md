# Sessions

One file per captured conversation: `<YYYYMMDD-HHMM>-<session>.md`, a one-page summary written by
`~/dotclaude/scripts/capture.py summary` after the capture dialog.
`<...>-stub.md`: a session that ended without a capture (SessionEnd hook). The next session offers the capture dialog
from its transcript, then marks the stub captured.
