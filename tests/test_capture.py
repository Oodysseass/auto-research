import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CAP = ROOT / "scripts" / "capture.py"


def run(root, *args):
    return subprocess.run([sys.executable, str(CAP), "--root", str(root), *args], capture_output=True, text=True)


@pytest.fixture
def root(tmp_path):
    (tmp_path / ".work").mkdir()
    (tmp_path / ".work" / "decisions.md").write_text("# Decisions\n")
    (tmp_path / ".work" / "deadends.md").write_text("# Dead ends\n")
    return tmp_path


def test_ideas_and_status(root):
    assert run(root, "idea", "--text", "use quorum certificates | maybe", "--session", "abc-123").stdout.strip() == "I1"
    assert run(root, "idea", "--text", "does liveness need GST?", "--kind", "question").stdout.strip() == "I2"
    assert run(root, "set", "I1", "status=pursued", "note=became T7").returncode == 0
    t = (root / ".work" / "ideas.md").read_text()
    assert "## I1 | idea | pursued" in t and "became T7" in t and "## I2 | question | open" in t
    assert "quorum certificates / maybe" in t and "session abc123" in t
    assert run(root, "set", "I1", "status=maybe").returncode == 2
    assert run(root, "set", "I9", "status=open").returncode == 2


def test_deadend_and_decision(root):
    run(root, "deadend", "--what", "reduce to Dolev-Strong", "--why", "needs signatures", "--ref", "I1")
    run(root, "decision", "--title", "keep 100 percent overlap as the main case", "--reason", "SoW scope")
    assert "| reduce to Dolev-Strong | needs signatures | I1" in (root / ".work" / "deadends.md").read_text()
    d = (root / ".work" / "decisions.md").read_text()
    assert "keep 100 percent overlap" in d and "- made by: human" in d and "- class: logged" in d


def test_stub_pending_and_summary(root, tmp_path):
    assert run(root, "captured", "--session", "s-1").returncode == 1
    stub = run(root, "stub", "--session", "s-1", "--transcript", "/t/x.jsonl").stdout.strip()
    p = json.loads(run(root, "pending", "--json").stdout)
    assert len(p) == 1 and p[0]["transcript"] == "/t/x.jsonl"
    f = tmp_path / "sum.md"
    f.write_text("We discussed overlap.\n")
    r = run(root, "summary", "--session", "s-2", "--file", str(f), "--covers", f".work/sessions/{stub}")
    assert r.returncode == 0, r.stderr
    assert json.loads(run(root, "pending", "--json").stdout) == []
    assert run(root, "captured", "--session", "s-2").returncode == 0
    assert "no stub" in run(root, "stub", "--session", "s-2").stdout
