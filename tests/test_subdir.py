"""Projects in a subdirectory of a shared git repo, next to sibling projects and coauthors' folders."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from test_codex_review import FAKE as FAKE_CODEX
from test_rw import FAKE as FAKE_CLAUDE

ROOT = Path(__file__).resolve().parent.parent
REPOS = ROOT / "scripts" / "repos.py"
HOOK = ROOT / "hooks" / "rw_hooks.py"
CODEX = ROOT / "skills" / "codex-review" / "codex_review.sh"
RW = ROOT / "bin" / "rw"
WORKFLOW_FILES = [".work/claims.md", ".work/state.md", ".work/contract.md", "CLAUDE.md", ".claude/settings.json",
                  "resources/BRIEF.md", "output/main.pdf", "paper/output/main.pdf"]
THIS, SIBLING = "reports/02-mitigations", "reports/03-attacks"


def run(proj, *args):
    return subprocess.run([sys.executable, str(REPOS), "--root", str(proj), *args], capture_output=True, text=True)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout


def commit_all(repo, msg):  # test setup only; the workflow commits through repos.py commit
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", msg)


def make_project(p, name):
    (p / "paper").mkdir(parents=True)
    (p / "paper" / "main.tex").write_text(f"{name}\n")
    r = run(p, "init")
    assert r.returncode == 0, r.stderr
    for f in WORKFLOW_FILES:
        (p / f).parent.mkdir(parents=True, exist_ok=True)
        (p / f).write_text(f"{f}\n")
    (p / ".work" / "issues").mkdir()
    (p / ".work" / "briefs").mkdir()
    (p / ".work" / "contract.md").write_text("- ai_tools_allowed: claude, codex\n")
    (p / ".work" / "briefs" / "S8-lemma.md").write_text("# Brief\n")


@pytest.fixture
def shared(tmp_path):
    """One repo: a coauthor folder, reports/CLAUDE.md, and two sibling projects under reports/."""
    repo = tmp_path / "repo"
    (repo / "other").mkdir(parents=True)
    (repo / "other" / "notes.tex").write_text("coauthor\n")
    (repo / "reports").mkdir()
    (repo / "reports" / "CLAUDE.md").write_text("shared rules for all reports\n")
    git(tmp_path, "init", "-q", str(repo))
    commit_all(repo, "add coauthor notes")
    this, sib = repo / THIS, repo / SIBLING
    make_project(this, "this")
    make_project(sib, "sibling")
    commit_all(repo, "add both papers")
    for p in (this, sib):
        commit_all(p / ".work", "add contract and playbook")
    return repo, this, sib


def test_excludes_are_prefixed_and_per_project(shared):
    repo, this, sib = shared
    lines = (repo / ".git" / "info" / "exclude").read_text().splitlines()
    for p in (THIS, SIBLING):
        for e in [f"/{p}/.work/", f"/{p}/CLAUDE.md", f"/{p}/.claude/", f"/{p}/resources/", f"/{p}/**/output/"]:
            assert lines.count(e) == 1, e
        assert lines.count(f"# research workflow (local only): {p}/") == 1
    assert "/.work/" not in lines and "output/" not in lines  # nothing unanchored that would hit other folders
    # only the papers are tracked; no workflow file of either project is visible
    assert sorted(git(repo, "ls-files").split()) == sorted(
        ["other/notes.tex", "reports/CLAUDE.md", f"{THIS}/paper/main.tex", f"{SIBLING}/paper/main.tex"])
    assert git(repo, "status", "--porcelain", "--untracked-files=all") == ""
    # an output/ folder outside the projects is not excluded
    (repo / "other" / "output").mkdir()
    (repo / "other" / "output" / "x.pdf").write_text("x")
    assert git(repo, "status", "--porcelain", "--untracked-files=all") == "?? other/output/x.pdf\n"
    # init is idempotent
    assert run(this, "init").stdout.strip() == "already set up"
    assert (repo / ".git" / "info" / "exclude").read_text().splitlines() == lines
    # each project removes only its own lines
    r = run(this, "unexclude")
    assert r.returncode == 0, r.stderr
    after = (repo / ".git" / "info" / "exclude").read_text().splitlines()
    assert not any(THIS in l for l in after)
    assert [l for l in lines if SIBLING in l] == [l for l in after if SIBLING in l]
    assert run(sib, "check").returncode == 0
    assert run(this, "check").returncode == 1
    run(this, "init")
    assert run(this, "check").returncode == 0


def test_check_reports_subdir_and_parent_claude_md(shared):
    repo, this, _ = shared
    r = run(this, "check")
    assert r.returncode == 0, r.stdout
    out = r.stdout.splitlines()
    assert out[0].startswith(f"project: {THIS}/ in the repo at ")
    assert "project repo: clean" in out and ".work repo: clean" in out
    assert "workflow files tracked by the project repo: none" in out
    assert [l for l in out if l.startswith("also loaded:")] == ["also loaded: reports/CLAUDE.md (CLAUDE.md above the project)"]


def test_sibling_changes_never_block_or_warn(shared):
    repo, this, sib = shared
    base = run(this, "guard-begin")
    assert base.returncode == 0, base.stderr
    base = base.stdout.strip()
    rev = run(this, "rev").stdout.strip()
    # coauthor edits, a sibling project's paper commit, untracked files and a tracked workflow file elsewhere
    (repo / "other" / "notes.tex").write_text("coauthor edit\n")
    (repo / "other" / "new.tex").write_text("new\n")
    (sib / "paper" / "main.tex").write_text("sibling edit\n")
    assert run(sib, "commit", "-m", "revise sibling paper").returncode == 0
    (repo / "other" / "CLAUDE.md").write_text("x\n")
    git(repo, "add", "-f", "other/CLAUDE.md")
    git(repo, "add", "-f", f"{SIBLING}/resources/BRIEF.md")
    (sib / "paper" / "draft.tex").write_text("dirty\n")
    assert git(repo, "status", "--porcelain") != ""
    r = run(this, "check")
    assert r.returncode == 0, r.stdout
    assert "project repo: clean" in r.stdout
    assert "workflow files tracked by the project repo: none" in r.stdout
    assert "resources/ files tracked by the project repo: none" in r.stdout
    assert run(this, "status").stdout == ""
    assert run(this, "guard-begin").returncode == 0
    assert run(this, "rev").stdout.strip() == rev  # a commit elsewhere does not move this project's commit
    g = run(this, "guard-check", "--base", base)
    assert g.returncode == 0 and "write guard: ok" in g.stdout, g.stdout
    assert run(this, "log", base).stdout == "" and run(this, "diff", base, "--name-only").stdout == ""
    # the sibling sees its own changes
    assert "dirty" in run(sib, "check").stdout


def test_guard_in_subdir_catches_and_reverts_only_this_project(shared):
    repo, this, sib = shared
    base = run(this, "guard-begin").stdout.strip()
    (this / "paper" / "main.tex").write_text("reviewer edit\n")
    (this / ".work" / "claims.md").write_text("C1 status: verified\n")
    (this / ".work" / "issues" / "lemma.G2.proof-checker.r1.json").write_text("{}\n")
    (repo / "other" / "notes.tex").write_text("coauthor edit\n")  # not ours: neither reported nor reverted
    r = run(this, "guard-check", "--base", base, "--allow", ".work/issues/lemma.G2.proof-checker.r1", "--revert")
    assert r.returncode == 3
    assert " M paper/main.tex" in r.stdout and " M .work/claims.md" in r.stdout and "other/" not in r.stdout
    assert "Reverted both repos" in r.stdout
    assert (this / "paper" / "main.tex").read_text() == "this\n"
    assert (repo / "other" / "notes.tex").read_text() == "coauthor edit\n"
    # a commit inside the project moves its HEAD
    (this / "paper" / "main.tex").write_text("new\n")
    assert run(this, "commit", "-m", "x").returncode == 0
    r = run(this, "guard-check", "--base", base)
    assert r.returncode == 3 and "project repo HEAD moved" in r.stdout
    names = run(this, "diff", base, "--name-only").stdout.split()
    assert names == ["paper/main.tex"]
    assert "project" in run(this, "log", base).stdout


def test_commit_stages_only_the_project(shared):
    repo, this, sib = shared
    (this / "paper" / "main.tex").write_text("proof\n")
    (this / "paper" / "lemma.tex").write_text("lemma\n")
    (this / "resources" / "new.pdf").write_text("excluded\n")
    (repo / "other" / "notes.tex").write_text("coauthor edit\n")
    (sib / "paper" / "main.tex").write_text("sibling staged\n")
    git(repo, "add", f"{SIBLING}/paper/main.tex")  # someone else's staged change stays staged and uncommitted
    r = run(this, "commit", "-m", "add proof of lemma 1")
    assert r.returncode == 0, r.stderr
    assert sorted(git(repo, "show", "--name-only", "--format=", "HEAD").split()) == [
        f"{THIS}/paper/lemma.tex", f"{THIS}/paper/main.tex"]
    assert git(repo, "log", "-1", "--format=%s").strip() == "add proof of lemma 1"
    st = git(repo, "status", "--porcelain")
    assert f"M  {SIBLING}/paper/main.tex" in st and " M other/notes.tex" in st
    assert run(this, "commit", "-m", "again").stdout.strip() == "nothing to commit"
    # paths outside the project, or in .work, are refused
    for bad in ("../03-attacks/paper/main.tex", str(repo / "other" / "notes.tex"), ".work/claims.md"):
        r = run(this, "commit", "-m", "x", bad)
        assert r.returncode == 2, bad
    # a deletion inside the project is committed, with an explicit path
    (this / "paper" / "lemma.tex").unlink()
    assert run(this, "commit", "-m", "drop lemma file", "paper").returncode == 0
    assert f"{THIS}/paper/lemma.tex" not in git(repo, "ls-files")


def test_top_level_project_is_unchanged(tmp_path):
    """A project at the repo root, inside a folder that has a CLAUDE.md (like the pilot inside ~/dotclaude)."""
    (tmp_path / "CLAUDE.md").write_text("outside the repo\n")
    p = tmp_path / "proj"
    (p / "paper").mkdir(parents=True)
    git(tmp_path, "init", "-q", str(p))
    assert run(p, "init").returncode == 0
    block = (p / ".git" / "info" / "exclude").read_text().split("# research workflow (local only)\n", 1)[1]
    assert block == "/.work/\n/CLAUDE.md\n/.claude/\n/resources/\noutput/\n"
    r = run(p, "check")
    assert r.stdout.splitlines() == ["project repo: clean", ".work repo: dirty (1 paths)",
                                     "workflow files tracked by the project repo: none",
                                     "resources/ files tracked by the project repo: none", "project repo excludes: ok"]
    (p / "paper" / "main.tex").write_text("x\n")
    assert run(p, "commit", "-m", "add paper").returncode == 0
    assert run(p, "rev").stdout.strip().split("+")[0] == git(p, "rev-parse", "--short=7", "HEAD").strip()


# ---------- hooks, codex review and rw in a subdirectory ----------

def hook_env(tmp_path, proj):
    e = {k: v for k, v in os.environ.items() if not k.startswith("RW_")}
    e.update(CLAUDE_PROJECT_DIR=str(proj), RW_HOOKS_STATE_DIR=str(tmp_path / "state"), RW_HOOKS_DEBUG="1",
             RW_NOTIFY_CMD="true", RW_USAGE_GLOBAL=str(tmp_path / "g.tsv"))
    return e


def hook(env, event, inp):
    r = subprocess.run([sys.executable, str(HOOK), event], input=json.dumps(inp), capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout) if r.stdout.strip().startswith("{") else r.stdout


def test_hooks_ignore_commits_and_changes_elsewhere(tmp_path, shared):
    repo, this, sib = shared
    env = hook_env(tmp_path, this)
    hook(env, "session-start", {"session_id": "s1", "source": "startup"})
    (sib / "paper" / "main.tex").write_text("sibling\n")
    run(sib, "commit", "-m", "revise sibling paper")
    (repo / "other" / "notes.tex").write_text("coauthor edit\n")
    assert hook(env, "stop", {"session_id": "s1"}) == ""
    (this / "paper" / "main.tex").write_text("ours\n")
    run(this, "commit", "-m", "add proof of lemma 1")
    out = hook(env, "stop", {"session_id": "s1"})
    assert out["decision"] == "block" and "1 commit(s)" in out["reason"]
    (this / "paper" / "extra.tex").write_text("x\n")
    hook(env, "pre-compact", {"session_id": "s1", "trigger": "auto"})
    snap = next((this / ".work" / "handoffs").glob("*-auto-precompact.md")).read_text()
    assert "- project " in snap and "add proof of lemma 1" in snap and "revise sibling paper" not in snap
    assert "?? paper/extra.tex" in snap and "other/" not in snap


def test_codex_review_in_subdir_with_dirty_sibling(tmp_path, shared):
    repo, this, sib = shared
    (sib / "paper" / "main.tex").write_text("sibling dirty\n")
    (repo / "other" / "notes.tex").write_text("coauthor dirty\n")
    fake = tmp_path / "codex"
    fake.write_text(FAKE_CODEX)
    fake.chmod(0o755)
    env = dict(os.environ, CODEX_BIN=str(fake), FAKE_TAMPER="")
    args = ["bash", str(CODEX), "--artifact", "paper/main.tex", "--slug", "lemma", "--round", "1",
            "--brief", ".work/briefs/S8-lemma.md", "--model", "m1", "--effort", "high"]
    r = subprocess.run(args, cwd=this, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rep = json.loads((this / ".work" / "issues" / "lemma.G3.codex.r1.json").read_text())
    assert rep["commit"] == run(this, "rev").stdout.strip()
    # tampering inside the project is still caught; the sibling's dirty file is left alone
    git(this / ".work", "add", "-A")
    git(this / ".work", "commit", "-qm", "review lemma, round 1")
    env["FAKE_TAMPER"] = "echo tampered >> paper/main.tex"
    r = subprocess.run(args[:7] + ["2"] + args[8:], cwd=this, env=env, capture_output=True, text=True)
    assert r.returncode == 3 and "paper/main.tex" in r.stderr, r.stderr
    assert (this / "paper" / "main.tex").read_text() == "this\n"
    assert (sib / "paper" / "main.tex").read_text() == "sibling dirty\n"


def test_rw_starts_in_subdir_and_points_to_projects(tmp_path, shared):
    repo, this, sib = shared
    (sib / "paper" / "main.tex").write_text("sibling dirty\n")
    fake = tmp_path / "claude"
    fake.write_text(FAKE_CLAUDE)
    fake.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("RW_", "FAKE_"))}
    env.update(RW_CLAUDE=str(fake), RW_NOTIFY_CMD="true", RW_POLL="0.1", FAKE_LOG=str(tmp_path / "calls"),
               RW_BUDGETS=str(tmp_path / "b.json"), RW_USAGE_GLOBAL=str(tmp_path / "g.tsv"), FAKE_PLAN="project-done")
    r = subprocess.run([sys.executable, str(RW)], cwd=this, env=env, capture_output=True, text=True, timeout=60,
                       stdin=subprocess.DEVNULL)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "project done" in r.stdout
    r = subprocess.run([sys.executable, str(RW)], cwd=repo, env=env, capture_output=True, text=True, timeout=60,
                       stdin=subprocess.DEVNULL)
    assert r.returncode == 2 and f"projects below this directory: {THIS}, {SIBLING}" in r.stderr
