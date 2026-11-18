import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
AG = ROOT / "scripts" / "agenda.py"


def run(root, *args):
    return subprocess.run([sys.executable, str(AG), "--root", str(root), *args], capture_output=True, text=True)


@pytest.fixture
def root(tmp_path):
    (tmp_path / ".work").mkdir()
    (tmp_path / ".work" / "decisions.md").write_text("# Decisions\n")
    return tmp_path


def order(root):
    return [t["id"] for t in json.loads(run(root, "list", "--all", "--json").stdout)]


def test_seed_from_playbook_with_current_stage(root):
    r = run(root, "seed", "--playbook", "new-paper", "--current", "S4")
    assert r.returncode == 0, r.stderr
    ts = json.loads(run(root, "list", "--all", "--json").stdout)
    assert [t["stage"] for t in ts[:4]] == ["S1", "S2", "S3", "S4"]
    assert [t["status"] for t in ts[:4]] == ["done", "done", "done", "committed"]
    assert json.loads(run(root, "next", "--json").stdout)["stage"] == "S4"
    assert run(root, "seed", "--playbook", "new-paper").returncode == 2
    assert run(root, "lint").returncode == 0


def test_add_move_set_drop_and_log(root):
    run(root, "seed", "--playbook", "proof-verification")
    t = run(root, "add", "--title", "Partial overlap", "--goal", "safety under 80 percent overlap", "--status",
            "exploring").stdout.strip()
    assert order(root)[-1] == t
    run(root, "move", t, "--top")
    assert order(root)[0] == t
    assert json.loads(run(root, "next", "--json").stdout)["id"] == "T1"  # exploring is not next
    run(root, "set", t, "status=committed", "next=state the overlap lemma")
    assert json.loads(run(root, "next", "--json").stdout)["id"] == t
    run(root, "--reason", "not needed for the verdict", "drop", "T2", "--reason", "covered by T3")
    ts = {x["id"]: x for x in json.loads(run(root, "list", "--all", "--json").stdout)}
    assert ts["T2"]["status"] == "dropped" and "covered by T3" in ts["T2"]["note"]
    assert "T2" not in [x["id"] for x in json.loads(run(root, "list", "--json").stdout)]
    log = (root / ".work" / "decisions.md").read_text()
    assert log.count("- class: logged") == 4 and "agenda: drop T2" in log and "agenda: move" in log
    run(root, "move", "T4", "--after", "T1")
    assert order(root).index("T4") == order(root).index("T1") + 1


def test_errors(root):
    run(root, "seed", "--playbook", "open-ended")
    assert run(root, "set", "T9", "status=done").returncode == 2
    assert run(root, "set", "T1", "status=gone").returncode == 2
    assert run(root, "set", "T1", "status=dropped").returncode == 2
    assert run(root, "move", "T1").returncode == 2
    assert run(root, "seed", "--playbook", "nope").returncode == 2


def test_title_with_bar_survives(root):
    t = run(root, "add", "--title", "A | B", "--goal", "g").stdout.strip()
    assert json.loads(run(root, "list", "--json").stdout)[0]["title"] == "A / B" and t == "T1"


def test_next_without_agenda_is_an_error(root):
    r = run(root, "next")
    assert r.returncode == 2 and "project_update.py" in r.stderr
