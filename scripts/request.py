#!/usr/bin/env python3
"""Requests typed in direct mode in a research workflow project (.work/). Stdlib only.

In a plain `claude` session in a project with `.work/`, every prompt is a request handled by the `request` skill, unless it
starts with `raw:` or `/`. The UserPromptSubmit hook saves the prompt (rw_hooks.py); this script records it, picks the gates,
writes scope cards, closes it and traces changes back to it. Registry: .work/requests.md, one block per request (RQ<n>).
The text of each request goes to resources/BRIEF.md under a dated "Requests" heading. Attachments go to
resources/<date>-<slug>/ and into .work/resources.manifest (origin `request`, handled RQ<n>).

Usage (run from the project root, or pass --root):
  request.py record --slug S --title T [--session ID] [--transcript PATH] [--text-file F] [--follow-up RQ<n>]
        record the prompt: the text saved by the hook for the session (or --text-file), with its images and documents from
        the transcript. Pasted blocks over PASTE_LINES lines and files outside the project named by @path or by an
        absolute path go to resources/<date>-<slug>/ too. Prints JSON: id, mode, dir, files, warnings.
        --follow-up: the prompt continues request RQ<n> (an answer, a correction); it is appended to it, no new ID.
  request.py gates --kind prose|technical [--tex] [--critical] [--mode default|quick|full]
        the brief's `- gates:` and `- critical:` values for a request. prose: G0, G1, G4. technical: G0 to G2 and G4,
        G3 if critical. quick: G0, G1. full: G0 to G4, critical. G0 only with --tex (a .tex file changes).
  request.py context
        the playbook stage in progress (active brief, briefs not done, their artifact files and claims) and open or
        deferred requests. The request skill checks a request against it for conflicts.
  request.py raise RQ<n> --affects IDS --question Q --reason R (--scope-change | --deliverable-change) [--recommend A|B|C]
        blocking decision card D<n> for a request that changes the scope or a deliverable: A apply it (the contract
        changes), B do it only within the approved contract, C drop it. IDS: the R-, N-, P-, C- or A-IDs it affects.
        Any other impact (model, statements, claims) gets an ordinary card with the class from approvals.md.
  request.py set RQ<n> KEY=VALUE ...     set registry fields (LIST_KEYS values are comma-separated and merged).
  request.py close RQ<n> --status done|answered|deferred|dropped --summary S
        record the outcome: rev after, the commits and changed files in both repos since `rev before`.
  request.py list [-n N] [--status S]   recent requests, newest first, one line each.
  request.py show RQ<n>                 the registry block and the request text in resources/BRIEF.md.
  request.py trace TOKEN                the requests behind a claim, decision, brief, file path or commit hash.

Exit 0 on success, 1 on a failed card lint, 2 on usage errors.
"""
import argparse
import base64
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decisions  # noqa: E402
import repos  # noqa: E402
import resources  # noqa: E402

REGISTRY = Path(".work") / "requests.md"
BRIEF = Path("resources") / "BRIEF.md"
STATE_DIR = Path(os.environ.get("RW_HOOKS_STATE_DIR", Path(tempfile.gettempdir()) / "rw-hooks"))
PASTE_LINES = 20
MAX_COPY = 50 * 1024 * 1024
KEYS = ("date", "title", "mode", "status", "text", "files", "rev before", "rev after", "briefs", "decisions", "claims",
        "gates", "changed", "commits", "summary")
LIST_KEYS = ("files", "briefs", "decisions", "claims", "gates", "changed", "commits")
STATUSES = ("open", "done", "answered", "deferred", "dropped")
HEADER = ("# Requests\n\nPrompts typed in direct mode. One block per request. Written by "
          "`~/dotclaude/scripts/request.py` only.\nThe text of each request is in `resources/BRIEF.md`, under "
          "\"Requests <date>\", heading `RQ<n>`.\n")
EXT = {"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif", "image/webp": "webp", "application/pdf": "pdf"}
PASTE = re.compile(r"<pasted_content[^>]*>\n?(.*?)\n?</pasted_content[^>]*>", re.S)


class UsageError(Exception):
    pass


# ---------- the prompt ----------

def session_key(sid):
    return "".join(c for c in str(sid or "nosession") if c.isalnum() or c in "-_")


def saved_prompt_path(sid):
    return STATE_DIR / f"{session_key(sid)}.prompt.json"


def is_direct(prompt):
    """True if a typed prompt is a request: not raw:, not a slash command, not empty."""
    s = (prompt or "").lstrip()
    return bool(s) and not s.startswith("/") and not s.lower().startswith("raw:")


def human_entries(transcript_path):
    """User messages typed by the human, oldest first: (text, content blocks). Tool results and meta messages skipped."""
    try:
        lines = Path(transcript_path).read_text().splitlines()
    except (OSError, TypeError):
        return []
    out = []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") != "user" or e.get("isMeta"):
            continue
        c = (e.get("message") or {}).get("content")
        if isinstance(c, str):
            out.append((c, []))
        elif isinstance(c, list):
            if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
                continue
            blocks = [x for x in c if isinstance(x, dict)]
            out.append(("\n".join(x.get("text", "") for x in blocks if x.get("type") == "text"), blocks))
    return out


def last_human_prompt(transcript_path):
    e = human_entries(transcript_path)
    return e[-1][0] if e else None


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def load_prompt(sid, transcript, text_file):
    """(text, blocks): the prompt text, and the content blocks (images, documents) of its transcript entry."""
    text = None
    if text_file:
        text = Path(text_file).read_text()
    else:
        try:
            d = json.loads(saved_prompt_path(sid).read_text())
            text = d.get("prompt")
            transcript = transcript or d.get("transcript")
        except (OSError, ValueError):
            pass
    entries = human_entries(transcript) if transcript else []
    blocks = []
    if entries:
        match = [e for e in entries if text is not None and norm(e[0]) and
                 (norm(e[0]) == norm(text) or norm(text).startswith(norm(e[0])) or norm(e[0]).startswith(norm(text)))]
        entry = match[-1] if match else (entries[-1] if text is None else None)
        if entry:
            blocks = entry[1]
            text = text if text is not None else entry[0]
    if text is None:
        raise UsageError("no prompt saved for this session and no --text-file")
    return text, blocks


def mode_of(text):
    """Gate depth from a `quick:` or `full:` prefix (case-insensitive). Words elsewhere in the prompt do not count."""
    m = re.match(r"\s*(quick|full)\s*:", text, re.I)
    return m.group(1).lower() if m else "default"


def attached_paths(text, root):
    """Existing files outside the project named in the prompt by @path or by an absolute or ~ path."""
    out = []
    for m in re.finditer(r"(?<![^\s(\[])(@[^\s'\"`<>]+|~/[^\s'\"`<>]+|/[^\s'\"`<>]+)", text):
        raw = m.group(1).lstrip("@").rstrip(".,;:)]")
        p = Path(os.path.expanduser(raw))
        if not p.is_absolute():
            p = Path(root) / p
        try:
            p = p.resolve()
        except OSError:
            continue
        if not p.is_file() or p.stat().st_size > MAX_COPY:
            continue
        home = Path.home()
        if Path(root).resolve() in p.parents or any(d in p.parents for d in (home / ".claude", home / "dotclaude")):
            continue
        if p not in out:
            out.append(p)
    return out


# ---------- registry ----------

def registry(root):
    return Path(root) / REGISTRY


def parse_registry(root):
    p = registry(root)
    if not p.is_file():
        return []
    out = []
    for chunk in re.split(r"(?m)^(?=## RQ\d+\s*$)", p.read_text()):
        m = re.match(r"(?m)## (RQ\d+)\s*$", chunk)
        if not m:
            continue
        r = {"id": m.group(1)}
        for line in chunk.splitlines()[1:]:
            km = re.match(r"^- ([a-z ]+):\s*(.*?)\s*$", line)
            if km and km.group(1) in KEYS:
                r[km.group(1)] = km.group(2)
        out.append(r)
    return out


def get(root, rid):
    for r in parse_registry(root):
        if r["id"] == rid:
            return r
    raise UsageError(f"no request {rid} in {REGISTRY}")


def next_id(root):
    return f"RQ{max([int(r['id'][2:]) for r in parse_registry(root)] or [0]) + 1}"


def split(v):
    return [x.strip() for x in (v or "").split(",") if x.strip() and x.strip() != "none"]


def join(xs):
    return ", ".join(xs) if xs else "none"


def write_block(root, r):
    p = registry(root)
    text = p.read_text() if p.is_file() else HEADER
    block = f"## {r['id']}\n" + "".join(f"- {k}: {r.get(k) or 'none'}\n" for k in KEYS)
    pat = re.compile(rf"(?ms)^## {r['id']}\s*$.*?(?=^## RQ\d+\s*$|\Z)")
    if pat.search(text):
        text = pat.sub(lambda _: block + "\n", text, count=1)
    else:
        text = text.rstrip("\n") + "\n\n" + block
    p.write_text(text.rstrip("\n") + "\n")


def set_fields(root, rid, pairs):
    r = get(root, rid)
    for k, v in pairs.items():
        if k not in KEYS or k in ("date", "rev before"):
            raise UsageError(f"cannot set {k!r}; settable: {', '.join(k for k in KEYS if k not in ('date', 'rev before'))}")
        if k == "status" and v not in STATUSES:
            raise UsageError(f"status must be one of {', '.join(STATUSES)}")
        if k == "mode" and v not in ("default", "quick", "full"):
            raise UsageError("mode must be default, quick or full")
        r[k] = join(split(r.get(k)) + [x for x in split(v) if x not in split(r.get(k))]) if k in LIST_KEYS else v
    write_block(root, r)
    return r


# ---------- record ----------

def unique_dir(root, day, slug):
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")[:40] or "request"
    base = Path(root) / "resources" / f"{day}-{slug}"
    d, n = base, 2
    while d.exists():
        d, n = Path(f"{base}-{n}"), n + 1
    return d


def unique_file(d, name):
    p, n = d / name, 2
    while p.exists():
        stem, suf = os.path.splitext(name)
        p, n = d / f"{stem}-{n}{suf}", n + 1
    return p


def append_brief(root, rid, title, text, files, follow_up):
    p = Path(root) / BRIEF
    p.parent.mkdir(parents=True, exist_ok=True)
    body = p.read_text() if p.is_file() else "# Project brief\n"
    now = datetime.now()
    heading = f"## Requests {now.date().isoformat()}"
    heads = re.findall(r"(?m)^## .*$", body)
    if not heads or heads[-1].strip() != heading:
        body = body.rstrip("\n") + f"\n\n{heading}\n"
    label = f"{rid} follow-up" if follow_up else rid
    entry = f"\n### {label} | {now.strftime('%H:%M')} | {title}\n\n{text.strip()}\n"
    if files:
        entry += "\nFiles: " + ", ".join(f"`{f}`" for f in files) + "\n"
    p.write_text(body.rstrip("\n") + "\n" + entry)


def update_manifest(root, rid, files):
    """Add the request's files and refresh BRIEF.md. Returns warnings for the human."""
    if not (Path(root) / resources.MANIFEST).is_file():
        return [f"no {resources.MANIFEST}: request files are not in a manifest. "
                "Run: python3 ~/dotclaude/scripts/project_update.py"]
    entries = resources.load(root)
    for f in files:
        entries[f] = resources.entry(root, f, "request", rid, f"attached to {rid}")
    b = BRIEF.as_posix()
    old = entries.get(b)
    entries[b] = resources.entry(root, b, "refreshed", old["handled"] if old else "-", f"{rid} appended")
    resources.save(root, entries)
    return []


def brief_edited(root):
    """True if BRIEF.md changed since the manifest last saw it (an edit by the human, to show once)."""
    try:
        e = resources.load(root).get(BRIEF.as_posix())
    except resources.UsageError:
        return False
    p = Path(root) / BRIEF
    return bool(e) and p.is_file() and resources.sha256(p) != e["sha256"] and not e["anomaly"].startswith("edited")


def do_record(root, slug, title, sid, transcript, text_file, follow_up):
    if not (Path(root) / ".work").is_dir():
        raise UsageError("no .work/ here: run from the project root")
    text, blocks = load_prompt(sid, transcript, text_file)
    rid = follow_up or next_id(root)
    old = get(root, rid) if follow_up else None
    warnings = []
    if brief_edited(root):
        warnings.append("resources/BRIEF.md was edited since the workflow last recorded it; the edit is kept as it is")
    day = datetime.now().date().isoformat()
    d = unique_dir(root, day, slug)
    saved = []

    def put(name, data):
        d.mkdir(parents=True, exist_ok=True)
        p = unique_file(d, name)
        p.write_bytes(data) if isinstance(data, bytes) else p.write_text(data)
        saved.append(p.relative_to(root).as_posix())
        return saved[-1]

    k = 0
    for b in blocks:
        src = b.get("source") or {}
        if b.get("type") in ("image", "document") and src.get("type") == "base64" and src.get("data"):
            k += 1
            ext = EXT.get(src.get("media_type"), "bin")
            put(f"{'image' if b['type'] == 'image' else 'document'}-{k}.{ext}", base64.b64decode(src["data"]))
    pastes = [0]

    def paste(m):
        body = m.group(1)
        if len(body.splitlines()) <= PASTE_LINES:
            return body
        pastes[0] += 1
        return f"[pasted text, saved to `{put(f'paste-{pastes[0]}.md', body.rstrip() + chr(10))}`]"

    text = PASTE.sub(paste, text)
    for p in attached_paths(text, root):
        d.mkdir(parents=True, exist_ok=True)
        dest = unique_file(d, p.name)
        shutil.copy2(p, dest)
        saved.append(dest.relative_to(root).as_posix())
    title = resources.clean(title)
    append_brief(root, rid, title, text, saved, bool(follow_up))
    warnings += update_manifest(root, rid, saved)
    mode = mode_of(text)
    if old:
        old["files"] = join(split(old.get("files")) + saved)
        if mode != "default":
            old["mode"] = mode
        write_block(root, old)
        r = old
    else:
        r = {"id": rid, "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "title": title, "mode": mode,
             "status": "open", "text": f"{BRIEF.as_posix()}#{rid}", "files": join(saved),
             "rev before": rev_or_none(root)}
        write_block(root, r)
    print(json.dumps({"id": rid, "follow_up": bool(follow_up), "mode": r["mode"],
                      "dir": d.relative_to(root).as_posix() if saved else None, "files": saved,
                      "warnings": warnings}, indent=2))
    return 0


def rev_or_none(root):
    try:
        return repos.rev(root)
    except Exception:
        return "none"


# ---------- gates ----------

def gates(kind, tex, critical, mode):
    if mode == "quick":
        g, critical = ["G0", "G1"], False
    elif mode == "full":
        g, critical = ["G0", "G1", "G2", "G3", "G4"], True
    elif kind == "prose":
        g, critical = ["G0", "G1", "G4"], False
    else:
        g = ["G0", "G1", "G2"] + (["G3"] if critical else []) + ["G4"]
    if not tex:
        g = [x for x in g if x != "G0"]
    return g, critical


# ---------- context ----------

def brief_fields(p):
    f = {}
    for line in p.read_text().splitlines():
        m = re.match(r"^- ([a-z ]+):\s*(.*?)\s*$", line)
        if m and m.group(1) not in f:
            f[m.group(1)] = m.group(2)
    return f


def context(root):
    st = Path(root) / ".work" / "state.md"
    text = st.read_text() if st.is_file() else ""
    field = lambda k: (re.search(rf"^- {k}:\s*(.*)$", text, re.M) or [None, "none"])[1].strip()
    active = []
    bdir = Path(root) / ".work" / "briefs"
    for b in sorted(bdir.glob("*.md")) if bdir.is_dir() else []:
        if b.name.startswith("_"):
            continue
        f = brief_fields(b)
        if f.get("status", "open") != "done" and not f.get("request", "none").startswith("RQ"):
            active.append({"brief": b.stem, "status": f.get("status", "open"), "artifact files": f.get("artifact files"),
                           "claims": f.get("claims")})
    reqs = [{"id": r["id"], "status": r.get("status"), "title": r.get("title")} for r in parse_registry(root)
            if r.get("status") in ("open", "deferred")]
    ab = field("active brief")
    return {"stage": field("stage"), "active brief": ab, "stage in progress": bool(active) or ab not in ("none", ""),
            "briefs not done": active, "requests open or deferred": reqs}


# ---------- raise ----------

def do_raise(root, rid, affects, question, reason, scope, deliverable, recommend):
    get(root, rid)
    ids = [x.strip() for x in affects.split(",") if x.strip()]
    resources.check_ids(root, ids)
    if not (scope or deliverable):
        raise UsageError("raise is for scope or deliverable changes; other impacts get an ordinary card (approvals.md)")
    cid = f"D{max([int(c['id'][1:]) for c in decisions.all_cards(root) if c['id'][1:].isdigit()] or [0]) + 1}"
    event = "Request that changes the scope or a deliverable"
    idl = ", ".join(ids)
    evidence = "; ".join([f"{BRIEF.as_posix()}#{rid}"] + [f".work/{resources.ID_FILES[i[0]]}#{i}" for i in ids])
    text = (f"# {cid}\n\n"
            f"- class: blocking\n- status: open\n- event: {event}\n- header: Request {rid}\n"
            f"- question: {resources.clean(question)}\n- recommendation: {recommend}\n- reason: {resources.clean(reason)}\n"
            f"- depends: {idl}\n- evidence: {evidence}\n- answer: none\n- answered: none\n\n"
            f"## Request\n\n{rid}: {get(root, rid).get('title')}\n\n## Options\n\n"
            f"- A | Apply the request | the contract changes as the request asks; {idl} are revised and checked again\n"
            "- B | Stay within the contract | the request is done only as far as the approved contract allows\n"
            "- C | Drop the request | nothing changes; the request is recorded as dropped\n")
    if len(f"Request {rid}") > 12:
        text = text.replace(f"- header: Request {rid}", f"- header: {rid}")
    d = Path(root) / ".work" / "decisions"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{cid}.md"
    p.write_text(text)
    errs = decisions.lint_card(decisions.parse_card(p))
    if errs:
        p.unlink()
        for e in errs:
            print(f"{cid}: {e}", file=sys.stderr)
        return 1
    set_fields(root, rid, {"decisions": cid})
    print(json.dumps({"card": cid, "class": "blocking", "affects": ids, "request": rid}))
    return 0


# ---------- close, list, show, trace ----------

def captured(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args)
    return [x for x in buf.getvalue().splitlines() if x.strip()]


def do_close(root, rid, status, summary):
    if status not in STATUSES or status == "open":
        raise UsageError(f"status must be one of {', '.join(s for s in STATUSES if s != 'open')}")
    r = get(root, rid)
    pairs = {"status": status, "summary": resources.clean(summary)}
    base = r.get("rev before", "none")
    if status != "deferred" and "+" in base:
        try:
            commits = captured(repos.do_log, root, base)
            changed = captured(repos.do_diff, root, base, "--name-only")
        except (repos.UsageError, OSError):
            commits, changed = [], []
        pairs.update({"rev after": rev_or_none(root),
                      "commits": join([" ".join(c.split()[:2]) for c in commits]), "changed": join(changed)})
    set_fields(root, rid, pairs)
    print(json.dumps(get(root, rid), indent=2))
    return 0


def line(r):
    extra = [f"{k}: {r[k]}" for k in ("briefs", "decisions", "claims") if r.get(k) not in (None, "none")]
    return f"{r['id']} | {r.get('date')} | {r.get('status')} | {r.get('mode')} | {r.get('title')}" + \
        ("" if not extra else " | " + " | ".join(extra))


def do_list(root, n, status):
    rs = [r for r in parse_registry(root) if not status or r.get("status") == status]
    for r in sorted(rs, key=lambda r: -int(r["id"][2:]))[:n]:
        print(line(r))
    if not rs:
        print("no requests")
    return 0


def do_show(root, rid):
    r = get(root, rid)
    print("\n".join(f"- {k}: {r.get(k, 'none')}" for k in ("id",) + KEYS))
    p = Path(root) / BRIEF
    if p.is_file():
        for m in re.finditer(rf"(?ms)^### {rid}( follow-up)? \|.*?(?=^#{{2,3}} |\Z)", p.read_text()):
            print("\n" + m.group(0).rstrip())
    return 0


def do_trace(root, token):
    hits = []
    for r in parse_registry(root):
        why = []
        for k in ("briefs", "decisions", "claims", "files", "changed"):
            vals = split(r.get(k))
            if token in vals or any(v.endswith("/" + token) or token.endswith("/" + v) for v in vals):
                why.append(k)
        for c in split(r.get("commits")):
            parts = c.split()
            if len(parts) == 2 and len(token) >= 4 and parts[1].startswith(token):
                why.append(f"commits ({parts[0]})")
        if token == r["id"]:
            why.append("id")
        if why:
            hits.append((r, why))
    bdir = Path(root) / ".work" / "briefs"
    for b in sorted(bdir.glob("*.md")) if bdir.is_dir() else []:
        f = brief_fields(b)
        rq = f.get("request", "none")
        if rq.startswith("RQ") and (token == b.stem or token in split(f.get("claims")) or
                                    token in split(f.get("artifact files"))):
            if not any(h[0]["id"] == rq for h in hits):
                try:
                    hits.append((get(root, rq), [f"brief {b.stem}"]))
                except UsageError:
                    pass
    for r, why in hits:
        print(f"{line(r)} | matched: {', '.join(why)}")
    if not hits:
        print(f"no request touches {token}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("record"); p.add_argument("--slug", required=True); p.add_argument("--title", required=True)
    p.add_argument("--session"); p.add_argument("--transcript"); p.add_argument("--text-file")
    p.add_argument("--follow-up")
    p = sub.add_parser("gates"); p.add_argument("--kind", choices=("prose", "technical"), required=True)
    p.add_argument("--tex", action="store_true"); p.add_argument("--critical", action="store_true")
    p.add_argument("--mode", choices=("default", "quick", "full"), default="default")
    sub.add_parser("context")
    p = sub.add_parser("raise"); p.add_argument("rid"); p.add_argument("--affects", required=True)
    p.add_argument("--question", required=True); p.add_argument("--reason", required=True)
    p.add_argument("--scope-change", action="store_true"); p.add_argument("--deliverable-change", action="store_true")
    p.add_argument("--recommend", choices=("A", "B", "C"), default="A")
    p = sub.add_parser("set"); p.add_argument("rid"); p.add_argument("pairs", nargs="+")
    p = sub.add_parser("close"); p.add_argument("rid"); p.add_argument("--status", required=True)
    p.add_argument("--summary", required=True)
    p = sub.add_parser("list"); p.add_argument("-n", type=int, default=10); p.add_argument("--status")
    p = sub.add_parser("show"); p.add_argument("rid")
    p = sub.add_parser("trace"); p.add_argument("token")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    try:
        if a.cmd == "record":
            return do_record(root, a.slug, a.title, a.session, a.transcript, a.text_file, a.follow_up)
        if a.cmd == "gates":
            g, crit = gates(a.kind, a.tex, a.critical, a.mode)
            print(f"- gates: {', '.join(g)}\n- critical: {'yes' if crit else 'no'}")
            return 0
        if a.cmd == "context":
            print(json.dumps(context(root), indent=2))
            return 0
        if a.cmd == "raise":
            return do_raise(root, a.rid, a.affects, a.question, a.reason, a.scope_change, a.deliverable_change,
                            a.recommend)
        if a.cmd == "set":
            pairs = {}
            for x in a.pairs:
                if "=" not in x:
                    raise UsageError(f"not KEY=VALUE: {x}")
                k, v = x.split("=", 1)
                pairs[k.strip()] = v.strip()
            set_fields(root, a.rid, pairs)
            return 0
        if a.cmd == "close":
            return do_close(root, a.rid, a.status, a.summary)
        if a.cmd == "list":
            return do_list(root, a.n, a.status)
        if a.cmd == "show":
            return do_show(root, a.rid)
        if a.cmd == "trace":
            return do_trace(root, a.token)
    except (UsageError, resources.UsageError, decisions.UsageError, repos.UsageError) as e:
        print(f"request: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
