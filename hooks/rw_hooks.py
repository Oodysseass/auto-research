#!/usr/bin/env python3
"""Hooks for the research workflow. Usage: rw_hooks.py <event>, hook input JSON on stdin.

Events: session-start, prompt, pre-compact, stop, pre-tool-use.
Every hook does nothing unless $CLAUDE_PROJECT_DIR/.work/ exists (fallback: the input's cwd).
Internal errors fail open: exit 0 with no output, so a bug never blocks a session.
Stdlib only. Never reads or sets API keys.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

DOTCLAUDE = Path(__file__).resolve().parent.parent
RULES_CARD = DOTCLAUDE / "rules-card.md"
STATE_DIR = Path(os.environ.get("RW_HOOKS_STATE_DIR", Path(tempfile.gettempdir()) / "rw-hooks"))
STATE_LINES, HANDOFF_LINES = 80, 60

# Verifier roles (tier suffix stripped). Their only allowed file writes: new files in .work/issues/.
REVIEWERS = {
    "conformance-reviewer", "assumption-auditor", "proof-checker", "counterexample-hunter",
    "citation-verifier", "style-reviewer", "regression-checker", "arbiter",
}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def project_dir(inp):
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or inp.get("cwd") or os.getcwd())


def git(proj, *args):
    try:
        r = subprocess.run(["git", "-C", str(proj), *args], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def file_hash(p):
    try:
        return hashlib.sha1(p.read_bytes()).hexdigest()
    except OSError:
        return None


def snapshot(proj):
    """Fingerprint of the session-relevant state: HEAD, state.md, and every other file under .work/."""
    work = proj / ".work"
    files = {}
    for p in sorted(work.rglob("*")):
        if p.is_file() and not p.name.startswith(".") and p != work / "state.md":
            files[str(p.relative_to(work))] = file_hash(p)
    return {"head": git(proj, "rev-parse", "HEAD"), "state": file_hash(work / "state.md"), "work": files}


def baseline_path(inp):
    sid = "".join(c for c in str(inp.get("session_id", "nosession")) if c.isalnum() or c in "-_")
    return STATE_DIR / f"{sid}.json"


def load_baseline(inp):
    try:
        return json.loads(baseline_path(inp).read_text())
    except (OSError, ValueError):
        return None


def save_baseline(inp, proj):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    baseline_path(inp).write_text(json.dumps(snapshot(proj)))


def unrecorded_work(inp, proj):
    """Changes since session start that state.md does not reflect.
    Returns (commits, changed .work files) if HEAD moved or .work/ changed while state.md did not; else None."""
    base = load_baseline(inp)
    if base is None:
        return None
    now = snapshot(proj)
    if now["state"] != base["state"]:
        return None
    changed = sorted(k for k in set(now["work"]) | set(base["work"]) if now["work"].get(k) != base["work"].get(k))
    commits = []
    if base["head"] and now["head"] and now["head"] != base["head"]:
        log = git(proj, "log", "--oneline", f"{base['head']}..{now['head']}")
        commits = log.splitlines() if log else [now["head"][:7]]
    if not changed and not commits:
        return None
    return commits, changed


def describe(commits, changed):
    parts = []
    if commits:
        parts.append(f"{len(commits)} commit(s)")
    if changed:
        shown = ", ".join(f".work/{c}" for c in changed[:5])
        parts.append(f"edits to {shown}" + (f" and {len(changed) - 5} more" if len(changed) > 5 else ""))
    return " and ".join(parts)


def head_lines(p, n):
    try:
        lines = p.read_text().splitlines()
    except OSError:
        return None
    return "\n".join(lines[:n]) + (f"\n[... {len(lines) - n} more lines in {p}]" if len(lines) > n else "")


def latest_handoff(proj):
    d = proj / ".work" / "handoffs"
    files = sorted(p for p in d.glob("*.md") if p.name != "_template.md") if d.is_dir() else []
    return files[-1] if files else None


def emit(obj):
    print(json.dumps(obj))


# Events

def session_start(inp, proj):
    if load_baseline(inp) is None or inp.get("source") in ("startup", "clear"):
        save_baseline(inp, proj)
    parts = ["Research workflow project (.work/ present). Binding: .work/contract.md, model.md, glossary.md, claims.md, "
             "resources/BRIEF.md. Follow ~/.claude/rules-card.md."]
    if inp.get("source") == "compact":
        parts.append("Context was just compacted. Before any other work: if this session changed .work/ or committed, "
                     "run /handoff now. Then re-read .work/contract.md, model.md and glossary.md before producing anything.")
    st = head_lines(proj / ".work" / "state.md", STATE_LINES)
    if st:
        parts.append("## .work/state.md\n" + st)
    ho = latest_handoff(proj)
    if ho:
        parts.append(f"## Latest handoff: .work/handoffs/{ho.name}\n" + head_lines(ho, HANDOFF_LINES))
    emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n\n".join(parts)}})


def prompt(inp, proj):
    card = RULES_CARD.read_text()
    emit({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": card}})


def pre_compact(inp, proj):
    pending = unrecorded_work(inp, proj)
    if pending and inp.get("trigger") == "manual":
        sys.stderr.write(f"Research workflow: compaction blocked. This session made {describe(*pending)}, "
                         "but .work/state.md is unchanged. Run /handoff first, then /compact.\n")
        sys.exit(2)
    if pending:
        # Auto-compaction: never block (blocking a context-limit recovery fails the request). Write a snapshot instead.
        base = load_baseline(inp) or {}
        ts = datetime.now().strftime("%Y%m%d-%H%M")
        out = proj / ".work" / "handoffs" / f"{ts}-auto-precompact.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        commits, changed = pending
        status = git(proj, "status", "--porcelain") or "clean"
        out.write_text(
            f"# Snapshot handoff {ts} (automatic, before auto-compaction)\n\n"
            "Written by the PreCompact hook, not by /handoff. Run /handoff now; it folds this file in.\n\n"
            f"- session HEAD at start: {base.get('head') or 'none'}\n"
            f"- HEAD now: {git(proj, 'rev-parse', 'HEAD') or 'none'}\n\n"
            "## Commits this session\n\n" + ("\n".join(f"- {c}" for c in commits) or "- none") + "\n\n"
            "## .work files changed this session\n\n" + ("\n".join(f"- .work/{c}" for c in changed) or "- none") + "\n\n"
            "## git status --porcelain\n\n```\n" + status + "\n```\n")
        print(f"This is a research workflow session. A snapshot handoff was written to .work/handoffs/{out.name}. "
              "The summary must say: run /handoff first after compaction. Keep the active brief ID, the gate and round "
              "in progress, and every open issue ID.")
        return
    print("This is a research workflow session. Keep the active brief ID, the gate and round in progress, "
          "and every open issue ID in the summary.")


def stop(inp, proj):
    if inp.get("stop_hook_active"):
        return
    if load_baseline(inp) is None:
        # .work/ appeared during the session (e.g. /intake), or the baseline was lost. Start tracking now.
        save_baseline(inp, proj)
        return
    pending = unrecorded_work(inp, proj)
    if pending:
        emit({"decision": "block", "reason":
              f"Research workflow: this session made {describe(*pending)}, but .work/state.md is unchanged since the "
              "session started. Run /handoff before stopping. If you are pausing mid-stage for the human, update "
              ".work/state.md (Next actions, Open approvals) instead."})


def pre_tool_use(inp, proj):
    role = str(inp.get("agent_type") or "")
    role = role[:-len("-mythos")] if role.endswith("-mythos") else role
    if role not in REVIEWERS or inp.get("tool_name") not in WRITE_TOOLS:
        return
    ti = inp.get("tool_input") or {}
    raw = ti.get("file_path") or ti.get("notebook_path") or ""
    target = Path(raw) if os.path.isabs(raw) else Path(inp.get("cwd") or proj) / raw
    target = Path(os.path.realpath(target))
    issues = Path(os.path.realpath(proj / ".work" / "issues"))
    inside = issues in target.parents
    if inp.get("tool_name") == "Write" and inside and not target.exists():
        return
    why = ("may only create new files in .work/issues/" if not inside or inp.get("tool_name") != "Write"
           else "may not overwrite an existing file in .work/issues/")
    emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
          "permissionDecisionReason": f"Reviewer write guard: {role} {why}. Blocked: {raw}"}})


EVENTS = {"session-start": session_start, "prompt": prompt, "pre-compact": pre_compact,
          "stop": stop, "pre-tool-use": pre_tool_use}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in EVENTS:
        sys.stderr.write(f"usage: rw_hooks.py {{{'|'.join(EVENTS)}}}\n")
        return 0
    try:
        inp = json.loads(sys.stdin.read() or "{}")
        proj = project_dir(inp)
        if not (proj / ".work").is_dir():
            return 0
        EVENTS[sys.argv[1]](inp, proj)
    except SystemExit:
        raise
    except Exception as e:  # fail open
        if os.environ.get("RW_HOOKS_DEBUG"):
            raise
        sys.stderr.write(f"rw_hooks: internal error ignored: {e}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
