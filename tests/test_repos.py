import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import repos  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPOS = ROOT / "scripts" / "repos.py"
WORKFLOW_FILES = [".work/claims.md", ".work/state.md", ".work/issues/README.md", "CLAUDE.md", ".claude/settings.json",
                  "resources/BRIEF.md", "resources/notes.md", "output/main.pdf", "paper/output/main.pdf"]


def run(proj, *args):
    return subprocess.run([sys.executable, str(REPOS), "--root", str(proj), *args], capture_output=True, text=True)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout


def commit_all(repo, msg):
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", msg)


@pytest.fixture
def proj(tmp_path):
    p = tmp_path / "proj"
    (p / "paper").mkdir(parents=True)
    (p / "paper" / "main.tex").write_text("\\documentclass{llncs}\n")
    git(tmp_path, "init", "-q", str(p))
    r = run(p, "init")
    assert r.returncode == 0, r.stderr
    for f in WORKFLOW_FILES:
        (p / f).parent.mkdir(parents=True, exist_ok=True)
        (p / f).write_text(f"{f}\n")
    commit_all(p, "add paper")
    commit_all(p / ".work", "add contract and playbook")
    return p


def test_project_status_never_shows_workflow_files(proj):
    assert git(proj, "status", "--porcelain", "--untracked-files=all") == ""
    tracked = git(proj, "ls-files").split()
    assert tracked == ["paper/main.tex"]
    assert not (proj / ".gitignore").exists()  # the excludes are local, never a committed file
    exclude = (proj / ".git" / "info" / "exclude").read_text()
    assert all(e in exclude.splitlines() for e in ["/.work/", "/CLAUDE.md", "/.claude/", "/resources/", "output/"])
    # every workflow change stays invisible to the project repo
    for f in WORKFLOW_FILES:
        (proj / f).write_text("changed\n")
    (proj / "resources" / "sow-v2.md").write_text("new\n")
    (proj / ".work" / "decisions").mkdir()
    (proj / ".work" / "decisions" / "D2.md").write_text("# D2\n")
    assert git(proj, "status", "--porcelain", "--untracked-files=all") == ""
    git(proj, "add", "-A")
    assert git(proj, "diff", "--cached", "--name-only") == ""
    # the .work repo sees them
    assert "claims.md" in git(proj / ".work", "status", "--porcelain")
    r = run(proj, "check")
    assert r.returncode == 0, r.stdout
    assert "workflow files tracked by the project repo: none" in r.stdout
    assert "project repo: clean" in r.stdout and ".work repo: dirty" in r.stdout


def test_init_is_idempotent_and_does_not_untrack(tmp_path):
    p = tmp_path / "old"
    (p / "resources").mkdir(parents=True)
    (p / "resources" / "paper.pdf").write_text("x")
    (p / "CLAUDE.md").write_text("old rules\n")
    git(tmp_path, "init", "-q", str(p))
    commit_all(p, "add paper and notes")
    r = run(p, "init")
    assert "TRACKED WORKFLOW FILE in the project repo: CLAUDE.md" in r.stdout
    assert "tracked resources file in the project repo: resources/paper.pdf" in r.stdout
    assert git(p, "ls-files").split() == ["CLAUDE.md", "resources/paper.pdf"]  # nothing untracked automatically
    run(p, "init")
    exclude = (p / ".git" / "info" / "exclude").read_text()
    assert exclude.count("/.work/") == 1
    r = run(p, "check")
    assert r.returncode == 1
    assert "workflow files tracked by the project repo: CLAUDE.md" in r.stdout
    assert "resources/ files tracked by the project repo: resources/paper.pdf" in r.stdout


def test_guard_catches_reviewer_editing_claims(proj):
    base = run(proj, "guard-begin")
    assert base.returncode == 0, base.stderr
    base = base.stdout.strip()
    # the reviewer writes its report and also edits the claims registry
    (proj / ".work" / "issues" / "lemma.G2.proof-checker.r1.json").write_text("{}\n")
    (proj / ".work" / "claims.md").write_text("C1 status: verified\n")
    # the project repo alone does not see it
    assert git(proj, "status", "--porcelain", "--untracked-files=all") == ""
    r = run(proj, "guard-check", "--base", base, "--allow", ".work/issues/lemma.G2.proof-checker.r1")
    assert r.returncode == 3 and " M .work/claims.md" in r.stdout
    assert "lemma.G2.proof-checker.r1.json" not in r.stdout  # its own report is allowed, the edit is not
    r = run(proj, "guard-check", "--base", base, "--allow", ".work/issues/lemma.G2.proof-checker.r1", "--revert")
    assert r.returncode == 3 and "Reverted both repos" in r.stdout
    assert (proj / ".work" / "claims.md").read_text() == ".work/claims.md\n"
    assert not (proj / ".work" / "issues" / "lemma.G2.proof-checker.r1.json").exists()
    assert run(proj, "status").stdout == ""


def test_guard_allows_own_report_only(proj):
    base = run(proj, "guard-begin").stdout.strip()
    (proj / ".work" / "issues" / "lemma.G2.proof-checker.r1.json").write_text("{}\n")
    allow = ["--allow", ".work/issues/lemma.G2.proof-checker.r1"]
    assert run(proj, "guard-check", "--base", base, *allow).returncode == 0
    (proj / ".work" / "issues" / "lemma.G2.assumption-auditor.r1.json").write_text("{}\n")
    r = run(proj, "guard-check", "--base", base, *allow)
    assert r.returncode == 3 and "?? .work/issues/lemma.G2.assumption-auditor.r1.json" in r.stdout


def test_guard_catches_paper_edit_and_commits(proj):
    base = run(proj, "guard-begin").stdout.strip()
    (proj / "paper" / "main.tex").write_text("edited\n")
    r = run(proj, "guard-check", "--base", base, "--revert")
    assert r.returncode == 3 and " M paper/main.tex" in r.stdout
    assert (proj / "paper" / "main.tex").read_text() == "\\documentclass{llncs}\n"
    (proj / ".work" / "model.md").write_text("A9\n")
    commit_all(proj / ".work", "x")
    r = run(proj, "guard-check", "--base", base)
    assert r.returncode == 3 and "work repo HEAD moved" in r.stdout


def test_guard_begin_refuses_dirty_work_repo(proj):
    (proj / ".work" / "state.md").write_text("dirty\n")
    r = run(proj, "guard-begin")
    assert r.returncode == 2 and ".work/state.md" in r.stderr


def test_rev_diff_and_log_cover_both_repos(proj):
    base = run(proj, "rev").stdout.strip()
    p, w = base.split("+")
    assert len(p) == 7 and len(w) == 7
    (proj / "paper" / "main.tex").write_text("new\n")
    commit_all(proj, "add proof of lemma 1")
    (proj / ".work" / "claims.md").write_text("C1\n")
    commit_all(proj / ".work", "register lemma statements")
    names = run(proj, "diff", base, "--name-only").stdout.split()
    assert names == ["paper/main.tex", ".work/claims.md"]
    log = run(proj, "log", base).stdout
    assert "project" in log and "add proof of lemma 1" in log and "work" in log and "register lemma statements" in log
    assert run(proj, "rev").stdout.strip() != base


def test_normalize_exclude():
    n = repos.normalize_exclude
    assert n("a/.work/") == "/a/.work/"
    assert n("/a/.work/") == "/a/.work/"
    assert n("a/**/output/") == "/a/**/output/"
    assert n("output/") == "output/"  # only a trailing slash: matches at any depth, not anchored
    assert n("CLAUDE.md") == "CLAUDE.md"
    assert n("# a/b") == "# a/b"
    assert n("  a/b  ") == "/a/b"


def test_commit_refuses_with_tracked_workflow_file(proj):
    (proj / "CLAUDE.md").write_text("notes\n")
    git(proj, "add", "-f", "CLAUDE.md")
    git(proj, "commit", "-qm", "add notes")
    (proj / "paper" / "main.tex").write_text("edited\n")
    r = run(proj, "commit", "-m", "revise intro")
    assert r.returncode != 0 and "CLAUDE.md" in (r.stdout + r.stderr) and "untrack" in (r.stdout + r.stderr)
