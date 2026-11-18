#!/usr/bin/env python3
"""Hooks for the research workflow. Usage: rw_hooks.py <event>, hook input JSON on stdin.

Events: session-start, prompt, pre-compact, stop, pre-tool-use, ask, post-agent, stop-failure, statusline.
Every hook does nothing unless $CLAUDE_PROJECT_DIR/.work/ exists (fallback: the input's cwd), except statusline,
which prints a status line in every project and caches context and usage-limit data for the other hooks.
Notifications: $RW_NOTIFY_CMD <title> <message> if set, else osascript on macOS.
bin/rw sets RW_LOOP=1 and RW_RUN=<id>; the Stop hook uses them to end a session after /handoff.
Internal errors fail open: exit 0 with no output, so a bug never blocks a session.
Stdlib only. Never reads or sets API keys.
"""
import hashlib
import json
import os
import re
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
# Roles that may write (create or overwrite) only inside one .work/ subdirectory.
SCOPED_WRITERS = {"summarizer": "packets"}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
# Context threshold for ending an orchestrator session: min(RW_CONTEXT_LIMIT, 60% of the window). See orch skill.
CONTEXT_LIMIT = int(os.environ.get("RW_CONTEXT_LIMIT", "300000"))
CONTEXT_FRACTION = 0.6
# Files under .work/ that hooks and scripts write automatically; they never count as unrecorded work.
AUTO_FILES = {"usage.tsv"}


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
        rel = p.relative_to(work)
        if (p.is_file() and not any(part.startswith(".") for part in rel.parts) and p != work / "state.md"
                and str(rel) not in AUTO_FILES):
            files[str(rel)] = file_hash(p)
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


def write_snapshot(inp, proj, why):
    """Snapshot handoff for work /handoff did not record. Returns the file path."""
    base = load_baseline(inp) or {}
    pending = unrecorded_work(inp, proj) or ([], [])
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    tag = "auto-precompact" if why == "compaction" else "auto-limit"
    out = proj / ".work" / "handoffs" / f"{ts}-{tag}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    commits, changed = pending
    status = git(proj, "status", "--porcelain") or "clean"
    out.write_text(
        f"# Snapshot handoff {ts} (automatic, before {why})\n\n"
        "Written by a hook, not by /handoff. The next orchestrator runs /handoff first; it folds this file in.\n\n"
        f"- session HEAD at start: {base.get('head') or 'none'}\n"
        f"- HEAD now: {git(proj, 'rev-parse', 'HEAD') or 'none'}\n\n"
        "## Commits this session\n\n" + ("\n".join(f"- {c}" for c in commits) or "- none") + "\n\n"
        "## .work files changed this session\n\n" + ("\n".join(f"- .work/{c}" for c in changed) or "- none") + "\n\n"
        "## git status --porcelain\n\n```\n" + status + "\n```\n")
    return out


def pre_compact(inp, proj):
    pending = unrecorded_work(inp, proj)
    if pending and inp.get("trigger") == "manual":
        sys.stderr.write(f"Research workflow: compaction blocked. This session made {describe(*pending)}, "
                         "but .work/state.md is unchanged. Run /handoff first, then /compact.\n")
        sys.exit(2)
    if pending:
        # Auto-compaction: never block (blocking a context-limit recovery fails the request). Write a snapshot instead.
        out = write_snapshot(inp, proj, "compaction")
        print(f"This is a research workflow session. A snapshot handoff was written to .work/handoffs/{out.name}. "
              "The summary must say: run /handoff first after compaction. Keep the active brief ID, the gate and round "
              "in progress, and every open issue ID.")
        return
    print("This is a research workflow session. Keep the active brief ID, the gate and round in progress, "
          "and every open issue ID in the summary.")


def end_marker(proj):
    try:
        return json.loads((proj / ".work" / ".rw" / "end.json").read_text())
    except (OSError, ValueError):
        return None


def mark_stopped(proj, data):
    p = proj / ".work" / ".rw" / "end.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dict(data, stopped=True)) + "\n")


def this_run(data):
    return data is not None and data.get("run") == os.environ.get("RW_RUN", "manual")


def last_human_prompt(transcript_path):
    """Text of the last user message typed by the human (not a tool result, not a meta message), or None."""
    try:
        lines = Path(transcript_path).read_text().splitlines()
    except (OSError, TypeError):
        return None
    for line in reversed(lines):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") != "user" or e.get("isMeta"):
            continue
        c = (e.get("message") or {}).get("content")
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
                continue
            texts = [x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text"]
            if texts:
                return "\n".join(texts)
    return None


def is_orch_turn(inp):
    t = last_human_prompt(inp.get("transcript_path"))
    return t is not None and bool(re.search(r"(^|\s|<command-name>)/orch\b", t.strip()))


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
              "session started. Run /handoff before stopping."})
        return
    end = end_marker(proj)
    if this_run(end):
        if not end.get("stopped"):
            mark_stopped(proj, end)  # bin/rw ends the session and acts on the outcome
        return
    if os.environ.get("RW_LOOP") and is_orch_turn(inp):
        emit({"decision": "block", "reason":
              "rw session: do not end the turn to ask the human or to wait. Ask with AskUserQuestion (decision card "
              "first) and continue. End the session only through /handoff (stage done, or context threshold). "
              "If you are blocked by an error you cannot resolve, run /handoff with outcome `error`."})


def pre_tool_use(inp, proj):
    role = str(inp.get("agent_type") or "")
    role = role[:-len("-mythos")] if role.endswith("-mythos") else role
    if inp.get("tool_name") not in WRITE_TOOLS or (role not in REVIEWERS and role not in SCOPED_WRITERS):
        return
    ti = inp.get("tool_input") or {}
    raw = ti.get("file_path") or ti.get("notebook_path") or ""
    target = Path(raw) if os.path.isabs(raw) else Path(inp.get("cwd") or proj) / raw
    target = Path(os.path.realpath(target))
    if role in SCOPED_WRITERS:
        scope = Path(os.path.realpath(proj / ".work" / SCOPED_WRITERS[role]))
        if scope in target.parents:
            return
        why = f"may only write in .work/{SCOPED_WRITERS[role]}/"
    else:
        issues = Path(os.path.realpath(proj / ".work" / "issues"))
        inside = issues in target.parents
        if inp.get("tool_name") == "Write" and inside and not target.exists():
            return
        why = ("may only create new files in .work/issues/" if not inside or inp.get("tool_name") != "Write"
               else "may not overwrite an existing file in .work/issues/")
    emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
          "permissionDecisionReason": f"Write guard: {role} {why}. Blocked: {raw}"}})


# Notifications, usage, context and limits

def notify(title, message):
    cmd = os.environ.get("RW_NOTIFY_CMD")
    try:
        if cmd:
            subprocess.run([cmd, title, message], timeout=5)
        elif sys.platform == "darwin":
            esc = lambda x: x.replace("\\", "\\\\").replace('"', '\\"')
            subprocess.Popen(["osascript", "-e",
                              f'display notification "{esc(message)}" with title "{esc(title)}" sound name "Glass"'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        pass


def status_cache_path(inp):
    sid = "".join(c for c in str(inp.get("session_id", "nosession")) if c.isalnum() or c in "-_")
    return STATE_DIR / f"{sid}.status.json"


def load_status(inp):
    try:
        return json.loads(status_cache_path(inp).read_text())
    except (OSError, ValueError):
        return {}


def context_tokens(st):
    """Tokens in the context window, from the cached statusline data. None if unknown."""
    cw = st.get("context_window") or {}
    cu = cw.get("current_usage") or {}
    if cu:
        return sum(int(cu.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    pct, size = cw.get("used_percentage"), cw.get("context_window_size")
    if pct is not None and size:
        return int(float(pct) * int(size) / 100)
    return None


def context_threshold(st):
    size = (st.get("context_window") or {}).get("context_window_size")
    return min(CONTEXT_LIMIT, int(CONTEXT_FRACTION * int(size))) if size else CONTEXT_LIMIT


def ask(inp, proj):
    qs = (inp.get("tool_input") or {}).get("questions") or []
    first = qs[0].get("question", "") if qs and isinstance(qs[0], dict) else ""
    more = f" (+{len(qs) - 1} more)" if len(qs) > 1 else ""
    notify(f"rw: input needed in {proj.name}", (first[:150] + more) or "A question is waiting.")


def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r is not None:
                return r
    return None


def post_agent(inp, proj):
    ti = inp.get("tool_input") or {}
    tokens = find_key(inp.get("tool_response"), "totalTokens")
    role = str(ti.get("subagent_type") or "general-purpose")
    m = re.search(r"\.work/briefs/([\w.-]+)\.md", str(ti.get("prompt") or ""))
    brief = m.group(1) if m else "none"
    stage_type = "other"
    if m:
        try:
            sm = re.search(r"^- stage type:\s*`?([\w-]+)", (proj / ".work" / "briefs" / f"{brief}.md").read_text(), re.M)
            stage_type = sm.group(1) if sm else "other"
        except OSError:
            pass
    if isinstance(tokens, (int, float)) and tokens > 0:
        sys.path.insert(0, str(DOTCLAUDE / "scripts"))
        import budgets
        budgets.log(proj, stage_type, brief, role, int(tokens), inp.get("session_id", "-"))
    st = load_status(inp)
    used = context_tokens(st)
    if used is not None and used >= context_threshold(st):
        emit({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
              f"Context threshold reached ({used // 1000}k tokens in context, threshold {context_threshold(st) // 1000}k). "
              "Do not start another dispatch or review round. Finish the bookkeeping of the current round "
              "(reports committed, review log row, review_status.py), then run /handoff with outcome `context`. "
              "bin/rw starts a fresh session that resumes from the files."}})


def reset_time(st):
    rl = st.get("rate_limits") or {}
    full = [w for w in rl.values() if isinstance(w, dict) and float(w.get("used_percentage") or 0) >= 99]
    pool = full or [w for k, w in rl.items() if k == "five_hour" and isinstance(w, dict)]
    times = [int(w["resets_at"]) for w in pool if w.get("resets_at")]
    return max(times) if times else None


def stop_failure(inp, proj):
    if inp.get("error") != "rate_limit":
        return
    snap = write_snapshot(inp, proj, "usage limit") if unrecorded_work(inp, proj) else None
    resets = reset_time(load_status(inp))
    data = {"run": os.environ.get("RW_RUN", "manual"), "outcome": "limit", "reason": "subscription usage limit",
            "resets_at": resets, "snapshot": snap.name if snap else None,
            "time": datetime.now().isoformat(timespec="seconds"), "stopped": True}
    p = proj / ".work" / ".rw" / "end.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data) + "\n")
    when = datetime.fromtimestamp(resets).strftime("%H:%M") if resets else "the reset"
    notify(f"rw: usage limit in {proj.name}", f"Paused. Resumes after {when}.")


def statusline(inp):
    """Print the status line and cache the input for the other hooks. Runs in every project."""
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        status_cache_path(inp).write_text(json.dumps(inp))
    except OSError:
        pass
    cw = inp.get("context_window") or {}
    pct = cw.get("used_percentage")
    model = (inp.get("model") or {}).get("display_name") or ""
    parts = [model] if model else []
    parts.append(f"ctx {int(float(pct))}%" if pct is not None else "ctx -")
    proj = project_dir(inp)
    st = proj / ".work" / "state.md"
    if st.is_file():
        m = re.search(r"^- stage:\s*(.+)$", st.read_text(), re.M)
        if m:
            parts.append(m.group(1).strip()[:40])
    print(" | ".join(parts))


EVENTS = {"session-start": session_start, "prompt": prompt, "pre-compact": pre_compact,
          "stop": stop, "pre-tool-use": pre_tool_use, "ask": ask, "post-agent": post_agent,
          "stop-failure": stop_failure, "statusline": statusline}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in EVENTS:
        sys.stderr.write(f"usage: rw_hooks.py {{{'|'.join(EVENTS)}}}\n")
        return 0
    try:
        inp = json.loads(sys.stdin.read() or "{}")
        if sys.argv[1] == "statusline":
            statusline(inp)
            return 0
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
