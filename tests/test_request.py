import base64
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REQ = ROOT / "scripts" / "request.py"
RES = ROOT / "scripts" / "resources.py"
UPD = ROOT / "scripts" / "project_update.py"
HOOK = ROOT / "hooks" / "rw_hooks.py"
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

CONTRACT = """# Contract

## Requirements

| ID | Requirement | Source | Approved |
|---|---|---|---|
| R1 | Prove safety of the protocol | resources/BRIEF.md:3 | D1 |
| R2 | Deliver a paper section | resources/BRIEF.md:5 | D1 |
"""


def g(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                   capture_output=True)


@pytest.fixture
def proj(tmp_path):
    p = tmp_path / "proj"
    (p / ".work" / "decisions").mkdir(parents=True)
    (p / ".work" / "briefs").mkdir()
    (p / ".work" / "contract.md").write_text(CONTRACT)
    (p / ".work" / "claims.md").write_text("# Claims\n\n## C1\n- label: lem:safety\n- status: draft\n")
    (p / ".work" / "model.md").write_text("# Model\n\n- A1: synchrony\n")
    (p / ".work" / "state.md").write_text("# State\n\n- stage: 5 (S5 Properties)\n- active brief: none\n")
    (p / "resources").mkdir()
    (p / "resources" / "BRIEF.md").write_text("# Project brief\n\nProve safety.\n")
    (p / "paper").mkdir()
    (p / "paper" / "main.tex").write_text("x\n")
    subprocess.run(["git", "init", "-q", str(p)], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "repos.py"), "--root", str(p), "init"], check=True,
                   capture_output=True)
    subprocess.run([sys.executable, str(RES), "--root", str(p), "init"], check=True, capture_output=True)
    for repo in (p, p / ".work"):
        g(repo, "add", "-A")
        g(repo, "commit", "-qm", "init")
    return p


@pytest.fixture
def env(tmp_path, proj):
    e = {k: v for k, v in os.environ.items() if not k.startswith("RW_")}
    e.update(CLAUDE_PROJECT_DIR=str(proj), RW_HOOKS_STATE_DIR=str(tmp_path / "state"), RW_HOOKS_DEBUG="1",
             RW_NOTIFY_CMD="/usr/bin/true")
    return e


def run(env, proj, *args):
    return subprocess.run([sys.executable, str(REQ), "--root", str(proj), *args], capture_output=True, text=True,
                          env=env)


def hook(env, event, inp, **extra):
    r = subprocess.run([sys.executable, str(HOOK), event], input=json.dumps(inp), capture_output=True, text=True,
                       env=dict(env, **extra))
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout) if r.stdout.strip().startswith("{") else r.stdout


def ctx(out):
    return out["hookSpecificOutput"]["additionalContext"]


def transcript(tmp_path, content):
    p = tmp_path / "t.jsonl"
    entries = [{"type": "user", "message": {"role": "user", "content": "earlier prompt"}},
               {"type": "user", "message": {"role": "user", "content": content}},
               {"type": "user", "isMeta": True, "message": {"role": "user", "content": "skill text"}},
               {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}}]
    p.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return str(p)


def submit(env, tmp_path, text, blocks=()):
    content = [{"type": "text", "text": text}, *blocks] if blocks else text
    t = transcript(tmp_path, content)
    return hook(env, "prompt", {"session_id": "s1", "prompt": text, "transcript_path": t})


def manifest(proj):
    rows = [l.split("\t") for l in (proj / ".work" / "resources.manifest").read_text().splitlines()
            if l and not l.startswith("#")]
    return {r[0]: r for r in rows}


# ---------- hook: direct mode, raw:, commands, rw ----------

def test_plain_prompt_is_a_request(env, tmp_path, proj):
    out = submit(env, tmp_path, "tighten the intro of section 2")
    assert "request` skill" in ctx(out) and "request.py record --session s1" in ctx(out)
    assert "Rules card" in ctx(out)
    saved = json.loads((tmp_path / "state" / "s1.prompt.json").read_text())
    assert saved["prompt"] == "tighten the intro of section 2"


def test_raw_bypasses_the_harness(env, tmp_path, proj):
    out = submit(env, tmp_path, "raw: what is 2+2")
    assert "outside the harness" in ctx(out) and "request.py record" not in ctx(out)
    assert not (tmp_path / "state" / "s1.prompt.json").exists()
    assert not (proj / ".work" / "requests.md").exists()


def test_commands_and_rw_loop_are_not_requests(env, tmp_path, proj):
    assert "request.py record" not in ctx(submit(env, tmp_path, "/wstatus"))
    out = hook(env, "prompt", {"session_id": "s1", "prompt": "fix lemma 2"}, RW_LOOP="1")
    assert "request.py record" not in ctx(out)


def test_session_start_reminds_direct_mode(env, proj):
    (proj / "CLAUDE.md").write_text("# Project\n\n## Build\n\nx\n")
    out = ctx(hook(env, "session-start", {"session_id": "s1", "source": "startup"}))
    assert "Direct mode" in out and "project_update.py" in out
    subprocess.run([sys.executable, str(UPD), "--root", str(proj)], check=True, capture_output=True)
    out = ctx(hook(env, "session-start", {"session_id": "s2", "source": "startup"}))
    assert "Direct mode" in out and "project_update.py" not in out
    out = ctx(hook(env, "session-start", {"session_id": "s3", "source": "startup"}, RW_LOOP="1"))
    assert "Direct mode" not in out


# ---------- record ----------

def test_record_appends_to_brief_and_registry(env, tmp_path, proj):
    submit(env, tmp_path, "tighten the intro of section 2")
    r = run(env, proj, "record", "--session", "s1", "--slug", "intro wording", "--title", "intro wording")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["id"] == "RQ1" and out["mode"] == "default" and out["files"] == [] and out["dir"] is None
    brief = (proj / "resources" / "BRIEF.md").read_text()
    assert f"## Requests {date.today().isoformat()}" in brief
    assert "### RQ1 |" in brief and "tighten the intro of section 2" in brief
    reg = (proj / ".work" / "requests.md").read_text()
    assert "## RQ1" in reg and "- status: open" in reg and "- rev before: " in reg
    m = manifest(proj)["resources/BRIEF.md"]
    assert m[4] == "refreshed" and "RQ1" in m[7]
    scan = subprocess.run([sys.executable, str(RES), "--root", str(proj), "scan"], capture_output=True, text=True)
    assert "0 new, 0 edited" in scan.stdout
    # a second request the same day: same heading, next ID
    submit(env, tmp_path, "full: review lemma 2")
    out = json.loads(run(env, proj, "record", "--session", "s1", "--slug", "lemma 2", "--title", "t").stdout)
    assert out["id"] == "RQ2" and out["mode"] == "full"
    assert (proj / "resources" / "BRIEF.md").read_text().count("## Requests ") == 1


def test_pasted_image_lands_in_resources_with_manifest_entry(env, tmp_path, proj):
    img = {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                       "data": base64.b64encode(PNG).decode()}}
    submit(env, tmp_path, "quick: use this figure [Image #1]", [img])
    r = run(env, proj, "record", "--session", "s1", "--slug", "new figure", "--title", "figure")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    rel = f"resources/{date.today().isoformat()}-new-figure/image-1.png"
    assert out["files"] == [rel] and out["mode"] == "quick"
    assert (proj / rel).read_bytes() == PNG
    m = manifest(proj)[rel]
    assert m[4] == "request" and m[5] == "RQ1"
    assert f"`{rel}`" in (proj / "resources" / "BRIEF.md").read_text()
    assert rel in (proj / ".work" / "requests.md").read_text()


def test_long_paste_and_attached_file_are_saved(env, tmp_path, proj):
    outside = tmp_path / "review.pdf"
    outside.write_bytes(b"%PDF-1.4 x")
    long = "\n".join(f"line {i}" for i in range(30))
    text = f"address this review {outside}\n<pasted_content id=\"x\">\n{long}\n</pasted_content id=\"x\">"
    submit(env, tmp_path, text)
    out = json.loads(run(env, proj, "record", "--session", "s1", "--slug", "review", "--title", "t").stdout)
    names = sorted(Path(f).name for f in out["files"])
    assert names == ["paste-1.md", "review.pdf"]
    brief = (proj / "resources" / "BRIEF.md").read_text()
    assert "line 29" not in brief and "pasted text, saved to" in brief
    assert all(manifest(proj)[f][5] == "RQ1" for f in out["files"])


def test_follow_up_extends_the_request(env, tmp_path, proj):
    submit(env, tmp_path, "rename the lemma")
    run(env, proj, "record", "--session", "s1", "--slug", "rename", "--title", "rename")
    submit(env, tmp_path, "call it the chain growth lemma")
    out = json.loads(run(env, proj, "record", "--session", "s1", "--slug", "rename", "--title", "x",
                         "--follow-up", "RQ1").stdout)
    assert out["id"] == "RQ1" and out["follow_up"]
    assert "### RQ1 follow-up |" in (proj / "resources" / "BRIEF.md").read_text()
    assert (proj / ".work" / "requests.md").read_text().count("## RQ") == 1


def test_text_file_fallback(env, tmp_path, proj):
    f = tmp_path / "p.txt"
    f.write_text("add a remark after lemma 1")
    out = json.loads(run(env, proj, "record", "--text-file", str(f), "--slug", "remark", "--title", "t").stdout)
    assert out["id"] == "RQ1"


# ---------- gates ----------

@pytest.mark.parametrize("args, want, crit", [
    (["--kind", "prose", "--tex"], "G0, G1, G4", "no"),
    (["--kind", "prose", "--tex", "--critical"], "G0, G1, G4", "no"),
    (["--kind", "technical", "--tex"], "G0, G1, G2, G4", "no"),
    (["--kind", "technical", "--tex", "--critical"], "G0, G1, G2, G3, G4", "yes"),
    (["--kind", "technical"], "G1, G2, G4", "no"),
    (["--kind", "technical", "--tex", "--critical", "--mode", "quick"], "G0, G1", "no"),
    (["--kind", "prose", "--tex", "--mode", "full"], "G0, G1, G2, G3, G4", "yes"),
])
def test_gates(env, proj, args, want, crit):
    r = run(env, proj, "gates", *args)
    assert r.stdout.splitlines() == [f"- gates: {want}", f"- critical: {crit}"]


def test_prose_only_request_runs_g0_g1_g4(env, proj):
    out = run(env, proj, "gates", "--kind", "prose", "--tex").stdout
    assert "G2" not in out and "G3" not in out and "- gates: G0, G1, G4" in out


# ---------- raise: scope and deliverables ----------

def test_deliverable_change_is_a_blocking_card(env, tmp_path, proj):
    submit(env, tmp_path, "turn the paper section into a journal version")
    run(env, proj, "record", "--session", "s1", "--slug", "journal", "--title", "journal version")
    r = run(env, proj, "raise", "RQ1", "--affects", "R2", "--deliverable-change",
            "--question", "Should the deliverable become a journal version of the paper?",
            "--reason", "the request changes the deliverable named in the contract")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["class"] == "blocking" and out["card"] == "D1"
    card = (proj / ".work" / "decisions" / "D1.md").read_text()
    assert "- class: blocking" in card and "- status: open" in card
    lint = subprocess.run([sys.executable, str(ROOT / "scripts" / "decisions.py"), "--root", str(proj), "lint", "D1"],
                          capture_output=True, text=True)
    assert lint.returncode == 0, lint.stdout + lint.stderr
    assert "- decisions: D1" in (proj / ".work" / "requests.md").read_text()


def test_raise_refuses_other_impacts_and_unknown_ids(env, tmp_path, proj):
    submit(env, tmp_path, "x")
    run(env, proj, "record", "--session", "s1", "--slug", "x", "--title", "x")
    assert run(env, proj, "raise", "RQ1", "--affects", "R2", "--question", "Q?", "--reason", "r").returncode == 2
    assert run(env, proj, "raise", "RQ1", "--affects", "R9", "--scope-change", "--question", "Q?",
               "--reason", "r").returncode == 2


# ---------- context, close, list, trace ----------

def test_context_reports_stage_in_progress(env, proj):
    (proj / ".work" / "briefs" / "S5-defs.md").write_text(
        "# Brief\n\n- stage: S5\n- request: none\n- status: open\n- artifact files: paper/defs.tex\n- claims: C1\n")
    out = json.loads(run(env, proj, "context").stdout)
    assert out["stage in progress"] and out["briefs not done"][0]["claims"] == "C1"
    (proj / ".work" / "briefs" / "S5-defs.md").write_text("# Brief\n\n- status: done\n")
    assert not json.loads(run(env, proj, "context").stdout)["stage in progress"]


def test_close_records_commits_and_trace_finds_the_request(env, tmp_path, proj):
    submit(env, tmp_path, "add a remark after lemma 1")
    run(env, proj, "record", "--session", "s1", "--slug", "remark", "--title", "remark after lemma 1")
    (proj / "paper" / "main.tex").write_text("y\n")
    g(proj, "add", "paper/main.tex")
    g(proj, "commit", "-qm", "add remark after lemma 1")
    sha = subprocess.run(["git", "-C", str(proj), "rev-parse", "--short", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    run(env, proj, "set", "RQ1", "briefs=RQ1-remark", "claims=C1")
    r = run(env, proj, "close", "RQ1", "--status", "done", "--summary", "remark added")
    assert r.returncode == 0, r.stderr
    rec = json.loads(r.stdout)
    assert rec["status"] == "done" and f"project {sha}" in rec["commits"] and "paper/main.tex" in rec["changed"]
    for token in ("paper/main.tex", sha, "C1", "RQ1-remark"):
        assert run(env, proj, "trace", token).stdout.startswith("RQ1 |"), token
    assert "no request touches" in run(env, proj, "trace", "C9").stdout
    assert run(env, proj, "list").stdout.startswith("RQ1 |")
    assert "remark after lemma 1" in run(env, proj, "show", "RQ1").stdout


def test_deferred_request_is_listed_at_session_start(env, tmp_path, proj):
    submit(env, tmp_path, "x")
    run(env, proj, "record", "--session", "s1", "--slug", "x", "--title", "x")
    run(env, proj, "close", "RQ1", "--status", "deferred", "--summary", "after S5")
    assert "deferred" in run(env, proj, "list", "--status", "deferred").stdout
    assert "RQ1 (deferred)" in ctx(hook(env, "session-start", {"session_id": "s9", "source": "startup"}))


# ---------- one-time project update ----------

def test_project_update_is_idempotent(env, proj):
    (proj / "CLAUDE.md").write_text("# Project\n\n## Build\n\nmake\n\n## Project-specific rules\n\n- none\n")
    tpl = ROOT / "templates" / "project" / ".work"
    (proj / ".work" / "approvals.md").write_text(
        "\n".join(l for l in (tpl / "approvals.md").read_text().splitlines() if not l.startswith("| A request ")) + "\n")
    (proj / ".work" / "briefs" / "_template.md").write_text("# Brief\n\n- stage: <s>\n- status: <s>\n")
    g(proj / ".work", "add", "-A")
    g(proj / ".work", "commit", "-qm", "old layout")
    r = subprocess.run([sys.executable, str(UPD), "--root", str(proj)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    md = (proj / "CLAUDE.md").read_text()
    assert md.index("## Direct mode") < md.index("## Build")
    assert (proj / ".work" / "requests.md").is_file()
    assert "| A request that changes the scope or a deliverable | blocking |" in (proj / ".work" / "approvals.md").read_text()
    assert "- request:" in (proj / ".work" / "briefs" / "_template.md").read_text()
    log = subprocess.run(["git", "-C", str(proj / ".work"), "log", "-1", "--format=%s"], capture_output=True, text=True)
    assert log.stdout.strip() == "add request registry"
    again = subprocess.run([sys.executable, str(UPD), "--root", str(proj)], capture_output=True, text=True)
    assert again.stdout.strip() == "up to date"
    assert (proj / "CLAUDE.md").read_text() == md


def test_project_update_refuses_tracked_claude_md(env, proj):
    (proj / "CLAUDE.md").write_text("# Project\n")
    g(proj, "add", "-f", "CLAUDE.md")
    g(proj, "commit", "-qm", "add notes")
    r = subprocess.run([sys.executable, str(UPD), "--root", str(proj)], capture_output=True, text=True)
    assert r.returncode == 1 and "tracked" in r.stderr
    assert (proj / "CLAUDE.md").read_text() == "# Project\n"
    assert not (proj / ".work" / "requests.md").exists()


def test_mode_needs_a_prefix():
    sys.path.insert(0, str(ROOT / "scripts"))
    import request
    assert request.mode_of("quick: fix the figure") == "quick"
    assert request.mode_of("  Full: prove lemma 2") == "full"
    assert request.mode_of("a quick question about lemma 2") == "default"
    assert request.mode_of("do a full review of lemma 2") == "default"


def test_project_update_renames_deliverable_ids(env, proj):
    (proj / "CLAUDE.md").write_text("# Project\n\n## Direct mode\n\nx\n")
    (proj / ".work" / "contract.md").write_text(
        "# Contract\n\n## Requirements\n\n| ID | Requirement | Source | Deliverable |\n|---|---|---|---|\n"
        "| R1 | Prove safety | resources/BRIEF.md:3 | D1, D2 |\n\n## Deliverables\n\n"
        "| ID | Deliverable | Covers | Milestone | Due |\n|---|---|---|---|---|\n| D1 | report | R1 | M1 | 2026-12-01 |\n"
        "| D2 | proof | R1 | M1 | 2026-12-01 |\n\n## Approval\n\n- changes since approval: D3 accepted\n")
    r = subprocess.run([sys.executable, str(UPD), "--root", str(proj), "--no-commit"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    c = (proj / ".work" / "contract.md").read_text()
    assert "| DL1, DL2 |" in c and "| DL1 | report |" in c and "| DL2 | proof |" in c and "D3 accepted" in c
    again = subprocess.run([sys.executable, str(UPD), "--root", str(proj), "--no-commit"], capture_output=True, text=True)
    assert "renamed" not in again.stdout and (proj / ".work" / "contract.md").read_text() == c


def test_project_update_leaves_decision_columns_alone(env, proj):
    before = (proj / ".work" / "contract.md").read_text()
    subprocess.run([sys.executable, str(UPD), "--root", str(proj), "--no-commit"], check=True, capture_output=True)
    assert (proj / ".work" / "contract.md").read_text() == before


def test_session_start_lists_unprocessed_resources(env, proj):
    (proj / "resources" / "sow-v2.pdf").write_bytes(b"%PDF new")
    (proj / "resources" / "BRIEF.md").write_text("# Project brief\n\nchanged\n")
    out = ctx(hook(env, "session-start", {"session_id": "s1", "source": "startup"}))
    assert "Unprocessed inputs in resources/" in out and "new resources/sow-v2.pdf" in out
    assert "edited resources/BRIEF.md" in out
    out = ctx(hook(env, "session-start", {"session_id": "s2", "source": "startup"}, RW_LOOP="1"))
    assert "Unprocessed inputs" not in out
