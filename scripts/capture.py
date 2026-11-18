#!/usr/bin/env python3
"""Capture from a research conversation into a workflow project (.work/). Stdlib only.

Only items the human ticked in the capture dialog are written. Writers:
  capture.py idea --text T [--kind idea|question] [--session SID]
        append I<n> to .work/ideas.md (status open). Prints the ID.
  capture.py set I<n> status=<open|pursued|answered|rejected> [note=TEXT]
  capture.py deadend --what W --why Y [--ref R]
        append one line to .work/deadends.md
  capture.py decision --title T --reason R
        a decision the human took in discussion: decisions.md entry, made by human, class logged
  capture.py summary --session SID --file F
        write .work/sessions/<YYYYMMDD-HHMM>-<sid8>.md from F (the one-page session summary) and mark the session captured;
        also marks every pending stub this capture covered (--covers STUB ...)
  capture.py stub --session SID --transcript P
        (SessionEnd hook) write .work/sessions/<ts>-<sid8>-stub.md unless the session was captured
  capture.py pending [--json]
        stubs not yet captured: session, transcript, date
  capture.py captured --session SID
        exit 0 if the session has a summary, 1 otherwise
Agenda changes from a capture go through agenda.py (new threads as `exploring`).
Exit 0 on success, 2 on usage errors.
"""
import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decisions  # noqa: E402

IDEAS = Path(".work") / "ideas.md"
DEADENDS = Path(".work") / "deadends.md"
SESSIONS = Path(".work") / "sessions"
IDEA_STATUSES = ("open", "pursued", "answered", "rejected")
IDEAS_PREAMBLE = """# Ideas

Ideas, hypotheses and open questions from discussions, kept when the human ticks them in a capture dialog.
Written only by `~/dotclaude/scripts/capture.py`. Status: open, pursued (became a thread), answered, rejected.
"""


class UsageError(Exception):
    pass


def one_line(s):
    return " ".join(str(s).split()).replace("|", "/")


def sid8(sid):
    return "".join(c for c in str(sid) if c.isalnum())[:8] or "nosessio"


def ideas(root):
    p = Path(root) / IDEAS
    return p.read_text() if p.is_file() else IDEAS_PREAMBLE


def do_idea(root, text, kind, session):
    t = ideas(root)
    n = max([int(x) for x in re.findall(r"(?m)^## I(\d+) \|", t)] or [0]) + 1
    src = f"{date.today().isoformat()} (session {sid8(session)})" if session else f"{date.today().isoformat()} (conversation)"
    t = t.rstrip("\n") + f"\n\n## I{n} | {kind} | open\n- text: {one_line(text)}\n- source: {src}\n"
    (Path(root) / IDEAS).parent.mkdir(parents=True, exist_ok=True)
    (Path(root) / IDEAS).write_text(t)
    print(f"I{n}")
    return 0


def do_set(root, iid, pairs):
    parts = re.split(r"(?m)^(?=## I\d+ \|)", ideas(root))
    k = next((n for n, b in enumerate(parts) if b.startswith(f"## {iid} |")), None)
    if k is None:
        raise UsageError(f"no idea {iid}")
    head, _, rest = parts[k].partition("\n")
    kind = head.split("|")[1].strip()
    rest = rest.rstrip("\n")
    for kv in pairs:
        key, _, v = kv.partition("=")
        if key == "status":
            if v not in IDEA_STATUSES:
                raise UsageError(f"status must be one of {', '.join(IDEA_STATUSES)}")
            head = f"## {iid} | {kind} | {v}"
        elif key == "note":
            rest += f"\n- note: {date.today().isoformat()} {one_line(v)}"
        else:
            raise UsageError(f"cannot set {key}")
    parts[k] = head + "\n" + rest + "\n\n"
    (Path(root) / IDEAS).write_text("".join(parts).rstrip("\n") + "\n")
    print(f"{iid} updated")
    return 0


def do_deadend(root, what, why, ref):
    p = Path(root) / DEADENDS
    t = p.read_text() if p.is_file() else "# Dead ends\n"
    t = t.rstrip("\n") + f"\n- {date.today().isoformat()} | {one_line(what)} | {one_line(why)} | {one_line(ref or 'discussion')}\n"
    p.write_text(t)
    print("dead end recorded")
    return 0


def session_files(root):
    d = Path(root) / SESSIONS
    return sorted(d.glob("*.md")) if d.is_dir() else []


def field(text, key):
    m = re.search(rf"^- {key}:\s*(.*)$", text, re.M)
    return m.group(1).strip() if m else None


def is_captured(root, session):
    return any(f.name.endswith(f"-{sid8(session)}.md") for f in session_files(root))


def do_summary(root, session, file, covers):
    body = Path(file).read_text().strip()
    if not body:
        raise UsageError("empty summary")
    d = Path(root) / SESSIONS
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{datetime.now().strftime('%Y%m%d-%H%M')}-{sid8(session)}.md"
    out.write_text(f"# Session {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n- session: {session}\n\n{body}\n")
    for stub in covers or []:
        p = Path(stub) if Path(stub).is_absolute() else Path(root) / stub
        if p.is_file() and field(p.read_text(), "captured") in (None, "no"):
            p.write_text(re.sub(r"(?m)^- captured: .*$", f"- captured: {out.name}", p.read_text()))
    print(out.relative_to(root) if out.is_relative_to(Path(root)) else out)
    return 0


def do_stub(root, session, transcript):
    if is_captured(root, session):
        print("captured already; no stub")
        return 0
    d = Path(root) / SESSIONS
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{datetime.now().strftime('%Y%m%d-%H%M')}-{sid8(session)}-stub.md"
    out.write_text(f"# Capture pending\n\nThe session ended without a capture. The next session offers the capture dialog "
                   f"from this transcript.\n\n- session: {session}\n- transcript: {transcript}\n- captured: no\n")
    print(out.name)
    return 0


def pending(root):
    out = []
    for f in session_files(root):
        if not f.name.endswith("-stub.md"):
            continue
        t = f.read_text()
        if field(t, "captured") == "no":
            out.append({"stub": str(f.relative_to(root)), "session": field(t, "session"),
                        "transcript": field(t, "transcript"), "date": f.name[:8]})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("idea"); p.add_argument("--text", required=True)
    p.add_argument("--kind", default="idea", choices=("idea", "question")); p.add_argument("--session")
    p = sub.add_parser("set"); p.add_argument("id"); p.add_argument("pairs", nargs="+")
    p = sub.add_parser("deadend"); p.add_argument("--what", required=True); p.add_argument("--why", required=True)
    p.add_argument("--ref")
    p = sub.add_parser("decision"); p.add_argument("--title", required=True); p.add_argument("--reason", required=True)
    p = sub.add_parser("summary"); p.add_argument("--session", required=True); p.add_argument("--file", required=True)
    p.add_argument("--covers", nargs="*")
    p = sub.add_parser("stub"); p.add_argument("--session", required=True); p.add_argument("--transcript", default="unknown")
    p = sub.add_parser("pending"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("captured"); p.add_argument("--session", required=True)
    a = ap.parse_args(argv)
    root = Path(a.root)
    try:
        if a.cmd == "idea":
            return do_idea(root, a.text, a.kind, a.session)
        if a.cmd == "set":
            return do_set(root, a.id, a.pairs)
        if a.cmd == "deadend":
            return do_deadend(root, a.what, a.why, a.ref)
        if a.cmd == "decision":
            decisions.log_entry(root, one_line(a.title), "human", "logged", "none", one_line(a.reason) + " (discussion)")
            print("decision recorded")
            return 0
        if a.cmd == "summary":
            return do_summary(root, a.session, a.file, a.covers)
        if a.cmd == "stub":
            return do_stub(root, a.session, a.transcript)
        if a.cmd == "pending":
            p = pending(root)
            if a.json:
                print(json.dumps(p, indent=2))
            else:
                for x in p:
                    print(f"{x['stub']}: session {x['session']}, transcript {x['transcript']}")
                if not p:
                    print("none")
            return 0
        if a.cmd == "captured":
            return 0 if is_captured(root, a.session) else 1
    except UsageError as e:
        print(f"capture: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
