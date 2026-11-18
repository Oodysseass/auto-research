#!/usr/bin/env python3
"""The two git repos of a research workflow project. Stdlib only.

A project has two repos. The project repo holds the paper and code; it is the one the human shares.
`.work/` is a separate, local repo for workflow state. Workflow files never enter the project repo:
`.git/info/exclude` of the project repo (never a committed .gitignore) excludes EXCLUDES below.
`resources/` is excluded too: it is an append-only drop folder for inputs, tracked by .work/resources.manifest.

The project root is the directory that contains `.work/`. The repo root is `git rev-parse --show-toplevel`. They differ
when the project lives in a subdirectory of a larger repo (`reports/02-mitigations/`); several projects may share one repo.
Then the exclude lines are prefixed with the project's path, every check of the project repo (status, tracked files, the
write guard, rev, diff, log) covers only the project's subdirectory, and the project's commit (`rev`) is the last commit
that touched it. Changes elsewhere in the repo (coauthors' folders, sibling projects) never block or warn.
For a project at the repo root nothing changes.

Usage (run from the project root, or pass --root):
  repos.py init                      make .work/ a git repo (if it is not one) and add this project's EXCLUDES to the
                                     project repo's .git/info/exclude. Idempotent. Never commits, never untracks anything.
                                     Prints what is already tracked by the project repo under workflow or resources paths.
  repos.py unexclude                 remove this project's lines (and only those) from .git/info/exclude.
  repos.py commit -m MSG [PATH ...]  commit in the project repo: stage the PATHs (default: the whole project directory),
                                     never anything outside the project directory and never an excluded path, and commit
                                     only them. Other staged changes in the repo stay staged and uncommitted.
  repos.py status                    `git status --porcelain --untracked-files=all` of both repos, as project-relative paths
                                     (.work repo lines are prefixed with .work/). Prints nothing when both are clean.
  repos.py rev [--full]              the combined commit ID `<project>+<work>` (short hashes; `none` for a repo without
                                     commits). Use it wherever a file records "the commit" (issue reports, verified_by,
                                     approvals Log, review log rows).
  repos.py check                     one block for /wstatus: cleanliness of both repos, workflow files tracked by the
                                     project repo (must be none), resources/ files tracked by it, missing exclude lines,
                                     and, for a project in a subdirectory, its path and any CLAUDE.md above it in the repo
                                     (loaded by Claude Code too; reported, not an error).
                                     Exit 1 if .work/ is not a repo, an exclude line is missing, or a workflow file is tracked.
  repos.py guard-begin               write guard before dispatch: exit 2 unless both repos are clean; print the base
                                     (`repos.py rev --full`).
  repos.py guard-check --base B [--allow PREFIX ...] [--revert]
                                     write guard after the reviewer returns. Allowed: new untracked files under .work/issues/
                                     whose names start with an --allow prefix (e.g. .work/issues/lemma.G2.proof-checker.r2).
                                     Anything else, in either repo, or a moved HEAD, is a violation: exit 3 and list it.
                                     --revert on a violation: restore tracked paths to the base and remove every untracked
                                     file in both repos (the reviewer's own report included). HEAD is never reset.
  repos.py diff <base> [--name-only | --stat]
                                     changes since a combined base, in both repos, as project-relative paths.
  repos.py log <base>                commits since a combined base, in both repos, one line each, prefixed `project` or `work`.

Exit 0 on success, 1 on a failed check, 2 on usage errors or a dirty tree at guard-begin, 3 on a write-guard violation.
"""
import argparse
import subprocess
import sys
from pathlib import Path
# Excluded from the project repo through .git/info/exclude. Paths relative to the project root.
EXCLUDES = ["/.work/", "/CLAUDE.md", "/.claude/", "/resources/", "output/"]
EXCLUDE_HEADER = "# research workflow (local only)"
# Paths that are workflow files: the project repo must never track them.
WORKFLOW_PATHS = (".work/", "CLAUDE.md", ".claude/", "resources/BRIEF.md")
WORK_GITIGNORE = ".rw/\n.DS_Store\nissues/probes/\n"
# Seconds before a git call is abandoned. None: no limit. The hooks set it.
TIMEOUT = None


class UsageError(Exception):
    pass


def git(cwd, *args, check=False):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=TIMEOUT)
    if check and r.returncode != 0:
        raise UsageError(f"git {' '.join(args)} in {cwd}: {r.stderr.strip()}")
    return r


def out(cwd, *args):
    r = git(cwd, *args)
    return r.stdout if r.returncode == 0 else None


def toplevel(path):
    """The top level of the git work tree that contains `path`, or None."""
    top = out(path, "rev-parse", "--show-toplevel")
    return Path(top.strip()).resolve() if top and top.strip() else None


def is_repo_root(path):
    """True if `path` is the top level of a git work tree."""
    top = toplevel(path)
    return top is not None and top == Path(path).resolve()


def layout(root):
    """(repo root, project subdirectory) of the project at `root`. The subdirectory is relative to the repo root, with a
    trailing slash, or "" for a project at the repo root. (None, "") if `root` is not inside a git work tree."""
    top = toplevel(root)
    if top is None:
        return None, ""
    rel = Path(root).resolve().relative_to(top).as_posix()
    return top, "" if rel == "." else rel + "/"


def spec(sub):
    """Pathspec arguments that limit a git command run at the repo root to the project's subdirectory."""
    return ["--", f":(literal){sub.rstrip('/')}"] if sub else []


def head(cwd):
    h = out(cwd, "rev-parse", "--verify", "-q", "HEAD")
    return h.strip() if h else None


def repo_head(cwd, sub=""):
    """HEAD, or for a project in a subdirectory the last commit at or before HEAD that touched it."""
    if not sub or not head(cwd):
        return head(cwd)
    h = out(cwd, "log", "-1", "--format=%H", "HEAD", *spec(sub))
    return h.strip() or None if h else None


def repos(root):
    """(name, directory to run git in, project subdirectory, display prefix) for the project repo and the .work repo.
    Git reports paths relative to the repo root; a display path drops the subdirectory and adds the prefix."""
    root = Path(root)
    top, sub = layout(root)
    return [("project", top or root, sub, ""), ("work", root / ".work", "", ".work/")]


def require(root):
    root = Path(root)
    top, _ = layout(root)
    if top is None or top == (root / ".work").resolve():
        raise UsageError(f"{root} is not inside a git repo")
    if not is_repo_root(root / ".work"):
        raise UsageError(f"{root / '.work'} is not a git repo. Run: python3 ~/dotclaude/scripts/repos.py init")


def raw_status(cwd, sub):
    """(code, path relative to the repo root, original path or None) for each changed path, limited to `sub`."""
    s = out(cwd, "status", "--porcelain", "-z", "--untracked-files=all", *spec(sub)) or ""
    parts = s.split("\0")
    res, i = [], 0
    while i < len(parts):
        e = parts[i]
        i += 1
        if len(e) < 4:
            continue
        code, path, orig = e[:2], e[3:], None
        if "R" in code or "C" in code:
            orig = parts[i] if i < len(parts) else None
            i += 1
        res.append((code, path, orig))
    return res


def display(path, sub, prefix):
    return prefix + (path[len(sub):] if sub and path.startswith(sub) else path)


def status_lines(root):
    """Porcelain lines of both repos (the project repo limited to the project), project-relative paths."""
    lines = []
    for name, cwd, sub, prefix in repos(root):
        if name == "work" and not is_repo_root(cwd):
            continue
        for code, path, orig in raw_status(cwd, sub):
            p = display(path, sub, prefix)
            lines.append((code, f"{display(orig, sub, prefix)} -> {p}" if orig else p))
    return lines


def rev(root, full=False):
    parts = []
    for _, cwd, sub, _ in repos(root):
        h = repo_head(cwd, sub)
        parts.append((h if full else h[:7]) if h else "none")
    return "+".join(parts)


def split_base(base):
    parts = base.split("+")
    if len(parts) != 2 or not all(parts):
        raise UsageError(f"base must look like <project>+<work>: {base!r}")
    return [None if p == "none" else p for p in parts]


def exclude_file(root):
    p = out(root, "rev-parse", "--git-path", "info/exclude")
    if p is None:
        raise UsageError(f"{root} is not a git repo")
    p = Path(p.strip())
    return p if p.is_absolute() else Path(root) / p


def gitignore_escape(path):
    return "".join("\\" + c if c in "*?[]\\!#" else c for c in path)


def project_excludes(root):
    """This project's exclude lines and their header. At the repo root: EXCLUDES as they are."""
    _, sub = layout(root)
    if not sub:
        return EXCLUDES, EXCLUDE_HEADER
    esc = gitignore_escape(sub)
    lines = ["/" + esc + e[1:] if e.startswith("/") else f"/{esc}**/{e}" for e in EXCLUDES]
    return lines, f"{EXCLUDE_HEADER}: {sub}"


def normalize_exclude(line):
    """Canonical form of an exclude line. Git anchors a pattern that has a slash before its last character to the
    repo root whether or not it starts with one, so `a/.work/` and `/a/.work/` are the same pattern. Canonical: with
    the leading slash. A pattern whose only slash is a trailing one (`output/`) matches at any depth and is unchanged."""
    s = line.strip()
    if not s or s.startswith("#") or s.startswith("/") or s.startswith("!"):
        return s
    return "/" + s if "/" in s.rstrip("/") else s


def missing_excludes(root):
    f = exclude_file(root)
    have = {normalize_exclude(l) for l in f.read_text().splitlines()} if f.is_file() else set()
    return [e for e in project_excludes(root)[0] if normalize_exclude(e) not in have]


def normalize_excludes(f, wanted):
    """Rewrite lines of the exclude file that equal a wanted line in another form (no leading slash) to the
    wanted form. Returns the rewritten lines as (old, new)."""
    if not f.is_file():
        return []
    canon = {normalize_exclude(w): w for w in wanted}
    lines, changed = f.read_text().splitlines(), []
    for k, l in enumerate(lines):
        w = canon.get(normalize_exclude(l))
        if w is not None and l != w:
            changed.append((l, w))
            lines[k] = w
    if changed:
        f.write_text("\n".join(lines) + "\n")
    return changed


def tracked(root):
    """(workflow files, resources files) tracked by the project repo under the project, project-relative paths."""
    files = [f for f in (out(root, "ls-files", "-z") or "").split("\0") if f]
    wf = [f for f in files if any(f == w or (w.endswith("/") and f.startswith(w)) for w in WORKFLOW_PATHS)]
    res = [f for f in files if f.startswith("resources/") and f not in wf]
    return wf, res


def parent_claude_md(root):
    """CLAUDE.md files above a project in a subdirectory, up to the repo root, relative to the repo root."""
    top, sub = layout(root)
    found = []
    if not sub:
        return found
    d = Path(root).resolve().parent
    while True:
        for f in (d / "CLAUDE.md", d / ".claude" / "CLAUDE.md"):
            if f.is_file():
                found.append(f.relative_to(top).as_posix())
        if d == top:
            return found
        d = d.parent


# ---------- commands ----------

def do_init(root):
    root = Path(root)
    top, sub = layout(root)
    if top is None:
        raise UsageError(f"{root} is not inside a git repo. Ask the human before running git init there.")
    if top == (root / ".work").resolve() or ".work" in Path(sub).parts:
        raise UsageError(f"{root} is inside a .work repo, not a project root")
    msgs = []
    for old, new in normalize_excludes(exclude_file(root), project_excludes(root)[0]):
        msgs.append(f"normalized exclude line: {old} -> {new}")
    miss = missing_excludes(root)
    if miss:
        f = exclude_file(root)
        f.parent.mkdir(parents=True, exist_ok=True)
        text = f.read_text() if f.is_file() else ""
        header = project_excludes(root)[1]
        add = ("\n" if text and not text.endswith("\n") else "")
        add += (header + "\n" if header not in text.splitlines() else "") + "\n".join(miss) + "\n"
        f.write_text(text + add)
        msgs.append(f"added to {f}: {' '.join(miss)}")
    work = root / ".work"
    work.mkdir(exist_ok=True)
    if not is_repo_root(work):
        git(work, "init", "-q", check=True)
        msgs.append(f"initialized git repo in {work}")
    gi = work / ".gitignore"
    if not gi.exists():
        gi.write_text(WORK_GITIGNORE)
        msgs.append("wrote .work/.gitignore")
    wf, res = tracked(root)
    for f in wf:
        msgs.append(f"TRACKED WORKFLOW FILE in the project repo: {f}")
    for f in res:
        msgs.append(f"tracked resources file in the project repo: {f}")
    print("\n".join(msgs) if msgs else "already set up")
    return 0


def do_unexclude(root):
    root = Path(root)
    if layout(root)[0] is None:
        raise UsageError(f"{root} is not inside a git repo")
    f = exclude_file(root)
    lines, header = project_excludes(root)
    text = f.read_text() if f.is_file() else ""
    mine = {normalize_exclude(l) for l in lines}
    kept = [l for l in text.splitlines() if l != header and normalize_exclude(l) not in mine]
    removed = [l for l in text.splitlines() if normalize_exclude(l) in mine]
    if not removed and header not in text.splitlines():
        print("nothing to remove")
        return 0
    f.write_text("\n".join(kept) + ("\n" if kept else ""))
    print(f"removed from {f}: {' '.join(removed)}")
    return 0


def do_commit(root, message, paths):
    root = Path(root).resolve()
    require(root)
    if not message.strip():
        raise UsageError("empty commit message")
    wf, _ = tracked(root)
    miss = missing_excludes(root)
    if wf or miss:
        raise UsageError("refusing to commit: " + "; ".join(
            ([f"workflow files tracked by the project repo: {', '.join(wf)} (untrack them first)"] if wf else []) +
            ([f"exclude lines missing: {' '.join(miss)} (run repos.py init)"] if miss else [])))
    rels = []
    for p in paths or ["."]:
        a = (Path(p) if Path(p).is_absolute() else root / p).resolve()
        try:
            rel = a.relative_to(root).as_posix()
        except ValueError:
            raise UsageError(f"outside the project directory: {p}")
        if rel == ".work" or rel.startswith(".work/"):
            raise UsageError(f"workflow path, commit it in the .work repo: {p}")
        rels.append(rel)
    pathspec = ["--"] + [f":(literal){r}" for r in rels]
    git(root, "add", *pathspec, check=True)  # never -A, -f or -u: excluded paths stay out
    if git(root, "diff", "--cached", "--quiet", *pathspec).returncode == 0:
        print("nothing to commit")
        return 0
    git(root, "commit", "-q", "-m", message, *pathspec, check=True)  # only these paths, not the rest of the index
    print(f"committed {(out(root, 'rev-parse', '--short=7', 'HEAD') or '').strip()}: {message.splitlines()[0]}")
    return 0


def do_check(root):
    root = Path(root)
    bad = False
    lines = []
    top, sub = layout(root)
    if top is None or top == (root / ".work").resolve():
        print("project repo: missing")
        return 1
    if sub:
        lines.append(f"project: {sub} in the repo at {top} (checks cover {sub} only)")
    work_ok = is_repo_root(root / ".work")
    projs = raw_status(top, sub)
    lines.append(f"project repo: {'clean' if not projs else f'dirty ({len(projs)} paths)'}")
    if work_ok:
        ws = raw_status(root / ".work", "")
        lines.append(f".work repo: {'clean' if not ws else f'dirty ({len(ws)} paths)'}")
    else:
        lines.append(".work repo: MISSING (run repos.py init)")
        bad = True
    wf, res = tracked(root)
    lines.append("workflow files tracked by the project repo: " + (", ".join(wf) if wf else "none"))
    lines.append("resources/ files tracked by the project repo: " + (", ".join(res) if res else "none"))
    miss = missing_excludes(root)
    lines.append("project repo excludes: " + ("ok" if not miss else "MISSING " + " ".join(miss)))
    for f in parent_claude_md(root):
        lines.append(f"also loaded: {f} (CLAUDE.md above the project)")
    bad = bad or bool(wf) or bool(miss)
    print("\n".join(lines))
    return 1 if bad else 0


def do_guard_begin(root):
    require(root)
    dirty = status_lines(root)
    if dirty:
        for code, path in dirty:
            print(f"{code} {path}", file=sys.stderr)
        print("repos: not clean. Commit in the project repo and in the .work repo before dispatch.", file=sys.stderr)
        return 2
    print(rev(root, full=True))
    return 0


def violations(root, base, allow):
    pb, wb = split_base(base)
    v = []
    for (name, cwd, sub, _), b in zip(repos(root), (pb, wb)):
        h = repo_head(cwd, sub)
        if h != b and not (b and h and h.startswith(b)):
            v.append(("HEAD", f"{name} repo HEAD moved from {b or 'none'} to {h or 'none'}"))
    for code, path in status_lines(root):
        ok = (code == "??" and path.startswith(".work/issues/")
              and any(path.startswith(a) for a in allow) and "/" not in path[len(".work/issues/"):])
        if not ok:
            v.append((code, path))
    return v


def revert(root, base):
    pb, wb = split_base(base)
    for (_, cwd, sub, _), b in zip(repos(root), (pb, wb)):
        for code, path, orig in raw_status(cwd, sub):
            for p in [x for x in (orig, path) if x]:
                if sub and not p.startswith(sub):
                    continue  # the other side of a rename across the project boundary: not ours
                if code == "??":
                    git(cwd, "--literal-pathspecs", "clean", "-f", "-q", "--", p)
                elif b and git(cwd, "cat-file", "-e", f"{b}:{p}").returncode == 0:
                    git(cwd, "--literal-pathspecs", "restore", "--staged", "--worktree", f"--source={b}", "--", p)
                else:  # added to the index, absent at the base
                    git(cwd, "--literal-pathspecs", "rm", "--cached", "-f", "-q", "--", p)
                    if (Path(cwd) / p).is_file():
                        (Path(cwd) / p).unlink()
    return status_lines(root)


def do_guard_check(root, base, allow, do_revert):
    require(root)
    v = violations(root, base, allow)
    if not v:
        print("write guard: ok")
        return 0
    print("WRITE GUARD VIOLATION. Review discarded.")
    for code, path in v:
        print(f"  {code} {path}")
    if do_revert:
        left = revert(root, base)
        if left:
            print("REVERT INCOMPLETE. Remaining:")
            for code, path in left:
                print(f"  {code} {path}")
        else:
            print("Reverted both repos to the base (HEAD not reset). Log the violation in decisions.md.")
    return 3


def do_diff(root, base, mode):
    require(root)
    pb, wb = split_base(base)
    for (_, cwd, sub, prefix), b in zip(repos(root), (pb, wb)):
        if not head(cwd):
            continue
        args = ["diff", b or git_empty_tree(cwd), "HEAD"] + ([f"--relative={sub}"] if sub else [])
        if mode == "--name-only":
            for line in (out(cwd, *args, "--name-only") or "").splitlines():
                print(prefix + line)
            continue
        if mode == "--stat":
            text = out(cwd, *args, "--stat") or ""
            text = "\n".join(f" {prefix}{l[1:]}" if prefix and "|" in l else l for l in text.splitlines())
        else:
            text = out(cwd, *args, f"--src-prefix=a/{prefix}", f"--dst-prefix=b/{prefix}") or ""
        if text.strip():
            print(text.rstrip("\n"))
    return 0


def git_empty_tree(cwd):
    return (out(cwd, "hash-object", "-t", "tree", "/dev/null") or "").strip()


def do_log(root, base):
    require(root)
    pb, wb = split_base(base)
    for (name, cwd, sub, _), b in zip(repos(root), (pb, wb)):
        if not head(cwd):
            continue
        rng = f"{b}..HEAD" if b else "HEAD"
        for line in (out(cwd, "log", "--oneline", rng, *spec(sub)) or "").splitlines():
            print(f"{name} {line}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("unexclude")
    p = sub.add_parser("commit"); p.add_argument("-m", "--message", required=True); p.add_argument("paths", nargs="*")
    sub.add_parser("status")
    p = sub.add_parser("rev"); p.add_argument("--full", action="store_true")
    sub.add_parser("check")
    sub.add_parser("guard-begin")
    p = sub.add_parser("guard-check"); p.add_argument("--base", required=True)
    p.add_argument("--allow", action="append", default=[]); p.add_argument("--revert", action="store_true")
    p = sub.add_parser("diff"); p.add_argument("base")
    g = p.add_mutually_exclusive_group(); g.add_argument("--name-only", action="store_true"); g.add_argument("--stat", action="store_true")
    p = sub.add_parser("log"); p.add_argument("base")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    try:
        if a.cmd == "init":
            return do_init(root)
        if a.cmd == "unexclude":
            return do_unexclude(root)
        if a.cmd == "commit":
            return do_commit(root, a.message, a.paths)
        if a.cmd == "status":
            require(root)
            for code, path in status_lines(root):
                print(f"{code} {path}")
            return 0
        if a.cmd == "rev":
            require(root)
            print(rev(root, a.full))
            return 0
        if a.cmd == "check":
            return do_check(root)
        if a.cmd == "guard-begin":
            return do_guard_begin(root)
        if a.cmd == "guard-check":
            return do_guard_check(root, a.base, a.allow, a.revert)
        if a.cmd == "diff":
            return do_diff(root, a.base, "--name-only" if a.name_only else "--stat" if a.stat else None)
        if a.cmd == "log":
            return do_log(root, a.base)
    except UsageError as e:
        print(f"repos: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
