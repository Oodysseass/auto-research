import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "scripts" / "resources.py"
DEC = ROOT / "scripts" / "decisions.py"

CONTRACT = """# Contract

## Requirements

| ID | Requirement | Source | Approved |
|---|---|---|---|
| R1 | Prove safety of the protocol | resources/BRIEF.md:3 | D1 |
| R2 | Deliver a paper section | resources/BRIEF.md:5 | D1 |

## G1 checks

| ID | Check | Source |
|---|---|---|
| P1 | the artifact does not contradict the expected answer | resources/BRIEF.md:9 |
| N1 | the artifact does not pursue liveness | resources/BRIEF.md:12 |
"""


def run(proj, *args):
    return subprocess.run([sys.executable, str(RES), "--root", str(proj), *args], capture_output=True, text=True)


@pytest.fixture
def proj(tmp_path):
    p = tmp_path / "proj"
    (p / ".work" / "decisions").mkdir(parents=True)
    (p / ".work" / "contract.md").write_text(CONTRACT)
    (p / ".work" / "claims.md").write_text("# Claims\n\n## C1\n- label: lem:safety\n- status: draft\n")
    (p / ".work" / "model.md").write_text("# Model\n\n| A1 | synchrony |\n")
    (p / ".work" / "decisions.md").write_text("# Decisions\n")
    (p / "resources").mkdir()
    (p / "resources" / "BRIEF.md").write_text("# Brief\n")
    (p / "resources" / "notes.md").write_text("# Notes\nLemma 1.\n")
    (p / "resources" / ".DS_Store").write_text("x")
    r = run(p, "init")
    assert r.returncode == 0, r.stderr
    return p


def manifest(proj):
    rows = [l.split("\t") for l in (proj / ".work" / "resources.manifest").read_text().splitlines() if not l.startswith("#")]
    return {r[0]: r for r in rows}


def cards(proj):
    return sorted(p.name for p in (proj / ".work" / "decisions").glob("D*.md"))


def test_init_lists_every_file_with_hash_size_and_date(proj):
    m = manifest(proj)
    assert set(m) == {"resources/BRIEF.md", "resources/notes.md"}  # hidden files ignored
    row = m["resources/notes.md"]
    assert row[1] == hashlib.sha256((proj / "resources" / "notes.md").read_bytes()).hexdigest()
    assert row[2] == str((proj / "resources" / "notes.md").stat().st_size)
    assert len(row[3]) == 10 and row[4] == "intake"
    assert run(proj, "init").returncode == 2  # never overwritten
    assert run(proj, "scan").stdout.strip() == "resources: 0 new, 0 edited, 0 deleted"


def test_new_file_that_changes_scope_raises_blocking_decision(proj):
    (proj / "resources" / "sow-v2.md").write_text("# SoW v2\nAlso prove liveness.\n")
    s = json.loads(run(proj, "scan", "--json").stdout)
    assert [x["path"] for x in s["new"]] == ["resources/sow-v2.md"]
    r = run(proj, "raise", "resources/sow-v2.md", "--summary", "second version of the SoW, adds liveness",
            "--affects", "R1,N1,P1,C1", "--reason", "the new version asks for liveness, which the contract excludes",
            "--scope-change", "--sow-version")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["class"] == "blocking" and out["affects"] == ["R1", "N1", "P1", "C1"]
    card = (proj / ".work" / "decisions" / f"{out['card']}.md").read_text()
    assert "- class: blocking" in card and "- status: open" in card
    assert "- depends: R1, N1, P1, C1" in card
    assert "R1" not in card.split("- depends:")[0]  # the question is plain; IDs stay in depends
    for label in ("Update the contract", "Ignore this file", "Stop the project"):
        assert label in card
    lint = subprocess.run([sys.executable, str(DEC), "--root", str(proj), "lint", out["card"]], capture_output=True, text=True)
    assert lint.returncode == 0, lint.stdout
    assert manifest(proj)["resources/sow-v2.md"][5] == out["card"]
    assert run(proj, "scan").stdout.strip() == "resources: 0 new, 0 edited, 0 deleted"


def test_new_file_bearing_on_contract_without_scope_change_is_checkpoint(proj):
    (proj / "resources" / "note-model.md").write_text("Delays are bounded by Delta.\n")
    out = json.loads(run(proj, "raise", "resources/note-model.md", "--summary", "bounded delays",
                         "--affects", "A1,C1", "--reason", "it fixes the network assumption").stdout)
    assert out["class"] == "checkpoint"


def test_raise_rejects_unknown_ids(proj):
    (proj / "resources" / "x.md").write_text("x\n")
    r = run(proj, "raise", "resources/x.md", "--summary", "x", "--affects", "R9", "--reason", "x", "--scope-change")
    assert r.returncode == 2 and "R9" in r.stderr and cards(proj) == []
    assert "resources/x.md" not in manifest(proj)


def test_unrelated_new_file_is_only_recorded(proj):
    (proj / "resources" / "slides.md").write_text("talk slides from a workshop\n")
    r = run(proj, "record", "resources/slides.md", "--summary", "workshop slides on an unrelated topic")
    assert r.returncode == 0, r.stderr
    assert cards(proj) == []  # no decision card
    row = manifest(proj)["resources/slides.md"]
    assert row[4] == "new" and row[5] == "recorded" and row[7] == "workshop slides on an unrelated topic"
    log = (proj / ".work" / "decisions.md").read_text()
    assert "new input recorded: resources/slides.md" in log and "- class: logged" in log
    screen = subprocess.run([sys.executable, str(DEC), "--root", str(proj), "checkpoint"], capture_output=True, text=True).stdout
    assert "new input recorded: resources/slides.md" in screen  # listed in the digest
    assert run(proj, "scan").stdout.strip() == "resources: 0 new, 0 edited, 0 deleted"
    assert run(proj, "record", "resources/slides.md", "--summary", "again").returncode == 2


def test_edited_file_warns_once_and_keeps_old_entry(proj):
    old = manifest(proj)["resources/notes.md"]
    (proj / "resources" / "notes.md").write_text("# Notes\nLemma 1, changed.\n")
    first = run(proj, "scan", "--warn").stdout
    assert first.count("WARNING") == 1 and "WARNING edited: resources/notes.md" in first
    second = run(proj, "scan", "--warn").stdout
    assert "WARNING" not in second
    assert run(proj, "scan").stdout.strip() == "resources: 0 new, 0 edited, 0 deleted"
    now = manifest(proj)["resources/notes.md"]
    assert now[:4] == old[:4]  # path, sha256, size, date seen: unchanged
    assert now[6].startswith("edited ")
    # a later, different edit is a new anomaly: warned once again
    (proj / "resources" / "notes.md").write_text("# Notes\nchanged twice\n")
    assert run(proj, "scan", "--warn").stdout.count("WARNING") == 1
    assert "WARNING" not in run(proj, "scan", "--warn").stdout


def test_deleted_file_warns_once(proj):
    (proj / "resources" / "notes.md").unlink()
    assert run(proj, "scan", "--warn").stdout.count("WARNING deleted") == 1
    assert "WARNING" not in run(proj, "scan", "--warn").stdout
    assert "resources/notes.md" in manifest(proj)


def test_scan_without_warn_is_read_only(proj):
    (proj / "resources" / "notes.md").write_text("edited\n")
    before = (proj / ".work" / "resources.manifest").read_text()
    assert "WARNING edited" in run(proj, "scan").stdout
    assert "WARNING edited" in run(proj, "scan").stdout
    assert (proj / ".work" / "resources.manifest").read_text() == before


def test_refresh_accepts_a_workflow_edit(proj):
    (proj / "resources" / "BRIEF.md").write_text("# Brief\n\n## Addendum 2026-11-18\nmore\n")
    assert run(proj, "refresh", "resources/BRIEF.md", "--reason", "addendum for D4").returncode == 0
    assert run(proj, "scan").stdout.strip() == "resources: 0 new, 0 edited, 0 deleted"
