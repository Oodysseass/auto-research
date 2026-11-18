import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "codex-review" / "codex_review.sh"

FAKE = r'''#!/usr/bin/env python3
"""Fake codex: `login status`, and `exec` that answers with a clean review and runs $FAKE_TAMPER (a shell snippet) first."""
import json, os, subprocess, sys
a = sys.argv[1:]
if a[:2] == ["login", "status"]:
    print("Logged in using ChatGPT")
    sys.exit(0)
sys.stdin.read()
if os.environ.get("FAKE_TAMPER"):
    subprocess.run(os.environ["FAKE_TAMPER"], shell=True, cwd=a[a.index("-C") + 1], check=True)
out = a[a.index("--output-last-message") + 1]
open(out, "w").write(json.dumps({"issues": [], "verdict": "accept"}))
'''


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout


@pytest.fixture
def proj(tmp_path):
    p = tmp_path / "proj"
    (p / "paper").mkdir(parents=True)
    (p / "paper" / "lemma.tex").write_text("\\begin{lemma}x\\end{lemma}\n")
    git(tmp_path, "init", "-q", str(p))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "repos.py"), "--root", str(p), "init"], check=True,
                   capture_output=True)
    (p / ".work" / "issues").mkdir()
    (p / ".work" / "briefs").mkdir()
    (p / ".work" / "contract.md").write_text("- ai_tools_allowed: claude, codex\n")
    (p / ".work" / "claims.md").write_text("## C1\n- status: draft\n")
    (p / ".work" / "briefs" / "S8-lemma.md").write_text("# Brief\n")
    for repo in (p, p / ".work"):
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "init")
    fake = tmp_path / "codex"
    fake.write_text(FAKE)
    fake.chmod(0o755)
    return p, fake


def review(proj, fake, tamper=""):
    env = dict(os.environ, CODEX_BIN=str(fake), FAKE_TAMPER=tamper)
    return subprocess.run(["bash", str(SCRIPT), "--artifact", "paper/lemma.tex", "--slug", "lemma", "--round", "1",
                           "--brief", ".work/briefs/S8-lemma.md", "--model", "m1", "--effort", "high"],
                          cwd=proj, env=env, capture_output=True, text=True)


def test_clean_review_records_both_commits(proj):
    p, fake = proj
    r = review(p, fake)
    assert r.returncode == 0, r.stderr
    rep = json.loads((p / ".work" / "issues" / "lemma.G3.codex.r1.json").read_text())
    proj_head, work_head = git(p, "rev-parse", "--short=7", "HEAD").strip(), git(p / ".work", "rev-parse", "--short=7", "HEAD").strip()
    assert rep["commit"] == f"{proj_head}+{work_head}"


def test_codex_editing_claims_is_caught_and_reverted(proj):
    p, fake = proj
    r = review(p, fake, tamper="echo '- status: verified' >> .work/claims.md")
    assert r.returncode == 3, r.stderr
    assert ".work/claims.md" in r.stderr and "REVIEW DISCARDED" in r.stderr
    assert (p / ".work" / "claims.md").read_text() == "## C1\n- status: draft\n"
    assert not (p / ".work" / "issues" / "lemma.G3.codex.r1.json").exists()
    assert git(p / ".work", "status", "--porcelain") == ""


def test_refuses_when_work_repo_dirty(proj):
    p, fake = proj
    (p / ".work" / "state.md").write_text("dirty\n")
    r = review(p, fake)
    assert r.returncode == 2 and "not clean" in r.stderr
