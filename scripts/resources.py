#!/usr/bin/env python3
"""The resources manifest of a research workflow project (.work/resources.manifest). Stdlib only.

`resources/` is an append-only drop folder for project inputs. It is excluded from the project repo (repos.py).
The manifest, committed in the .work repo, lists every file in it: path, sha256, size, date seen, and how it was handled.

Usage (run from the project root, or pass --root):
  resources.py init                   create the manifest from every file now in resources/ (intake, migration).
                                      Refuses if the manifest exists.
  resources.py scan [--json] [--warn] compare resources/ against the manifest. Prints new files, and anomalies: a file
                                      edited or deleted since it was seen. An anomaly is reported until it is warned once:
                                      --warn records it in the manifest (the orchestrator shows it to the human once).
                                      The old entry is kept; nothing is re-extracted.
  resources.py record <path> --summary S [--produced]
                                      a new file that does not bear on the contract: add it to the manifest, and (unless
                                      --produced) log it in decisions.md (class logged) so the checkpoint digest lists it.
                                      --produced: a file a workflow agent wrote into resources/ (literature notes).
  resources.py raise <path> --summary S --affects IDS --reason R [--scope-change] [--sow-version] [--recommend A|B|C]
                                      a new file that bears on the contract: write decision card D<n> with the options
                                      update the contract (A), ignore (B), stop (C), and add the file to the manifest.
                                      IDS: comma-separated R-, N-, P-, C- or A-IDs; each must exist in contract.md,
                                      claims.md or model.md. Class: blocking with --scope-change or --sow-version,
                                      checkpoint otherwise. Prints the card ID and its class.
  resources.py refresh <path> --reason R
                                      accept the current content of a file the workflow itself changed (a dated addendum to
                                      resources/BRIEF.md), or that the human asked to re-extract. Replaces its entry.

Manifest columns (tab-separated): path, sha256, size, seen (YYYY-MM-DD), origin (intake | new | produced | refreshed |
request), handled (- | recorded | D<n> | RQ<n>; request files are written by request.py), anomaly (- | edited <sha256 prefix> <date> | deleted <date>), summary.
Hidden files (names starting with ".") are ignored. Exit 0 on success, 1 on a failed card lint, 2 on usage errors.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decisions  # noqa: E402

MANIFEST = Path(".work") / "resources.manifest"
COLUMNS = ("path", "sha256", "size", "seen", "origin", "handled", "anomaly", "summary")
HEADER = ("# Resources manifest. One line per file in resources/. Written by ~/dotclaude/scripts/resources.py only.\n"
          "# " + "\t".join(COLUMNS) + "\n")
ID_FILES = {"R": "contract.md", "N": "contract.md", "P": "contract.md", "C": "claims.md", "A": "model.md"}


class UsageError(Exception):
    pass


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def current_files(root):
    res = Path(root) / "resources"
    if not res.is_dir():
        return {}
    out = {}
    for p in sorted(res.rglob("*")):
        rel = p.relative_to(root)
        if p.is_file() and not any(part.startswith(".") for part in rel.parts):
            out[rel.as_posix()] = p
    return out


def clean(s):
    return re.sub(r"[\t\r\n]+", " ", str(s)).strip() or "-"


def load(root):
    p = Path(root) / MANIFEST
    if not p.is_file():
        raise UsageError(f"no {MANIFEST}. Run: python3 ~/dotclaude/scripts/resources.py init")
    entries = {}
    for line in p.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        cols += ["-"] * (len(COLUMNS) - len(cols))
        e = dict(zip(COLUMNS, cols))
        entries[e["path"]] = e
    return entries


def save(root, entries):
    lines = [HEADER.rstrip("\n")]
    for path in sorted(entries):
        e = entries[path]
        lines.append("\t".join(clean(e.get(c, "-")) for c in COLUMNS))
    (Path(root) / MANIFEST).write_text("\n".join(lines) + "\n")


def entry(root, rel, origin, handled, summary):
    p = Path(root) / rel
    return {"path": rel, "sha256": sha256(p), "size": str(p.stat().st_size), "seen": date.today().isoformat(),
            "origin": origin, "handled": handled, "anomaly": "-", "summary": summary}


def check_path(root, path):
    p = Path(path) if Path(path).is_absolute() else Path(root) / path
    try:
        rel = p.resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        raise UsageError(f"not inside the project: {path}")
    if not rel.startswith("resources/"):
        raise UsageError(f"not under resources/: {path}")
    if not (Path(root) / rel).is_file():
        raise UsageError(f"no such file: {rel}")
    if "\t" in rel or "\n" in rel:
        raise UsageError(f"path contains a tab or newline: {rel!r}")
    return rel


# ---------- commands ----------

def do_init(root):
    p = Path(root) / MANIFEST
    if p.exists():
        raise UsageError(f"{MANIFEST} exists; never overwritten")
    if not (Path(root) / ".work").is_dir():
        raise UsageError("no .work/")
    entries = {rel: entry(root, rel, "intake", "-", "-") for rel in current_files(root)}
    save(root, entries)
    print(f"{MANIFEST}: {len(entries)} file(s)")
    return 0


def scan(root):
    entries = load(root)
    files = current_files(root)
    new = [rel for rel in files if rel not in entries]
    edited, deleted = [], []
    for rel, e in entries.items():
        an = e.get("anomaly", "-")
        if rel in files:
            h = sha256(files[rel])
            if h != e["sha256"] and not an.startswith(f"edited {h[:12]}"):
                edited.append({"path": rel, "sha256": h, "seen": e["seen"]})
        elif not an.startswith("deleted"):
            deleted.append({"path": rel, "seen": e["seen"]})
    return {"new": [{"path": rel, "size": files[rel].stat().st_size} for rel in new],
            "edited": edited, "deleted": deleted}


def do_scan(root, as_json, warn):
    r = scan(root)
    if warn and (r["edited"] or r["deleted"]):
        entries = load(root)
        today = date.today().isoformat()
        for x in r["edited"]:
            entries[x["path"]]["anomaly"] = f"edited {x['sha256'][:12]} {today}"
        for x in r["deleted"]:
            entries[x["path"]]["anomaly"] = f"deleted {today}"
        save(root, entries)
    if as_json:
        print(json.dumps(r, indent=2))
        return 0
    for x in r["new"]:
        print(f"new: {x['path']} ({x['size']} bytes)")
    for x in r["edited"]:
        print(f"WARNING edited: {x['path']} changed since it was seen on {x['seen']}. The manifest keeps the old entry; "
              "nothing is re-extracted unless the human asks.")
    for x in r["deleted"]:
        print(f"WARNING deleted: {x['path']} (seen on {x['seen']}) is gone. The manifest keeps the old entry; "
              "nothing is re-extracted unless the human asks.")
    print(f"resources: {len(r['new'])} new, {len(r['edited'])} edited, {len(r['deleted'])} deleted")
    return 0


def do_record(root, path, summary, produced):
    rel = check_path(root, path)
    entries = load(root)
    if rel in entries:
        raise UsageError(f"{rel} is already in the manifest")
    entries[rel] = entry(root, rel, "produced" if produced else "new", "recorded", summary)
    save(root, entries)
    if not produced:
        decisions.log_entry(root, f"new input recorded: {rel}", "orchestrator", "logged", "none",
                            f"{clean(summary)}; does not bear on the contract")
    print(f"recorded {rel}")
    return 0


def check_ids(root, ids):
    if not ids:
        raise UsageError("--affects needs at least one R-, N-, P-, C- or A-ID")
    for i in ids:
        m = re.fullmatch(r"([RNPCA])\d+", i)
        if not m:
            raise UsageError(f"not an R-, N-, P-, C- or A-ID: {i}")
        f = Path(root) / ".work" / ID_FILES[m.group(1)]
        if not f.is_file() or not re.search(rf"(?<![\w-]){i}(?![\w-])", f.read_text()):
            raise UsageError(f"{i} does not appear in .work/{ID_FILES[m.group(1)]}")


def do_raise(root, path, summary, affects, reason, scope_change, sow_version, recommend):
    rel = check_path(root, path)
    entries = load(root)
    if rel in entries:
        raise UsageError(f"{rel} is already in the manifest")
    ids = [x.strip() for x in affects.split(",") if x.strip()]
    check_ids(root, ids)
    blocking = scope_change or sow_version
    cid = f"D{max([int(c['id'][1:]) for c in decisions.all_cards(root) if c['id'][1:].isdigit()] or [0]) + 1}"
    event = ("New input that changes scope or is a new SoW version" if blocking
             else "New input that bears on the contract")
    idl = ", ".join(ids)
    evidence = "; ".join([rel] + [f".work/{ID_FILES[i[0]]}#{i}" for i in ids])
    text = (f"# {cid}\n\n"
            f"- class: {'blocking' if blocking else 'checkpoint'}\n- status: open\n- event: {event}\n- header: New input\n"
            f"- question: A new input file bears on the contract ({idl}): how should the project respond?\n"
            f"- recommendation: {recommend}\n- reason: {clean(reason)}\n- depends: {idl}\n- evidence: {evidence}\n"
            f"- answer: none\n- answered: none\n\n"
            f"## Input\n\n{rel}: {clean(summary)}\n\n"
            "## Options\n\n"
            f"- A | Update the contract | the contract is revised to take the new input into account; {idl} are revised and checked again\n"
            "- B | Ignore this file | the file stays recorded; the contract and the work continue as approved\n"
            "- C | Stop the project | the session ends and no further work runs until you restart it\n")
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
    entries[rel] = entry(root, rel, "new", cid, summary)
    save(root, entries)
    print(json.dumps({"card": cid, "class": "blocking" if blocking else "checkpoint", "affects": ids, "path": rel}))
    return 0


def do_refresh(root, path, reason):
    rel = check_path(root, path)
    entries = load(root)
    old = entries.get(rel)
    entries[rel] = entry(root, rel, "refreshed", old["handled"] if old else "-", reason)
    save(root, entries)
    print(f"refreshed {rel}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p = sub.add_parser("scan"); p.add_argument("--json", action="store_true"); p.add_argument("--warn", action="store_true")
    p = sub.add_parser("record"); p.add_argument("path"); p.add_argument("--summary", required=True)
    p.add_argument("--produced", action="store_true")
    p = sub.add_parser("raise"); p.add_argument("path"); p.add_argument("--summary", required=True)
    p.add_argument("--affects", required=True); p.add_argument("--reason", required=True)
    p.add_argument("--scope-change", action="store_true"); p.add_argument("--sow-version", action="store_true")
    p.add_argument("--recommend", choices=("A", "B", "C"), default="A")
    p = sub.add_parser("refresh"); p.add_argument("path"); p.add_argument("--reason", required=True)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    try:
        if a.cmd == "init":
            return do_init(root)
        if a.cmd == "scan":
            return do_scan(root, a.json, a.warn)
        if a.cmd == "record":
            return do_record(root, a.path, a.summary, a.produced)
        if a.cmd == "raise":
            return do_raise(root, a.path, a.summary, a.affects, a.reason, a.scope_change, a.sow_version, a.recommend)
        if a.cmd == "refresh":
            return do_refresh(root, a.path, a.reason)
    except (UsageError, decisions.UsageError) as e:
        print(f"resources: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
