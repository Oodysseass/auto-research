import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "hooks" / "rw_hooks.py"


@pytest.fixture
def proj(tmp_path):
    p = tmp_path / "proj"
    (p / ".work" / "briefs").mkdir(parents=True)
    (p / ".work" / "state.md").write_text("# State\n\n- stage: 2 (S4 Model)\n")
    (p / ".work" / "briefs" / "S4-model.md").write_text("# Brief S4-model\n\n- stage type: model\n")
    (p / "paper").mkdir()
    (p / "paper" / "main.tex").write_text("x\n")
    subprocess.run(["git", "init", "-q", str(p)], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "repos.py"), "--root", str(p), "init"], check=True,
                   capture_output=True)
    for repo in (p, p / ".work"):
        commit(repo, "init")
    return p


def commit(repo, msg):
    g = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(g + ["add", "-A"], check=True)
    subprocess.run(g + ["commit", "-qm", msg], check=True)


@pytest.fixture
def env(tmp_path, proj):
    notes = tmp_path / "notes.txt"
    notifier = tmp_path / "notify.sh"
    notifier.write_text(f'#!/bin/sh\nprintf "%s | %s\\n" "$1" "$2" >> "{notes}"\n')
    notifier.chmod(0o755)
    e = {k: v for k, v in os.environ.items() if not k.startswith("RW_")}
    e.update(CLAUDE_PROJECT_DIR=str(proj), RW_HOOKS_STATE_DIR=str(tmp_path / "state"), RW_NOTIFY_CMD=str(notifier),
             RW_USAGE_GLOBAL=str(tmp_path / "global.tsv"), RW_HOOKS_DEBUG="1")
    e["_notes"] = str(notes)
    return e


def hook(env, event, inp, **extra):
    e = dict(env, **extra)
    r = subprocess.run([sys.executable, str(HOOK), event], input=json.dumps(inp), capture_output=True, text=True, env=e)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout) if r.stdout.strip().startswith("{") else r.stdout


def transcript(tmp_path, *entries):
    p = tmp_path / "t.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return str(p)


def user(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def tool_result():
    return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}}


def notes(env):
    p = Path(env["_notes"])
    return p.read_text() if p.exists() else ""


def start(env, sid="s1"):
    hook(env, "session-start", {"session_id": sid, "source": "startup"})


def test_stop_blocks_orch_turn_in_rw_loop(tmp_path, env):
    start(env)
    t = transcript(tmp_path, user("<command-name>/orch</command-name>"), tool_result())
    out = hook(env, "stop", {"session_id": "s1", "transcript_path": t}, RW_LOOP="1", RW_RUN="r1")
    assert out["decision"] == "block" and "AskUserQuestion" in out["reason"]


def test_stop_allows_human_turn_and_non_rw_sessions(tmp_path, env):
    start(env)
    t = transcript(tmp_path, user("/orch"), user("why is C3 provisional?"))
    assert hook(env, "stop", {"session_id": "s1", "transcript_path": t}, RW_LOOP="1", RW_RUN="r1") == ""
    t = transcript(tmp_path, user("/orch"))
    assert hook(env, "stop", {"session_id": "s1", "transcript_path": t}) == ""
    t = transcript(tmp_path, user("/orch"))
    assert hook(env, "stop", {"session_id": "s1", "transcript_path": t, "stop_hook_active": True},
                RW_LOOP="1", RW_RUN="r1") == ""


def test_stop_after_handoff_marks_end(tmp_path, env, proj):
    start(env)
    (proj / ".work/.rw").mkdir()
    (proj / ".work/.rw/end.json").write_text(json.dumps({"run": "r1", "outcome": "stage-done", "reason": "S4 done"}))
    t = transcript(tmp_path, user("/orch"))
    assert hook(env, "stop", {"session_id": "s1", "transcript_path": t}, RW_LOOP="1", RW_RUN="r1") == ""
    assert json.loads((proj / ".work/.rw/end.json").read_text())["stopped"] is True


def test_stop_ignores_marker_of_other_run(tmp_path, env, proj):
    start(env)
    (proj / ".work/.rw").mkdir()
    (proj / ".work/.rw/end.json").write_text(json.dumps({"run": "old", "outcome": "stage-done"}))
    t = transcript(tmp_path, user("/orch"))
    out = hook(env, "stop", {"session_id": "s1", "transcript_path": t}, RW_LOOP="1", RW_RUN="r1")
    assert out["decision"] == "block"


def test_auto_files_are_not_unrecorded_work(tmp_path, env, proj):
    start(env)
    (proj / ".work/usage.tsv").write_text("x\n")
    (proj / ".work/.rw").mkdir()
    (proj / ".work/.rw/end.json").write_text("{}")
    assert hook(env, "stop", {"session_id": "s1"}) == ""
    (proj / ".work/claims.md").write_text("x\n")
    assert hook(env, "stop", {"session_id": "s1"})["decision"] == "block"


def status(env, sid, **cw):
    hook(env, "statusline", {"session_id": sid, "cwd": env["CLAUDE_PROJECT_DIR"], "context_window": cw,
                             "rate_limits": cw.pop("rate_limits", {})})


def agent_call(tokens=12345, prompt="Brief: .work/briefs/S4-model.md"):
    return {"session_id": "s1", "tool_name": "Agent", "tool_input": {"subagent_type": "modeler", "prompt": prompt},
            "tool_response": {"content": [], "totalTokens": tokens, "usage": {"input_tokens": 1}}}


def test_post_agent_logs_usage(env, proj, tmp_path):
    assert hook(env, "post-agent", agent_call()) == ""
    rows = (proj / ".work/usage.tsv").read_text().splitlines()
    assert rows[1].split("\t")[2:] == ["model", "S4-model", "modeler", "12345"]
    assert (tmp_path / "global.tsv").exists()


def test_post_agent_context_threshold(env):
    status(env, "s1", context_window_size=1000000, current_usage={"input_tokens": 10, "cache_read_input_tokens": 100000})
    assert hook(env, "post-agent", agent_call()) == ""
    status(env, "s1", context_window_size=1000000, current_usage={"input_tokens": 10, "cache_read_input_tokens": 320000})
    out = hook(env, "post-agent", agent_call())
    assert "/handoff with outcome `context`" in out["hookSpecificOutput"]["additionalContext"]
    status(env, "s1", context_window_size=200000, used_percentage=65)  # 130k > 60% of 200k
    assert "additionalContext" in hook(env, "post-agent", agent_call())["hookSpecificOutput"]


def test_ask_notifies(env):
    hook(env, "ask", {"session_id": "s1", "tool_name": "AskUserQuestion",
                      "tool_input": {"questions": [{"question": "D1: Approve the model?"}, {"question": "D2: x?"}]}})
    n = notes(env)
    assert "input needed" in n and "D1: Approve the model? (+1 more)" in n


def test_stop_failure_rate_limit(env, proj):
    start(env)
    reset = int(time.time()) + 3600
    status(env, "s1", used_percentage=10, rate_limits={"five_hour": {"used_percentage": 100, "resets_at": reset},
                                                        "seven_day": {"used_percentage": 40, "resets_at": reset + 99999}})
    (proj / ".work/claims.md").write_text("changed\n")
    hook(env, "stop-failure", {"session_id": "s1", "error": "rate_limit"}, RW_RUN="r9")
    d = json.loads((proj / ".work/.rw/end.json").read_text())
    assert (d["run"], d["outcome"], d["resets_at"], d["stopped"]) == ("r9", "limit", reset, True)
    assert d["snapshot"] and (proj / ".work/handoffs" / d["snapshot"]).exists()
    assert "usage limit" in notes(env)
    hook(env, "stop-failure", {"session_id": "s1", "error": "server_error"}, RW_RUN="r10")
    assert json.loads((proj / ".work/.rw/end.json").read_text())["run"] == "r9"


def test_statusline_without_work_dir(env, tmp_path):
    out = hook(dict(env, CLAUDE_PROJECT_DIR=str(tmp_path)), "statusline",
               {"session_id": "s2", "cwd": str(tmp_path), "model": {"display_name": "Opus 5.5"},
                "context_window": {"used_percentage": 42.7}})
    assert out.strip() == "Opus 5.5 | ctx 42%"


def test_statusline_shows_stage(env):
    out = hook(env, "statusline", {"session_id": "s3", "context_window": {}})
    assert out.strip() == "ctx - | 2 (S4 Model)"


def guard(env, proj, role, path, tool="Write"):
    return hook(env, "pre-tool-use", {"agent_type": role, "tool_name": tool, "cwd": str(proj),
                                      "tool_input": {"file_path": str(proj / path)}})


def test_summarizer_write_scope(env, proj):
    assert guard(env, proj, "summarizer", ".work/packets/S4.md") == ""
    assert guard(env, proj, "summarizer", ".work/packets/S4.md", "Edit") == ""
    out = guard(env, proj, "summarizer", "paper/lemmas.tex")
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    out = guard(env, proj, "proof-checker", ".work/packets/S4.md")
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert guard(env, proj, "proof-checker-mythos", ".work/issues/new.json") == ""


def test_stop_sees_commits_in_both_repos(tmp_path, env, proj):
    start(env)
    (proj / "paper" / "main.tex").write_text("y\n")
    commit(proj, "add proof of lemma 1")
    out = hook(env, "stop", {"session_id": "s1"})
    assert out["decision"] == "block" and "1 commit(s)" in out["reason"]
    hook(env, "session-start", {"session_id": "s2", "source": "startup"})
    (proj / ".work" / "briefs" / "S4-model.md").write_text("changed\n")
    commit(proj / ".work", "plan model")
    out = hook(env, "stop", {"session_id": "s2"})
    assert out["decision"] == "block" and "1 commit(s)" in out["reason"]
    (proj / ".work" / "state.md").write_text("# State\n\n- stage: 3\n")
    commit(proj / ".work", "update project state after model")
    assert hook(env, "stop", {"session_id": "s2"}) == ""


def test_precompact_snapshot_lists_both_repos(tmp_path, env, proj):
    start(env)
    (proj / ".work" / "claims.md").write_text("changed\n")
    (proj / "paper" / "main.tex").write_text("z\n")
    out = hook(env, "pre-compact", {"session_id": "s1", "trigger": "auto"})
    assert "snapshot handoff" in out
    snap = next((proj / ".work" / "handoffs").glob("*-auto-precompact.md")).read_text()
    assert " M paper/main.tex" in snap and "?? .work/claims.md" in snap


def push(env, proj, cmd):
    return hook(env, "pre-tool-use", {"tool_name": "Bash", "cwd": str(proj), "tool_input": {"command": cmd}})


def test_push_guard(env, proj):
    for cmd in ("git push origin work/S4-model", "git push --all", "git -C .work push", "cd .work && git push",
                "git push -u origin workflow-migration", "git push origin HEAD:refs/heads/work/x"):
        out = push(env, proj, cmd)
        assert out["hookSpecificOutput"]["permissionDecision"] == "deny", cmd
    assert push(env, proj, "git push origin main") == ""
    assert push(env, proj, "git status") == ""
    subprocess.run(["git", "-C", str(proj), "checkout", "-qb", "work/S8-proofs"], check=True)
    assert push(env, proj, "git push")["hookSpecificOutput"]["permissionDecision"] == "deny"
