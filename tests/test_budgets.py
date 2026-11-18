import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import budgets  # noqa: E402


def env(tmp_path, monkeypatch):
    monkeypatch.setenv("RW_BUDGETS", str(tmp_path / "budgets.json"))
    monkeypatch.setenv("RW_USAGE_GLOBAL", str(tmp_path / "global.tsv"))


def test_default_when_uncalibrated(tmp_path, monkeypatch):
    env(tmp_path, monkeypatch)
    dfl = json.loads(budgets.DEFAULTS.read_text())
    assert budgets.get("proof-main") == dfl["proof-main"]
    assert budgets.get("no-such-type") == dfl["other"]


def test_log_writes_project_and_global(tmp_path, monkeypatch):
    env(tmp_path, monkeypatch)
    proj = tmp_path / "proj"
    (proj / ".work").mkdir(parents=True)
    budgets.log(proj, "model", "S4-model", "modeler", 87000, "sess")
    budgets.log(proj, "model", "S4-model", "conformance-reviewer", 41000, "sess")
    rows = (proj / ".work/usage.tsv").read_text().splitlines()
    assert rows[0].startswith("time\tsession") and len(rows) == 3 and rows[1].endswith("\t87000")
    g = (tmp_path / "global.tsv").read_text().splitlines()
    assert len(g) == 3 and str(proj.resolve()) in g[1]


def test_recalibrate_needs_three_briefs(tmp_path, monkeypatch):
    env(tmp_path, monkeypatch)
    for i, n in enumerate([100000, 200000]):
        budgets.log(tmp_path / f"p{i}", "model", "S4-model", "modeler", n)
    budgets.recalibrate()
    dfl = json.loads(budgets.DEFAULTS.read_text())
    assert budgets.get("model") == dfl["model"]
    budgets.log(tmp_path / "p2", "model", "S4-model", "modeler", 300000)
    budgets.log(tmp_path / "p2", "model", "S4-model", "assumption-auditor", 20000)  # same brief: summed, 320k
    out = budgets.recalibrate()
    # p90 of [100k, 200k, 320k] = 296k; x1.25 = 370k
    assert out["model"] == 370000 and budgets.get("model") == 370000
    assert out["proof-main"] == dfl["proof-main"]
