#!/usr/bin/env python3
"""Mark the end of an orchestrator session for bin/rw. Stdlib only. Run by /handoff as its last step.

Usage: rw_end.py <outcome> <reason> [--root R]
outcome: stage-done (next stage in a fresh session) | context (same stage, fresh session) | project-done | error

Writes R/.work/.rw/end.json: {"run": $RW_RUN or "manual", "outcome", "reason", "time"}.
The Stop hook adds "stopped": true when the turn ends; bin/rw then ends the session and acts on the outcome.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

OUTCOMES = ("stage-done", "context", "project-done", "error", "limit")


def write(root, outcome, reason, **extra):
    p = Path(root) / ".work" / ".rw" / "end.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"run": os.environ.get("RW_RUN", "manual"), "outcome": outcome, "reason": reason,
            "time": datetime.now().isoformat(timespec="seconds"), **extra}
    p.write_text(json.dumps(data) + "\n")
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outcome", choices=OUTCOMES[:-1])
    ap.add_argument("reason")
    ap.add_argument("--root", default=".")
    a = ap.parse_args(argv)
    print(write(a.root, a.outcome, a.reason))
    return 0


if __name__ == "__main__":
    sys.exit(main())
