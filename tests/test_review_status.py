import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import review_status  # noqa: E402
from validate_issue_json import check  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "review_status"
sys.path.insert(0, str(FIX))
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


# Review context: model.md, glossary.md, and the claims.md entries of the artifact's claims and dependencies.

def test_model_changed_between_clean_rounds_breaks_consecutive():
    res = status("critical-model-changed-between-clean-rounds")
    assert res["gates"]["G1"]["status"] == "open"
    assert res["gates"]["G1"]["action"] == "next-gate"


def test_dependency_claim_changed_between_clean_rounds_breaks_consecutive():
    res = status("critical-dependency-changed-between-clean-rounds")
    assert res["gates"]["G1"]["status"] == "open"


def test_claim_status_change_is_not_an_edit():
    assert overall("critical-status-changed-between-clean-rounds") == ("converged", "none", None, None)


def test_model_changed_after_clean_round_voids_it():
    res = status("model-changed-after-clean")
    assert res["overall"]["gate"] == "G1" and "voided" in res["overall"]["reason"]


def test_claims_hash_covers_dependencies_only(tmp_path):
    from make_fixtures import materialize
    materialize(tmp_path, "A", "A", "A")
    base = review_status.claims_hash(tmp_path, ["C1"])
    cl = tmp_path / ".work" / "claims.md"
    cl.write_text(cl.read_text().replace("- statement: Unrelated.", "- statement: Changed."))
    assert review_status.claims_hash(tmp_path, ["C1"]) == base  # C3 is not a dependency
    cl.write_text(cl.read_text().replace("- depends_on: C2", "- depends_on: C2, C3"))
    assert review_status.claims_hash(tmp_path, ["C1"]) != base
    assert review_status.claim_closure(review_status.parse_claims(cl), ["C1"]) == ["C1", "C2", "C3"]


def test_cli_hashes_prints_review_log_cell():
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "review_status.py"),
                          str(FIX / "converged" / ".work" / "issues"), "lemma", "--hashes"], capture_output=True, text=True)
    cell = out.stdout.strip()
    assert [k.split("=")[0] for k in cell.split("; ")] == ["paper/lemma.tex", ".work/model.md", ".work/glossary.md", "claims"]
    brief = (FIX / "converged" / ".work" / "briefs" / "S1-lemma.md").read_text()
    assert cell in brief


# Deadlock ladder: arbiter, then arbiter-mythos, then the human.

def test_both_arbiters_need_human_goes_to_human():
    res = status("ruling-both-need-human")["overall"]
    assert (res["status"], res["action"]) == ("deadlocked", "human")
    assert res["question"] == "Which?"


def test_main_theorem_second_ruling_needs_human_overrides_first():
    assert overall("ruling-main-theorem-second-needs-human")[:2] == ("deadlocked", "human")


def test_mythos_ruling_settles_after_first_needs_human():
    # ruling 2 (producer_right) closes the issue; G2 moves on to counterexample-hunter.
    assert overall("ruling-needs-human-then-producer-right") == ("open", "run", "G2", "counterexample-hunter")


@pytest.mark.parametrize("case", sorted(p.name for p in FIX.iterdir() if p.is_dir()))
def test_human_only_after_the_arbiters(case):
    """Every deadlocked -> human verdict has ruling 1, and ruling 2 where the ladder requires it."""
    res = status(case)
    for s in list(res["gates"].values()) + [res["overall"]]:
        if s["status"] != "deadlocked":
            continue
        issue = s["issue"]
        g, rv, n = issue.split("/")
        rulings = {int(p.name[-6]) for p in (FIX / case / ".work" / "issues").glob(f"lemma.{g}.{rv}.i{n}.ruling*.json")}
        if s["action"] == "arbitrate":
            assert rulings == set()
        if s["action"] == "arbitrate-mythos":
            assert rulings == {1}
        if s["action"] == "human":
            assert 1 in rulings
            r1 = json.loads((FIX / case / ".work" / "issues" / f"lemma.{g}.{rv}.i{n}.ruling1.json").read_text())["ruling"]
            if r1 == "needs_human" or res["main"]:
                assert 2 in rulings


# Provisional claims and the automatic budget.

import shutil  # noqa: E402


def case_copy(tmp_path, case):
    dst = tmp_path / case
    shutil.copytree(FIX / case, dst)
    return dst


def set_claim(root, cid, **kv):
    p = root / ".work" / "claims.md"
    out, cur = [], None
    for line in p.read_text().splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
        if cur == cid:
            for k, v in kv.items():
                if line.startswith(f"- {k}:"):
                    line = f"- {k}: {v}"
        out.append(line)
    p.write_text("\n".join(out) + "\n")


def usage(root, brief, tokens):
    (root / ".work" / "usage.tsv").write_text(
        "time\tsession\tstage_type\tbrief\trole\ttokens\n" + f"t\ts\tproof-lemma\t{brief}\tprover\t{tokens}\n")


def analyse_at(root):
    return review_status.analyse(root / ".work" / "issues", "lemma")


def test_provisional_dependency_gives_converged_provisional(tmp_path):
    root = case_copy(tmp_path, "converged")
    set_claim(root, "C2", status="provisional")
    res = analyse_at(root)
    assert res["overall"]["status"] == "converged-provisional"
    assert res["overall"]["action"] == "none"
    assert res["provisional"] and res["provisional"][0][0] == "C2"


def test_provisional_unrelated_claim_is_ignored(tmp_path):
    root = case_copy(tmp_path, "converged")
    set_claim(root, "C3", status="provisional")
    assert analyse_at(root)["overall"]["status"] == "converged"


def test_status_change_to_provisional_is_not_an_edit(tmp_path):
    root = case_copy(tmp_path, "converged")
    before = review_status.content_hashes(root, review_status.parse_brief(root / ".work/briefs/S1-lemma.md")[0])
    set_claim(root, "C1", status="provisional")
    after = review_status.content_hashes(root, review_status.parse_brief(root / ".work/briefs/S1-lemma.md")[0])
    assert before == after


def test_under_budget_is_unchanged(tmp_path):
    root = case_copy(tmp_path, "open")
    usage(root, "S1-lemma", 50000)
    o = analyse_at(root)["overall"]
    assert (o["status"], o["action"]) == ("open", "run")


def test_over_budget_with_new_issues_extends(tmp_path):
    root = case_copy(tmp_path, "open")
    usage(root, "S1-lemma", 150000)
    o = analyse_at(root)["overall"]
    assert (o["status"], o["action"]) == ("open", "extend-budget")


def test_over_extended_budget_is_stalled(tmp_path):
    root = case_copy(tmp_path, "open")
    b = root / ".work/briefs/S1-lemma.md"
    b.write_text(b.read_text().replace("- tokens: 100k", "- tokens: 100k\n- extended: yes"))
    usage(root, "S1-lemma", 140000)
    assert analyse_at(root)["overall"]["action"] == "run"  # 140k < 150k
    usage(root, "S1-lemma", 160000)
    o = analyse_at(root)["overall"]
    assert (o["status"], o["action"]) == ("stalled", "human")


def test_over_budget_without_new_issues_is_stalled(tmp_path):
    root = case_copy(tmp_path, "open")
    issues = root / ".work" / "issues"
    r1 = json.loads((issues / "lemma.G1.conformance-reviewer.r1.json").read_text())
    (issues / "lemma.G1.conformance-reviewer.r2.json").write_text(json.dumps(r1))
    usage(root, "S1-lemma", 150000)
    o = analyse_at(root)["overall"]
    assert (o["status"], o["action"]) == ("stalled", "human")
    assert "no new issues" in o["reason"]


def test_budget_never_overrides_deadlock_or_convergence(tmp_path):
    for case, status in (("deadlocked", "deadlocked"), ("converged", "converged")):
        root = case_copy(tmp_path, case)
        usage(root, "S1-lemma", 10 ** 7)
        assert analyse_at(root)["overall"]["status"] == status


def test_cli_prints_provisional_line(tmp_path):
    root = case_copy(tmp_path, "converged")
    set_claim(root, "C2", status="provisional", provisional_on="D1")
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "review_status.py"), str(root / ".work/issues"), "lemma"],
                         capture_output=True, text=True).stdout
    assert "overall: converged-provisional -> none" in out


# Legacy issue files and the optional issue status.

def legacy_issue(n, severity, **extra):
    return dict({"id": f"G5/legacy/{n}", "severity": severity, "location": "x.tex", "claim": None,
                 "evidence": "e", "suggested_fix": "f"}, **extra)


def write_legacy(d, issues):
    d.mkdir(parents=True, exist_ok=True)
    (d / "legacy-open.json").write_text(json.dumps(
        {"gate": "G5", "reviewer": "legacy", "model": "none", "artifact": "a", "commit": "c", "issues": issues}))
    (d / "README.md").write_text("# Issues\n")


def test_all_counts_legacy_issues_without_status_as_open(tmp_path):
    d = tmp_path / ".work" / "issues"
    write_legacy(d, [legacy_issue(1, "major"), legacy_issue(2, "major"), legacy_issue(3, "minor")])
    res = review_status.open_issues_all(d)
    assert res["per"]["legacy-open.json"] == {"blocking": 0, "major": 2, "minor": 1}
    assert res["total"] == {"blocking": 0, "major": 2, "minor": 1}


def test_all_skips_closed_and_duplicate_legacy_issues(tmp_path):
    d = tmp_path / ".work" / "issues"
    write_legacy(d, [legacy_issue(1, "major", status="closed"), legacy_issue(2, "major", status="open"),
                     legacy_issue(3, "major", duplicate_of="G5/legacy/2")])
    assert review_status.open_issues_all(d)["total"] == {"blocking": 0, "major": 1, "minor": 0}


def test_all_adds_artifact_reports_to_legacy_counts(tmp_path):
    src = FIX / "critical-awaiting-g3"
    d = tmp_path / "p" / ".work" / "issues"
    subprocess.run(["cp", "-R", str(src), str(tmp_path / "p")], check=True)
    per_artifact = review_status.analyse(d, "lemma")["open_issues"]
    write_legacy(d, [legacy_issue(1, "blocking")])
    res = review_status.open_issues_all(d)
    assert res["per"]["lemma"] == per_artifact
    assert res["total"]["blocking"] == per_artifact["blocking"] + 1


def test_report_issue_status_is_ignored_outside_legacy_files(tmp_path):
    src = FIX / "open"
    subprocess.run(["cp", "-R", str(src), str(tmp_path / "p")], check=True)
    d = tmp_path / "p" / ".work" / "issues"
    before = review_status.analyse(d, "lemma")["open_issues"]
    f = sorted(d.glob("lemma.*.r*.json"))
    f = [p for p in f if not p.name.endswith(".response.json") and json.loads(p.read_text())["issues"]][-1]
    rep = json.loads(f.read_text())
    rep["issues"][0]["status"] = "closed"
    f.write_text(json.dumps(rep))
    after = review_status.analyse(d, "lemma")["open_issues"]
    assert after == before


def test_cli_all(tmp_path):
    d = tmp_path / ".work" / "issues"
    write_legacy(d, [legacy_issue(1, "major")])
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "review_status.py"), str(d), "--all"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == ["legacy-open.json: blocking 0, major 1, minor 0",
                                     "open issues: blocking 0, major 1, minor 0"]


def test_validator_allows_status_only_in_legacy_files(tmp_path):
    schema = ROOT / "schemas" / "issue-report.schema.json"
    rep = {"gate": "G2", "reviewer": "proof-checker", "model": "m", "artifact": "a", "commit": "x+y", "verdict": "accept",
           "issues": [{"id": "G2/proof-checker/1", "severity": "minor", "location": "a:1", "claim": None,
                       "evidence": "e", "suggested_fix": "f", "status": "closed"}]}
    for name, want in (("lemma.G2.proof-checker.r1.json", 1), ("legacy-open.json", 0)):
        p = tmp_path / name
        p.write_text(json.dumps(rep))
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_issue_json.py"), str(schema), str(p)],
                           capture_output=True, text=True)
        assert r.returncode == want, (name, r.stdout)


def test_clean_round_without_hashes_does_not_converge(tmp_path):
    subprocess.run(["cp", "-R", str(FIX / "converged"), str(tmp_path / "p")], check=True)
    root = tmp_path / "p"
    for b in (root / ".work" / "briefs").glob("*.md"):
        lines = b.read_text().splitlines()
        b.write_text("\n".join(re.sub(r"\|[^|]*\|\s*$", "|  |", l) if re.match(r"^\|\s*\d+\s*\|", l) else l
                               for l in lines) + "\n")
    o = review_status.analyse(root / ".work" / "issues", "lemma")["overall"]
    assert o["status"] == "open" and "no content hashes" in json.dumps(review_status.analyse(
        root / ".work" / "issues", "lemma"))
