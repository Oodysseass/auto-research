import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import review_status  # noqa: E402
from validate_issue_json import check  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "review_status"
SCHEMAS = {n: json.loads((ROOT / "schemas" / f"{n}.schema.json").read_text())
           for n in ("issue-report", "issue-response", "arbiter-ruling")}


def status(case):
    return review_status.analyse(FIX / case / ".work" / "issues", "lemma")


def overall(case):
    o = status(case)["overall"]
    return o["status"], o["action"], o.get("gate"), o.get("reviewer")


def test_fixtures_are_schema_valid():
    for f in FIX.glob("*/.work/issues/*.json"):
        kind = "arbiter-ruling" if ".ruling" in f.name else "issue-response" if f.name.endswith(".response.json") else "issue-report"
        assert check(json.loads(f.read_text()), SCHEMAS[kind]) == [], f


# One fixture directory per outcome.

def test_converged():
    assert overall("converged") == ("converged", "none", None, None)


def test_open():
    assert overall("open") == ("open", "run", "G1", "conformance-reviewer")


def test_deadlocked():
    s, a, g, rv = overall("deadlocked")
    assert (s, a, g, rv) == ("deadlocked", "arbitrate", "G2", "proof-checker")
    assert status("deadlocked")["overall"]["issue"] == "G2/proof-checker/1"


def test_stalled_no_diff():
    assert overall("stalled")[:2] == ("stalled", "human")


def test_stalled_repeated_hash():
    res = status("stalled-repeat")["overall"]
    assert (res["status"], res["reason"]) == ("stalled", "r3 content repeats r1")


def test_max_rounds_uses_brief_budget():
    res = status("max_rounds")
    assert res["budget"] == 3
    assert overall("max_rounds")[:2] == ("max_rounds", "human")


# Critical artifacts.

def test_g3_counts_as_second_clean_round():
    res = status("critical-g3-second-round")
    assert all(g["status"] == "converged" for g in res["gates"].values())
    assert "clean G3 codex r1" in res["gates"]["G1"]["reason"]
    assert res["overall"]["status"] == "converged"


def test_critical_one_clean_round_moves_to_next_gate():
    res = status("critical-awaiting-g3")
    assert res["gates"]["G1"]["action"] == "next-gate"
    assert res["gates"]["G2"]["action"] == "next-gate"
    assert overall("critical-awaiting-g3") == ("open", "run", "G3", "codex")


def test_g3_on_other_content_does_not_count():
    res = status("critical-g3-other-content")
    assert res["gates"]["G1"]["status"] == "open"
    assert "voided" in res["gates"]["G1"]["reason"]
    assert res["overall"]["gate"] == "G1"


def test_edit_between_two_clean_rounds():
    res = status("critical-edit-between-clean-rounds")
    assert res["gates"]["G1"]["status"] == "open"
    assert res["gates"]["G1"]["action"] == "next-gate"


def test_two_clean_rounds_same_content():
    assert overall("critical-two-clean-rounds") == ("converged", "none", None, None)


def test_edit_after_clean_round_reruns_from_g1():
    res = status("edit-after-clean")
    assert res["overall"]["gate"] == "G1" and res["overall"]["action"] == "run"
    assert "voided" in res["overall"]["reason"]


# Duplicates.

def test_duplicate_only_issue_counts_once_and_keeps_g3_open():
    res = status("duplicate-only")
    assert res["open_issues"] == {"blocking": 1, "major": 0, "minor": 0}
    assert res["gates"]["G3"]["status"] == "open"
    assert overall("duplicate-only") == ("open", "run", "G2", "proof-checker")


def test_duplicate_closed_with_its_canonical_issue():
    res = status("duplicate-closed-by-ruling")
    assert res["overall"]["status"] == "converged", res


# Arbiter rulings.

def test_producer_right_closes_issue():
    # proof-checker converges on the closed issue; G2 moves on to counterexample-hunter.
    assert overall("ruling-producer-right") == ("open", "run", "G2", "counterexample-hunter")
    assert status("ruling-producer-right")["open_issues"]["major"] == 0


def test_reviewer_right_issue_stands():
    assert overall("ruling-reviewer-right") == ("open", "run", "G2", "proof-checker")


def test_rejection_after_reviewer_right_goes_to_human():
    assert overall("ruling-reviewer-right-rejected-again")[:2] == ("deadlocked", "human")


def test_needs_human_ruling_goes_to_mythos_arbiter():
    assert overall("ruling-needs-human-first")[:2] == ("deadlocked", "arbitrate-mythos")


def test_main_theorem_needs_second_ruling():
    assert overall("ruling-main-theorem")[:2] == ("deadlocked", "arbitrate-mythos")


def test_main_theorem_second_ruling_governs():
    assert overall("ruling-main-theorem-second") == ("open", "run", "G2", "proof-checker")


# CLI.

def test_cli_text_output_last_line():
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "review_status.py"),
                          str(FIX / "deadlocked" / ".work" / "issues"), "lemma"], capture_output=True, text=True)
    assert out.returncode == 0
    assert out.stdout.strip().splitlines()[-1] == "overall: deadlocked -> arbitrate G2 proof-checker G2/proof-checker/1"


def test_cli_json_and_missing_dir(tmp_path):
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "review_status.py"),
                          str(FIX / "open" / ".work" / "issues"), "lemma", "--json"], capture_output=True, text=True)
    assert json.loads(out.stdout)["overall"]["status"] == "open"
    bad = subprocess.run([sys.executable, str(ROOT / "scripts" / "review_status.py"), str(tmp_path / "nope"), "x"])
    assert bad.returncode == 2


@pytest.mark.parametrize("case", sorted(p.name for p in FIX.iterdir() if p.is_dir()))
def test_every_fixture_returns_a_known_status(case):
    assert status(case)["overall"]["status"] in {"converged", "deadlocked", "stalled", "max_rounds", "open"}


def test_brief_gates_field_names_g2_reviewers(tmp_path):
    import shutil
    case = tmp_path / "c"
    shutil.copytree(FIX / "ruling-producer-right", case)
    brief = case / ".work" / "briefs" / "S1-lemma.md"
    brief.write_text(brief.read_text().replace("- main theorem: no", "- main theorem: no\n- gates: G1, G2[assumption-auditor proof-checker]"))
    res = review_status.analyse(case / ".work" / "issues", "lemma")
    assert res["overall"]["status"] == "converged", res["overall"]
    assert review_status.parse_gates("G0, G2[a b], G3") == {"G0": None, "G2": ["a", "b"], "G3": None}
