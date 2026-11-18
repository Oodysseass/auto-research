#!/usr/bin/env python3
"""The agenda of a research workflow project: .work/threads.md. Stdlib only. The only writer of that file.

A thread is a line of work. Order in the file is priority: the first `committed` thread is what `rw` works on next.
Block format:
  ## T<n> | <title> | <status>
  - goal: <one line>
  - stage: <playbook stage ID it runs, e.g. S4 | none>
  - covers: <R-, DL-, C-IDs it serves | none>
  - next: <next concrete step | none>
  - added: <YYYY-MM-DD> (<intake | RQ<n> | conversation | migration>)
  - note: <optional; drop reasons and status history are appended here>
Statuses: exploring (discussed, not committed), committed (rw may work on it), parked, done, dropped (kept, never deleted).

Usage (run from the project root, or pass --root):
  agenda.py list [--all] [--json]       threads in order; without --all, done and dropped are left out
  agenda.py next [--json]               the first committed thread, or "none" (exit 2 if threads.md is missing)
  agenda.py add --title T --goal G [--stage S<n>] [--covers IDS] [--status exploring|committed] [--source S]
                [--top | --before T<n> | --after T<n>]        (default: after the last open thread)
  agenda.py move T<n> (--top | --bottom | --before T<m> | --after T<m>)
  agenda.py set T<n> [status=S] [next=TEXT] [goal=TEXT] [covers=IDS] [title=TEXT]
  agenda.py drop T<n> --reason R        status dropped, reason kept in the note; the block stays
  agenda.py seed --playbook NAME [--current S<n>]
                                        create threads.md from a playbook's stages (intake, migration): one committed
                                        thread per stage, in playbook order; stages before --current are done.
                                        Refuses if threads.md has threads.
  agenda.py lint                        format check: IDs unique, statuses valid, fields present
Every change except seed appends a `class: logged` entry to decisions.md (`--by`, default human).
Changes that alter a requirement or deliverable are not decided here: the request skill raises a blocking card first.
Exit 0 on success, 1 on lint errors, 2 on usage errors.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decisions  # noqa: E402

THREADS = Path(".work") / "threads.md"
PLAYBOOKS = Path(__file__).resolve().parent.parent / "skills" / "intake" / "playbooks"
STATUSES = ("exploring", "committed", "parked", "done", "dropped")
OPEN = ("exploring", "committed", "parked")
FIELDS = ("goal", "stage", "covers", "next", "added", "note")
HEAD = re.compile(r"^## (T\d+) \| (.+?) \| (\S+)\s*$")
PREAMBLE = """# Threads

The project's agenda, in priority order: the first `committed` thread is what `rw` works on next.
Written only by `~/dotclaude/scripts/agenda.py`. Statuses: exploring, committed, parked, done, dropped.
"""


class UsageError(Exception):
    pass


def path(root):
    return Path(root) / THREADS


def load(root):
    """(preamble, [thread dict]) with each thread: id, title, status and the FIELDS."""
    p = path(root)
    if not p.is_file():
        return PREAMBLE, []
    text = p.read_text()
    parts = re.split(r"(?m)^(?=## T\d+ \|)", text)
    pre, threads = parts[0], []
    for block in parts[1:]:
        lines = block.strip("\n").splitlines()
        m = HEAD.match(lines[0])
        if not m:
            raise UsageError(f"bad thread heading: {lines[0]}")
        t = {"id": m.group(1), "title": m.group(2).strip(), "status": m.group(3)}
        for line in lines[1:]:
            fm = re.match(r"^- ([a-z]+):\s*(.*?)\s*$", line)
            if fm and fm.group(1) in FIELDS:
                t[fm.group(1)] = fm.group(2)
        threads.append(t)
    return pre, threads


def render(pre, threads):
    out = [pre.rstrip("\n"), ""]
    for t in threads:
        out.append(f"## {t['id']} | {t['title']} | {t['status']}")
        for f in FIELDS:
            if t.get(f) or f != "note":
                out.append(f"- {f}: {t.get(f) or 'none'}")
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def save(root, pre, threads):
    p = path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render(pre, threads))


def clean(s):
    """One line, no `|` (it separates the heading fields)."""
    return " ".join(str(s).split()).replace("|", "/")


def find(threads, tid):
    for i, t in enumerate(threads):
        if t["id"] == tid:
            return i
    raise UsageError(f"no thread {tid}")


def next_id(threads):
    return f"T{max([int(t['id'][1:]) for t in threads] or [0]) + 1}"


def log(root, by, title, reason):
    decisions.log_entry(root, title, by, "logged", "none", reason)


def note(t, text):
    stamp = f"{date.today().isoformat()} {text}"
    t["note"] = f"{t['note']}; {stamp}" if t.get("note") and t["note"] != "none" else stamp


def position(threads, a):
    """Index to insert at, from --top/--bottom/--before/--after (None: default)."""
    if getattr(a, "top", False):
        return 0
    if getattr(a, "bottom", False):
        return len(threads)
    if getattr(a, "before", None):
        return find(threads, a.before)
    if getattr(a, "after", None):
        return find(threads, a.after) + 1
    return None


def do_list(root, all_, as_json):
    _, threads = load(root)
    shown = [t for t in threads if all_ or t["status"] in OPEN]
    if as_json:
        print(json.dumps(shown, indent=2))
        return 0
    if not shown:
        print("no threads")
    for n, t in enumerate(shown, 1):
        extra = f" [{t['stage']}]" if t.get("stage") not in (None, "none") else ""
        print(f"{n}. {t['id']} {t['title']}{extra}: {t['status']}" +
              (f". next: {t['next']}" if t.get("next") not in (None, "none") else ""))
    return 0


def do_next(root, as_json):
    if not path(root).is_file():
        raise UsageError("no .work/threads.md: this project predates the agenda; run "
                         "python3 ~/dotclaude/scripts/project_update.py first")
    _, threads = load(root)
    t = next((t for t in threads if t["status"] == "committed"), None)
    if as_json:
        print(json.dumps(t))
    else:
        print(f"{t['id']} | {t['title']} | stage {t.get('stage', 'none')}" if t else "none")
    return 0


def do_add(root, a):
    pre, threads = load(root)
    if a.status not in ("exploring", "committed"):
        raise UsageError("a new thread is exploring or committed")
    t = {"id": next_id(threads), "title": clean(a.title), "status": a.status, "goal": clean(a.goal),
         "stage": a.stage or "none", "covers": a.covers or "none", "next": "none",
         "added": f"{date.today().isoformat()} ({a.source})"}
    at = position(threads, a)
    if at is None:
        at = max((i + 1 for i, x in enumerate(threads) if x["status"] in OPEN), default=0)
    threads.insert(at, t)
    save(root, pre, threads)
    log(root, a.by, f"agenda: add {t['id']} {t['title']} ({t['status']}, position {at + 1})", a.reason or "added to the agenda")
    print(t["id"])
    return 0


def do_move(root, a):
    pre, threads = load(root)
    i = find(threads, a.id)
    if a.id in (a.before, a.after):
        raise UsageError("cannot move a thread relative to itself")
    t = threads.pop(i)
    at = position(threads, a)
    if at is None:
        raise UsageError("move needs --top, --bottom, --before or --after")
    threads.insert(at, t)
    save(root, pre, threads)
    log(root, a.by, f"agenda: move {t['id']} {t['title']} to position {at + 1}", a.reason or "priority changed")
    print(f"{t['id']} at position {at + 1}")
    return 0


def do_set(root, a):
    pre, threads = load(root)
    t = threads[find(threads, a.id)]
    changes = []
    for kv in a.pairs:
        if "=" not in kv:
            raise UsageError(f"expected key=value: {kv}")
        k, v = kv.split("=", 1)
        v = clean(v)
        if k == "status":
            if v not in STATUSES:
                raise UsageError(f"status must be one of {', '.join(STATUSES)}")
            if v == "dropped":
                raise UsageError("use `drop` with a reason")
            note(t, f"{t['status']} -> {v}")
            t["status"] = v
        elif k in ("next", "goal", "covers", "title", "stage"):
            t[k] = v or "none"
        else:
            raise UsageError(f"cannot set {k}")
        changes.append(f"{k}={v}")
    if not changes:
        raise UsageError("nothing to set")
    save(root, pre, threads)
    log(root, a.by, f"agenda: {t['id']} {t['title']}: {', '.join(changes)}", a.reason or "agenda updated")
    print(f"{t['id']}: {', '.join(changes)}")
    return 0


def do_drop(root, a):
    pre, threads = load(root)
    t = threads[find(threads, a.id)]
    if t["status"] == "dropped":
        raise UsageError(f"{t['id']} is already dropped")
    note(t, f"dropped: {clean(a.reason)}")
    t["status"] = "dropped"
    save(root, pre, threads)
    log(root, a.by, f"agenda: drop {t['id']} {t['title']}", clean(a.reason))
    print(f"{t['id']} dropped")
    return 0


def playbook_stages(name):
    p = PLAYBOOKS / f"{name}.md"
    if not p.is_file():
        raise UsageError(f"no playbook {name}")
    out = []
    for block in re.split(r"(?m)^(?=## S\d+ )", p.read_text())[1:]:
        m = re.match(r"## (S\d+) (.+)", block)
        g = re.search(r"^- goal:\s*(.+)$", block, re.M)
        out.append((m.group(1), m.group(2).strip(), g.group(1).strip() if g else "none"))
    return out


def do_seed(root, playbook, current, source="intake"):
    pre, threads = load(root)
    if threads:
        raise UsageError("threads.md already has threads")
    stages = playbook_stages(playbook)
    ids = [s for s, _, _ in stages]
    if current and current not in ids:
        raise UsageError(f"{current} is not a stage of {playbook}")
    cut = ids.index(current) if current else 0
    today = date.today().isoformat()
    for n, (sid, title, goal) in enumerate(stages):
        threads.append({"id": f"T{n + 1}", "title": title, "status": "done" if n < cut else "committed", "goal": goal,
                        "stage": sid, "covers": "none", "next": "none", "added": f"{today} ({source})"})
    save(root, pre, threads)
    print(f"{len(threads)} threads from playbook {playbook}" + (f", before {current} done" if current else ""))
    return 0


def lint(root):
    errs = []
    p = path(root)
    if not p.is_file():
        return ["no .work/threads.md"]
    try:
        _, threads = load(root)
    except UsageError as e:
        return [str(e)]
    seen = set()
    for t in threads:
        if t["id"] in seen:
            errs.append(f"{t['id']}: duplicate ID")
        seen.add(t["id"])
        if t["status"] not in STATUSES:
            errs.append(f"{t['id']}: bad status {t['status']!r}")
        for f in ("goal", "stage", "covers", "next", "added"):
            if not t.get(f):
                errs.append(f"{t['id']}: missing {f}")
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--by", default="human")
    ap.add_argument("--reason")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--all", action="store_true"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("next"); p.add_argument("--json", action="store_true")

    def where(p):
        g = p.add_mutually_exclusive_group()
        g.add_argument("--top", action="store_true"); g.add_argument("--bottom", action="store_true")
        g.add_argument("--before"); g.add_argument("--after")

    p = sub.add_parser("add")
    p.add_argument("--title", required=True); p.add_argument("--goal", required=True); p.add_argument("--stage")
    p.add_argument("--covers"); p.add_argument("--status", default="committed"); p.add_argument("--source", default="conversation")
    where(p)
    p = sub.add_parser("move"); p.add_argument("id"); where(p)
    p = sub.add_parser("set"); p.add_argument("id"); p.add_argument("pairs", nargs="+")
    p = sub.add_parser("drop"); p.add_argument("id"); p.add_argument("--reason", required=True, dest="drop_reason")
    p = sub.add_parser("seed"); p.add_argument("--playbook", required=True); p.add_argument("--current")
    sub.add_parser("lint")
    a = ap.parse_args(argv)
    root = a.root
    try:
        if a.cmd == "list":
            return do_list(root, a.all, a.json)
        if a.cmd == "next":
            return do_next(root, a.json)
        if a.cmd == "add":
            return do_add(root, a)
        if a.cmd == "move":
            return do_move(root, a)
        if a.cmd == "set":
            return do_set(root, a)
        if a.cmd == "drop":
            a.reason = a.drop_reason
            return do_drop(root, a)
        if a.cmd == "seed":
            return do_seed(root, a.playbook, a.current)
        if a.cmd == "lint":
            errs = lint(root)
            for e in errs:
                print(f"FAIL {e}")
            print("OK" if not errs else f"{len(errs)} error(s)")
            return 1 if errs else 0
    except UsageError as e:
        print(f"agenda: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
