#!/usr/bin/env python3
"""One-time update of an existing research workflow project (.work/) to the current templates. Stdlib only. Idempotent.

Usage (run from the project root, or pass --root):
  project_update.py [--no-commit]

Conversation mode and the agenda:
- the project CLAUDE.md (or .claude/CLAUDE.md) gets the "## Working mode" section of templates/project/CLAUDE.md. It replaces
  an older "## Direct mode" section, else goes before "## Build" (else before "## Project-specific rules", else at the end).
  Nothing else in it changes.
- .work/threads.md is created from the playbook in state.md (`- playbook:`): one thread per stage, stages before the current
  one (`- stage:`) done (agenda.py seed --current). Without a known playbook it starts empty.
- .work/ideas.md and .work/sessions/README.md are created from the templates; .work/.gitignore gets `issues/probes/`.
- .work/requests.md is created from the template.
- .work/approvals.md gets the request rows of the template's Class table that it lacks.
- .work/briefs/_template.md gets the `- request:` field.
- .work/resources.manifest is created (resources.py init) if the project has none.
- .work/contract.md: deliverable IDs D<n> become DL<n> (the Deliverables table's ID column and the Requirements
  table's Deliverable column only), because D<n> means a decision card everywhere else.
The .work files it changed are committed in the .work repo ("update workflow files to the current templates"), only those
files, unless --no-commit.
CLAUDE.md is in neither repo. If the project repo tracks the CLAUDE.md it would edit, nothing changes and it exits 1:
workflow text must never enter the project's shared history; untrack the file first (intake, step on tracked files).
Prints one line per change, or "up to date".
"""
import argparse
import contextlib
import io
import re
import subprocess
import sys
from pathlib import Path

DOTCLAUDE = Path(__file__).resolve().parent.parent
TEMPLATE = DOTCLAUDE / "templates" / "project"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import resources  # noqa: E402
import agenda  # noqa: E402


def section(text, heading):
    m = re.search(rf"(?ms)^{re.escape(heading)}\s*$.*?(?=^## |\Z)", text)
    return m.group(0).rstrip("\n") + "\n\n" if m else None


class TrackedError(Exception):
    pass


def tracked(p):
    r = subprocess.run(["git", "-C", str(p.parent), "ls-files", "--error-unmatch", "--", p.name],
                       capture_output=True, text=True)
    return p.parent.is_dir() and r.returncode == 0


def update_claude_md(root):
    p = next((x for x in (root / "CLAUDE.md", root / ".claude" / "CLAUDE.md") if x.is_file()), root / "CLAUDE.md")
    text = p.read_text() if p.is_file() else ""
    if "## Working mode" in text:
        return None
    if tracked(p):
        raise TrackedError(f"{p.relative_to(root)} is tracked by the project repo; adding workflow text would put it in "
                           "shared history. Untrack it first (git rm --cached, then repos.py init for the excludes).")
    sec = section((TEMPLATE / "CLAUDE.md").read_text(), "## Working mode")
    m = re.search(r"(?ms)^## Direct mode\s*$.*?(?=^## |\Z)", text)
    if m:
        text = text[:m.start()] + sec + text[m.end():]
        p.write_text(text.rstrip("\n") + "\n")
        return p
    for anchor in ("## Build", "## Project-specific rules"):
        m = re.search(rf"(?m)^{re.escape(anchor)}\s*$", text)
        if m:
            text = text[:m.start()] + sec + text[m.start():]
            break
    else:
        text = text.rstrip("\n") + ("\n\n" if text else "") + sec
    p.write_text(text.rstrip("\n") + "\n")
    return p


def update_approvals(root):
    p = root / ".work" / "approvals.md"
    if not p.is_file():
        return None
    text = p.read_text()
    rows = [r for r in (TEMPLATE / ".work" / "approvals.md").read_text().splitlines()
            if r.startswith("| A request ") and r not in text]
    if not rows:
        return None
    lines = text.splitlines()
    idx = max((i for i, l in enumerate(lines) if re.match(r"^\|.*\|\s*(blocking|checkpoint|logged)\s*\|\s*$", l)),
              default=None)
    if idx is None:
        return None
    lines[idx + 1:idx + 1] = rows
    p.write_text("\n".join(lines) + "\n")
    return p


def update_contract_ids(root):
    """Rename deliverable IDs D<n> to DL<n> in the column headed "ID" of the Deliverables table and the column headed
    "Deliverable" of the Requirements table. Other columns and sections are left alone."""
    p = root / ".work" / "contract.md"
    if not p.is_file():
        return None
    lines, section, col, changed = p.read_text().splitlines(), None, None, False
    want = {"Deliverables": "ID", "Requirements": "Deliverable"}
    for i, line in enumerate(lines):
        if line.startswith("## "):
            section, col = line[3:].strip(), None
            continue
        if section not in want or not line.startswith("|"):
            continue
        cells = line.split("|")
        if col is None:
            heads = [c.strip() for c in cells]
            col = heads.index(want[section]) if want[section] in heads else -1
            continue
        if col < 0 or col >= len(cells) or set(cells[1].strip()) <= set("-:"):
            continue
        new = re.sub(r"\bD(\d+)\b", r"DL\1", cells[col])
        if new != cells[col]:
            cells[col] = new
            lines[i] = "|".join(cells)
            changed = True
    if not changed:
        return None
    p.write_text("\n".join(lines) + "\n")
    return p


def update_agenda(root):
    """Create threads.md, ideas.md, sessions/README.md and the probes ignore line. Returns the changed .work paths."""
    work, changed = root / ".work", []
    if not (work / "threads.md").exists():
        st = (work / "state.md").read_text() if (work / "state.md").is_file() else ""
        pb = re.search(r"^- playbook:\s*([\w-]+)", st, re.M)
        cur = re.search(r"^- stage:.*?\b(S\d+)\b", st, re.M)
        seeded = False
        if pb and (agenda.PLAYBOOKS / f"{pb.group(1)}.md").is_file():
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    agenda.do_seed(root, pb.group(1), cur.group(1) if cur else None, source="migration")
                seeded = True
            except agenda.UsageError:
                pass
        if not seeded:
            (work / "threads.md").write_text((TEMPLATE / ".work" / "threads.md").read_text())
        changed.append(work / "threads.md")
    for rel in ("ideas.md", "sessions/README.md"):
        if not (work / rel).exists():
            (work / rel).parent.mkdir(parents=True, exist_ok=True)
            (work / rel).write_text((TEMPLATE / ".work" / rel).read_text())
            changed.append(work / rel)
    gi = work / ".gitignore"
    if gi.is_file() and "issues/probes/" not in gi.read_text().split():
        gi.write_text(gi.read_text().rstrip("\n") + "\nissues/probes/\n")
        changed.append(gi)
    return changed


def update_brief_template(root):
    p = root / ".work" / "briefs" / "_template.md"
    if not p.is_file():
        return None
    text = p.read_text()
    if re.search(r"(?m)^- request:", text):
        return None
    line = "- request: <RQ-ID if the brief serves a request | none>\n"
    m = re.search(r"(?m)^- stage:.*\n", text)
    text = text[:m.end()] + line + text[m.end():] if m else text.rstrip("\n") + "\n" + line
    p.write_text(text)
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--no-commit", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if not (root / ".work").is_dir():
        print("project_update: no .work/ here: run from the project root", file=sys.stderr)
        return 2
    changed = []
    try:
        c = update_claude_md(root)
    except TrackedError as e:
        print(f"project_update: {e} Nothing changed.", file=sys.stderr)
        return 1
    if c:
        print(f"added the Working mode section to {c.relative_to(root)}")
    reg = root / ".work" / "requests.md"
    if not reg.exists():
        reg.write_text((TEMPLATE / ".work" / "requests.md").read_text())
        changed.append(reg)
        print("created .work/requests.md")
    for fn, what in ((update_approvals, "added request rows to .work/approvals.md"),
                     (update_brief_template, "added the request field to .work/briefs/_template.md"),
                     (update_contract_ids, "renamed deliverable IDs in .work/contract.md to DL<n>")):
        p = fn(root)
        if p:
            changed.append(p)
            print(what)
    for p in update_agenda(root):
        changed.append(p)
        print(f"created or updated .work/{p.relative_to(root / '.work')}")
    if not (root / resources.MANIFEST).exists():
        if resources.do_init(root) == 0:
            changed.append(root / resources.MANIFEST)
    if not changed and not c:
        print("up to date")
    if changed and not a.no_commit and (root / ".work" / ".git").exists():
        rel = [str(p.relative_to(root / ".work")) for p in changed]
        g = ["git", "-C", str(root / ".work")]
        subprocess.run(g + ["add", "--"] + rel, check=True)
        subprocess.run(g + ["commit", "-qm", "update workflow files to the current templates", "--"] + rel, check=True)
        print("committed in the .work repo: update workflow files to the current templates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
