import json

import pytest
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import lint_tex  # noqa: E402
from validate_issue_json import check  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "lint"
SCHEMA = json.loads((ROOT / "schemas" / "issue-report.schema.json").read_text())


def run(root, *args, glossary=FIX / "glossary.md"):
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "lint_tex.py"), "--root", str(root),
                          "--glossary", str(glossary), *map(str, args)], capture_output=True, text=True)
    return out.returncode, json.loads(out.stdout)


@pytest.fixture
def dirty(tmp_path):
    """The dirty fixture stores @EMDASH@ so the repo holds no literal em dash."""
    src = (FIX / "dirty" / "main.tex").read_text().replace("@EMDASH@", "\u2014")
    (tmp_path / "main.tex").write_text(src)
    return tmp_path


def by_rule(rep, rule):
    return [i for i in rep["issues"] if i["evidence"].startswith(f"[{rule}]")]


def test_clean_file_accepts_and_is_schema_valid():
    code, rep = run(FIX / "clean")
    assert rep["issues"] == [], rep["issues"]
    assert rep["verdict"] == "accept" and code == 0
    assert rep["gate"] == "G0" and rep["reviewer"] == "lint-tex"
    assert check(rep, SCHEMA) == []


def test_dirty_file_report_is_schema_valid_and_revise(dirty):
    code, rep = run(dirty)
    assert check(rep, SCHEMA) == []
    assert rep["verdict"] == "revise" and code == 1
    ids = [i["id"] for i in rep["issues"]]
    assert len(ids) == len(set(ids))


def test_em_dashes(dirty):
    _, rep = run(dirty)
    locs = sorted(i["location"] for i in by_rule(rep, "em-dash"))
    assert locs == ["main.tex:5", "main.tex:7"]


def test_ref_and_eqref(dirty):
    _, rep = run(dirty)
    ev = " ".join(i["evidence"] for i in by_rule(rep, "ref"))
    assert "\\ref{}" in ev and "\\eqref{}" in ev
    assert len(by_rule(rep, "ref")) == 2


def test_banned_words_including_across_line_break(dirty):
    _, rep = run(dirty)
    found = {i["evidence"].split('"')[1] for i in by_rule(rep, "banned-word")}
    assert found == {"clearly", "it is easy to see", "trivially", "straightforwardly", "the key insight"}
    easy = [i for i in by_rule(rep, "banned-word") if "easy" in i["evidence"]][0]
    assert easy["location"] == "main.tex:6"


def test_titles_are_warnings(dirty):
    _, rep = run(dirty)
    titles = by_rule(rep, "title")
    assert all(i["severity"] == "minor" for i in titles)
    ev = " | ".join(i["evidence"] for i in titles)
    assert "ends with punctuation" in ev and "contains the verb is" in ev
    assert "has 9 words" in ev
    assert "Results" not in ev


def test_raw_words_from_glossary_skip_definitions(dirty):
    _, rep = run(dirty)
    raw = by_rule(rep, "raw-word")
    assert [i["location"] for i in raw] == ["main.tex:5"]
    assert "\\sysname" in raw[0]["suggested_fix"]


def test_label_prefix(dirty):
    _, rep = run(dirty)
    assert [i["location"] for i in by_rule(rep, "label-prefix")] == ["main.tex:4"]


def test_unresolved_cref_only_missing_target(dirty):
    _, rep = run(dirty)
    ev = [i["evidence"] for i in by_rule(rep, "unresolved-ref")]
    assert len(ev) == 1 and "lem.missing" in ev[0]


def test_labels_resolve_across_files():
    _, rep = run(FIX / "crossref")
    ev = [i["evidence"] for i in by_rule(rep, "unresolved-ref")]
    assert len(ev) == 1 and "thm.nowhere" in ev[0]


def test_author_notes_default_and_glossary_are_warnings(dirty):
    _, rep = run(dirty)
    notes = by_rule(rep, "author-note")
    assert {i["evidence"].split("\\")[1].split("{")[0] for i in notes} == {"todo", "odysseas"}
    assert all(i["severity"] == "minor" for i in notes)
    _, notes_from_glossary = lint_tex.read_glossary(FIX / "glossary.md")
    assert set(notes_from_glossary) == {"odysseas", "fixme"}


def test_glossary_parsing_ignores_placeholders():
    raw, _ = lint_tex.read_glossary(FIX / "glossary.md")
    assert raw == {"Bitcoin": "\\sysname", "BTC": "\\sysname"}


def test_no_sentence_length_rule():
    long_para = "The honest parties " + "extend the chain and " * 60 + "stop.\n"
    p = FIX.parent / "_long.tex"
    try:
        p.write_text(long_para)
        assert lint_tex.check_file(p, "_long.tex", set(), {}, []) == []
    finally:
        p.unlink()


def test_stable_ids_with_previous(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    (proj / "main.tex").write_text("A --- b. Clearly c.\n")
    _, r1 = run(proj)
    prev = tmp_path / "r1.json"
    prev.write_text(json.dumps(r1))
    clearly_id = [i["id"] for i in r1["issues"] if "clearly" in i["evidence"]][0]
    (proj / "main.tex").write_text("\n\nClearly c. Obviously d.\n")
    _, r2 = run(proj, "--previous", prev)
    ids = {i["evidence"].split('"')[1]: i["id"] for i in by_rule(r2, "banned-word")}
    assert ids["clearly"] == clearly_id
    assert ids["obviously"] == "G0/lint-tex/3"


def test_build_failure_is_blocking(tmp_path):
    (tmp_path / "main.tex").write_text("\\documentclass{article}\\begin{document}\\undefinedmacro\\end{document}\n")
    code, rep = run(tmp_path, "--build")
    b = by_rule(rep, "build")
    assert len(b) == 1 and b[0]["severity"] == "blocking" and code == 1
