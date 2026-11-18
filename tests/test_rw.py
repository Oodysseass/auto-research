import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RW = ROOT / "bin" / "rw"

FAKE = r'''#!/usr/bin/env python3
"""Fake claude for rw tests. Reads the outcome plan from $FAKE_PLAN (comma-separated), one per call."""
import json, os, sys, time
from pathlib import Path
log = Path(os.environ["FAKE_LOG"])
calls = log.read_text().splitlines() if log.exists() else []
n = len(calls)
log.write_text("\n".join(calls + [json.dumps({"argv": sys.argv[1:], "loop": os.environ.get("RW_LOOP"),
                                              "run": os.environ.get("RW_RUN")})]) + "\n")
plan = os.environ["FAKE_PLAN"].split(",")
step = plan[n] if n < len(plan) else "quit"
if step == "quit":
    sys.exit(0)
end = Path(".work/.rw/end.json")
end.parent.mkdir(parents=True, exist_ok=True)
data = {"run": os.environ["RW_RUN"], "outcome": step, "reason": f"step {n}", "stopped": True}
Path(".work/state.md").write_text(f"# State\n\n- stage: {os.environ.get('FAKE_STAGES', '').split(',')[n] if os.environ.get('FAKE_STAGES') else 'x'}\n")
if step == "limit":
    data["resets_at"] = int(time.time()) - 120
end.write_text(json.dumps(data))
time.sleep(30)  # the session stays open until rw ends it
'''


@pytest.fixture
def setup(tmp_path):
    proj = tmp_path / "proj"
    (proj / ".work").mkdir(parents=True)
    (proj / ".work/state.md").write_text("# State\n")
    fake = tmp_path / "claude"
    fake.write_text(FAKE)
    fake.chmod(0o755)
    notes = tmp_path / "notes.txt"
    notifier = tmp_path / "notify.sh"
    notifier.write_text(f'#!/bin/sh\nprintf "%s | %s\\n" "$1" "$2" >> "{notes}"\n')
    notifier.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("RW_", "FAKE_"))}
    env.update(RW_CLAUDE=str(fake), RW_NOTIFY_CMD=str(notifier), RW_POLL="0.1", FAKE_LOG=str(tmp_path / "calls"),
               RW_BUDGETS=str(tmp_path / "budgets.json"), RW_USAGE_GLOBAL=str(tmp_path / "g.tsv"))
    return proj, env, tmp_path


def rw(proj, env, plan, *args, timeout=60):
    t0 = time.time()
    r = subprocess.run([sys.executable, str(RW), *args], cwd=proj, env=dict(env, FAKE_PLAN=plan),
                       capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    return r, time.time() - t0


def calls(tmp):
    p = tmp / "calls"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def test_loops_until_project_done(setup):
    proj, env, tmp = setup
    r, took = rw(proj, env, "stage-done,context,project-done", "--permission-mode", "plan")
    assert r.returncode == 0, r.stdout + r.stderr
    c = calls(tmp)
    assert len(c) == 3 and took < 25  # every session was ended by rw, not by the 30 s sleep
    assert c[0]["argv"] == ["--model", "claude-opus-5-5", "--effort", "high", "--permission-mode", "plan", "/orch"]
    assert all(x["loop"] == "1" for x in c) and len({x["run"] for x in c}) == 3
    assert "done" in (tmp / "notes.txt").read_text()


def test_stops_on_error_with_notification(setup):
    proj, env, tmp = setup
    r, _ = rw(proj, env, "stage-done,error")
    assert r.returncode == 1 and len(calls(tmp)) == 2
    assert "stopped" in (tmp / "notes.txt").read_text()


def test_stops_when_human_quits(setup):
    proj, env, tmp = setup
    r, _ = rw(proj, env, "quit")
    assert r.returncode == 0 and "without a handoff" in r.stdout and len(calls(tmp)) == 1


def test_limit_waits_then_resumes(setup):
    proj, env, tmp = setup
    r, _ = rw(proj, env, "limit,project-done")
    assert r.returncode == 0, r.stdout
    assert len(calls(tmp)) == 2
    assert "usage limit" in (tmp / "notes.txt").read_text() and "Resumes at" in r.stdout


def test_stale_marker_is_ignored(setup):
    proj, env, tmp = setup
    (proj / ".work/.rw").mkdir()
    (proj / ".work/.rw/end.json").write_text(json.dumps({"run": "old", "outcome": "stage-done", "stopped": True}))
    r, _ = rw(proj, env, "quit")
    assert "without a handoff" in r.stdout


def test_refuses_outside_project(setup, tmp_path):
    _, env, _ = setup
    r = subprocess.run([sys.executable, str(RW)], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert r.returncode == 2 and "no .work/state.md" in r.stderr


def test_stop_before_stage(setup):
    proj, env, tmp = setup
    env = dict(env, FAKE_STAGES="4 (S7 Statements),5 (S8 Proofs)")
    r, _ = rw(proj, env, "stage-done,stage-done,project-done", "--stop-before", "S8")
    assert r.returncode == 0 and "stopped before S8" in r.stdout
    assert len(calls(tmp)) == 2
    assert all("--stop-before" not in c["argv"] for c in calls(tmp))
    (tmp / "calls").unlink()
    (proj / ".work/state.md").write_text("# State\n\n- stage: 6 (S80 other)\n")
    r, _ = rw(proj, dict(env, FAKE_STAGES="x"), "project-done", "--stop-before", "S8")
    assert "project done" in r.stdout
