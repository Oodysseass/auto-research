#!/usr/bin/env python3
"""Raw inputs for /wstatus in one call, so the skill never composes shell pipelines. Stdlib only. Read-only.

Usage (run from the project root, or pass --root):
  wstatus.py
Prints one section per source, each headed `## <name>`: state, agenda, approvals log, latest handoff, claims (count per
status), ideas (open ideas and questions), pending captures, decisions, issues (review_status.py --all: every artifact and legacy file), requests, repos, resources.
A source that fails prints its output and `(exit N)` in its section; the other sections still run. Always exits 0 unless the root has no .work/ (2).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def script(root, name, *args):
    try:
        r = subprocess.run([sys.executable, str(SCRIPTS / name), *args], cwd=root, capture_output=True, text=True,
                           timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return f"(failed: {e})"
    out = (r.stdout + r.stderr).rstrip()
    return out + (f"\n(exit {r.returncode})" if r.returncode else "")


def section(name, body):
    print(f"## {name}\n{body.rstrip() or '(empty)'}\n")


def approvals_log(root):
    try:
        text = (root / ".work" / "approvals.md").read_text()
    except OSError:
        return "(no .work/approvals.md)"
    m = re.search(r"(?ms)^## Log\s*$(.*?)(?=^## |\Z)", text)
    return m.group(1).strip() if m else "(no Log section)"


def latest_handoff(root):
    d = root / ".work" / "handoffs"
    files = sorted(p.name for p in d.glob("*.md") if p.name != "_template.md") if d.is_dir() else []
    return files[-1] if files else "none"


def open_ideas(root):
    try:
        text = (root / ".work" / "ideas.md").read_text()
    except OSError:
        return "(no .work/ideas.md)"
    found = re.findall(r"(?m)^## (I\d+) \| (\S+) \| open\s*\n- text: (.*)$", text)
    return "\n".join(f"{i} ({k}): {t}" for i, k, t in found) or "none"


def claims_by_status(root):
    sys.path.insert(0, str(SCRIPTS))
    import review_status
    counts = {}
    for c in review_status.parse_claims(root / ".work" / "claims.md").values():
        st = c.get("status", "missing")
        counts[st] = counts.get(st, 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "none"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    root = Path(ap.parse_args(argv).root).resolve()
    if not (root / ".work").is_dir():
        print(f"wstatus: no .work/ in {root}: run from the project root", file=sys.stderr)
        return 2
    try:
        state = (root / ".work" / "state.md").read_text()
    except OSError:
        state = "(no .work/state.md)"
    section("state", state)
    section("agenda", script(root, "agenda.py", "list"))
    section("approvals log", approvals_log(root))
    section("latest handoff", latest_handoff(root))
    section("claims", claims_by_status(root))
    section("ideas", open_ideas(root))
    section("pending captures", script(root, "capture.py", "pending"))
    section("decisions", script(root, "decisions.py", "list"))
    issues = root / ".work" / "issues"
    section("issues", script(root, "review_status.py", str(issues), "--all") if issues.is_dir() else "(no .work/issues/)")
    section("requests", script(root, "request.py", "list", "-n", "5"))
    section("repos", script(root, "repos.py", "check"))
    section("resources", script(root, "resources.py", "scan"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
