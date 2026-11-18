import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WSTATUS = ROOT / "scripts" / "wstatus.py"


def sections(out):
    res, cur = {}, None
    for line in out.splitlines():
        if line.startswith("## "):
            cur = line[3:]
            res[cur] = []
        elif cur:
            res[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in res.items()}


def test_wstatus_runs_every_section_without_a_shell(tmp_path):
    p = tmp_path / "proj"
    (p / ".work" / "issues").mkdir(parents=True)
    (p / ".work" / "state.md").write_text("# State\n\n- updated: x\n")
    (p / ".work" / "claims.md").write_text("## C1\n- status: draft\n\n## C2\n- status: draft\n\n## C3\n- status: verified\n")
    (p / ".work" / "issues" / "legacy-open.json").write_text(json.dumps({"issues": [
        {"id": "G5/legacy/1", "severity": "major", "location": "x", "claim": None, "evidence": "e", "suggested_fix": "f"}]}))
    r = subprocess.run([sys.executable, str(WSTATUS), "--root", str(p)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    s = sections(r.stdout)
    assert list(s) == ["state", "agenda", "approvals log", "latest handoff", "claims", "ideas", "pending captures",
                       "decisions", "issues", "requests", "repos", "resources"]
    assert s["agenda"] == "no threads" and s["ideas"] == "(no .work/ideas.md)" and s["pending captures"] == "none"
    assert s["claims"] == "draft 2, verified 1"
    assert s["issues"].splitlines()[-1] == "open issues: blocking 0, major 1, minor 0"
    assert s["repos"].endswith("(exit 1)")  # not a git repo: reported in its section, the others still ran


def test_wstatus_needs_work_dir(tmp_path):
    r = subprocess.run([sys.executable, str(WSTATUS), "--root", str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 2
