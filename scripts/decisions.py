#!/usr/bin/env python3
"""Decision cards for the research workflow (.work/decisions/D<n>.md). Stdlib only.

Usage (run from the project root, or pass --root):
  decisions.py lint [D<n> ...]           check cards: fields, 2 to 4 options, recommendation, no technical vocabulary
  decisions.py next-id                   print the next free card ID
  decisions.py list [--status S]         one line per card
  decisions.py compress D<n> [...]       AskUserQuestion questions (JSON), recommended option first
  decisions.py provisional D<n>          checkpoint card: proceed with the recommendation, mark dependent claims provisional
  decisions.py accept D<n> [--option X]  record the human's answer; a different option than the provisional one reverses
  decisions.py reverse D<n> --to X       reverse a provisional decision: dependent claims back to draft, briefs requeued
  decisions.py checkpoint [--questions] [--close]
                                         the checkpoint screen: pending provisional cards, open cards, digest of logged
                                         decisions since the last checkpoint. No token usage.
                                         --questions prints the first dialog (JSON). --close records the checkpoint.

Dependent claims of a card: the C-IDs in `depends`, the claims whose `assumptions` use an A-ID in `depends`,
and every claim whose `depends_on` reaches one of those, transitively. Refuted claims are left alone.
Exit 0 on success, 1 on lint errors, 2 on usage errors.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rw_vocab import technical_terms, workflow_refs  # noqa: E402

CLASSES = ("blocking", "checkpoint")
STATUSES = ("open", "provisional", "accepted", "reversed")
CARD_KEYS = ("class", "status", "event", "header", "question", "recommendation", "reason", "depends", "evidence",
             "answer", "answered")
HUMAN_KEYS = ("header", "question", "reason")


class UsageError(Exception):
    pass


# ---------- cards ----------

def card_path(root, cid):
    return Path(root) / ".work" / "decisions" / f"{cid}.md"


def parse_card(path):
    text = Path(path).read_text()
    m = re.match(r"#\s*(D\d+)\s*$", text.splitlines()[0] if text else "")
    card = {"id": m.group(1) if m else Path(path).stem, "options": [], "path": Path(path)}
    for line in text.splitlines():
        km = re.match(r"^- ([a-z]+):\s*(.*?)\s*$", line)
        if km and km.group(1) in CARD_KEYS:
            card.setdefault(km.group(1), km.group(2))
            continue
        om = re.match(r"^- ([A-D])\s*\|\s*(.*?)\s*\|\s*(.*?)\s*$", line)
        if om:
            card["options"].append({"key": om.group(1), "label": om.group(2), "consequence": om.group(3)})
    return card


def set_card_fields(path, **fields):
    lines = Path(path).read_text().splitlines()
    for k, v in fields.items():
        for i, line in enumerate(lines):
            if re.match(rf"^- {k}:", line):
                lines[i] = f"- {k}: {v}"
                break
        else:
            raise UsageError(f"{path}: no `- {k}:` line")
    Path(path).write_text("\n".join(lines) + "\n")


def all_cards(root):
    d = Path(root) / ".work" / "decisions"
    paths = sorted((p for p in d.glob("D*.md")), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0)) if d.is_dir() else []
    return [parse_card(p) for p in paths]


def load(root, cid):
    p = card_path(root, cid)
    if not p.is_file():
        raise UsageError(f"no card {p}")
    return parse_card(p)


def ids(field, prefix):
    return re.findall(rf"\b{prefix}\d+\b", field or "")


def lint_card(card):
    errs = []
    for k in CARD_KEYS:
        if not card.get(k):
            errs.append(f"missing `- {k}:`")
    if card.get("class") and card["class"] not in CLASSES:
        errs.append(f"class {card['class']!r} is not one of {', '.join(CLASSES)} (logged decisions get no card)")
    if card.get("status") and card["status"] not in STATUSES:
        errs.append(f"status {card['status']!r} is not one of {', '.join(STATUSES)}")
    if card.get("class") == "blocking" and card.get("status") in ("provisional", "reversed"):
        errs.append("a blocking decision is never provisional")
    opts = card["options"]
    if not 2 <= len(opts) <= 4:
        errs.append(f"{len(opts)} options; need 2 to 4")
    keys = [o["key"] for o in opts]
    if len(set(keys)) != len(keys):
        errs.append("duplicate option letters")
    if card.get("recommendation") and card["recommendation"] not in keys:
        errs.append(f"recommendation {card['recommendation']!r} is not an option")
    if card.get("answer") not in (None, "none") and card["answer"] not in keys:
        errs.append(f"answer {card['answer']!r} is not an option")
    if len(card.get("header", "")) > 12:
        errs.append(f"header longer than 12 characters: {card['header']!r}")
    if card.get("question") and not card["question"].endswith("?"):
        errs.append("question does not end with '?'")
    if card.get("question") and len(re.findall(r"[.?!](\s|$)", card["question"])) > 1:
        errs.append("question is more than one sentence")
    for o in opts:
        n = len(o["label"].split())
        if not 1 <= n <= 5:
            errs.append(f"option {o['key']} label has {n} words; need 1 to 5")
        if not o["consequence"]:
            errs.append(f"option {o['key']} has no consequence")
    texts = [(k, card.get(k, "")) for k in HUMAN_KEYS] + \
            [(f"option {o['key']}", o["label"] + " " + o["consequence"]) for o in opts]
    for where, t in texts:
        for word, what in technical_terms(t):
            errs.append(f"{where}: technical term {word!r} ({what}); the system decides this, never the human")
        for word, what in workflow_refs(t):
            errs.append(f"{where}: {what} {word!r}; say what it is in plain words (IDs belong in `depends` and `evidence`)")
    return errs


def compress(card):
    """One AskUserQuestion question for a card, recommended option first."""
    rec = card["recommendation"]
    opts = sorted(card["options"], key=lambda o: o["key"] != rec)
    out = []
    for o in opts:
        if o["key"] == rec:
            out.append({"label": f"{o['label']} (Recommended)", "description": f"{o['consequence']} Why: {card['reason']}"})
        else:
            out.append({"label": o["label"], "description": o["consequence"]})
    return {"question": f"{card['question']} ({refs(card)})", "header": card["header"], "multiSelect": False, "options": out}


def refs(card, extra=()):
    """The trailing `Refs:` part shown to the human: the card ID, then its dependencies."""
    deps = [d.strip() for d in (card.get("depends") or "").split(",") if d.strip() and d.strip() != "none"]
    return "Refs: " + ", ".join([card["id"], *deps, *extra])


def option(card, key):
    for o in card["options"]:
        if o["key"] == key:
            return o
    raise UsageError(f"{card['id']} has no option {key}")


# ---------- claims ----------

def parse_claim_blocks(path):
    """claims.md -> (lines, {C-ID: (start, end, {key: value})})."""
    lines = Path(path).read_text().splitlines() if Path(path).is_file() else []
    blocks, cur, start = {}, None, 0
    for i, line in enumerate(lines + ["## END"]):
        if line.startswith("## "):
            if cur:
                fields = {}
                for j in range(start, i):
                    m = re.match(r"^- ([a-z_]+):\s*(.*?)\s*$", lines[j])
                    if m:
                        fields[m.group(1)] = m.group(2)
                blocks[cur] = (start, i, fields)
            m = re.match(r"^## (C\d+)\s*$", line)
            cur, start = (m.group(1), i + 1) if m else (None, 0)
    return lines, blocks


def write_claim_fields(path, updates):
    """updates: {C-ID: {key: value}}. Sets existing keys in place; adds missing ones after the last key line."""
    lines, blocks = parse_claim_blocks(path)
    for cid in sorted(updates, key=lambda c: -blocks[c][0]):
        start, end, _ = blocks[cid]
        for k, v in updates[cid].items():
            for j in range(start, end):
                if re.match(rf"^- {k}:", lines[j]):
                    lines[j] = f"- {k}: {v}"
                    break
            else:
                last = max((j for j in range(start, end) if lines[j].startswith("- ")), default=start - 1)
                lines.insert(last + 1, f"- {k}: {v}")
                end += 1
    Path(path).write_text("\n".join(lines) + "\n")


def affected_claims(root, card):
    _, blocks = parse_claim_blocks(Path(root) / ".work" / "claims.md")
    claims = {c: f for c, (_, _, f) in blocks.items()}
    dep = card.get("depends", "")
    direct = set(ids(dep, "C")) & set(claims)
    a_ids = set(ids(dep, "A"))
    for c, f in claims.items():
        if a_ids & set(ids(f.get("assumptions", ""), "A")):
            direct.add(c)
    out, changed = set(direct), True
    while changed:
        changed = False
        for c, f in claims.items():
            if c not in out and set(ids(f.get("depends_on", ""), "C")) & out:
                out.add(c)
                changed = True
    return sorted((c for c in out if claims[c].get("status") != "refuted"), key=lambda c: int(c[1:])), claims


def id_list(field):
    return [x for x in re.findall(r"D\d+", field or "")]


def fmt_list(xs):
    return ", ".join(xs) if xs else "none"


# ---------- log, briefs, state ----------

def log_entry(root, title, made_by, cls, card_id, reason):
    p = Path(root) / ".work" / "decisions.md"
    text = p.read_text() if p.is_file() else "# Decisions\n"
    entry = (f"\n## {date.today().isoformat()} | {title}\n- made by: {made_by}\n- class: {cls}\n- card: {card_id}\n"
             f"- reason: {reason}\n- routing: n/a\n")
    p.write_text(text.rstrip("\n") + "\n" + entry)


def requeue_briefs(root, claim_ids, card_id):
    out = []
    bdir = Path(root) / ".work" / "briefs"
    for b in sorted(bdir.glob("*.md")) if bdir.is_dir() else []:
        if b.name.startswith("_"):
            continue
        text = b.read_text()
        m = re.search(r"^- claims:\s*(.*)$", text, re.M)
        if not m or not set(ids(m.group(1), "C")) & set(claim_ids):
            continue
        text = re.sub(r"^- status:.*$", "- status: requeued", text, count=1, flags=re.M)
        text = text.rstrip("\n") + f"\n\nRequeued {date.today().isoformat()}: {card_id} reversed. Rerun this brief.\n"
        b.write_text(text)
        out.append(b.stem)
    return out


def add_requeued_to_state(root, lines):
    p = Path(root) / ".work" / "state.md"
    if not p.is_file():
        return
    text = p.read_text()
    m = re.search(r"^## Requeued\s*$", text, re.M)
    block = "".join(f"- {line}\n" for line in lines)
    if m:
        rest = text[m.end():]
        nxt = re.search(r"^## ", rest, re.M)
        cut = m.end() + (nxt.start() if nxt else len(rest))
        body = text[m.end():cut].strip("\n")
        body = "\n".join(x for x in body.splitlines() if x.strip() and x.strip() != "- none")
        text = text[:m.end()] + "\n\n" + (body + "\n" if body else "") + block + "\n" + text[cut:].lstrip("\n")
    else:
        text = text.rstrip("\n") + "\n\n## Requeued\n\nRun these briefs first, in order.\n\n" + block
    p.write_text(text)


# ---------- actions ----------

def do_provisional(root, cid):
    card = load(root, cid)
    if card["class"] != "checkpoint":
        raise UsageError(f"{cid} is {card['class']}; only checkpoint decisions are provisional")
    if card["status"] != "open":
        raise UsageError(f"{cid} is {card['status']}, not open")
    affected, claims = affected_claims(root, card)
    updates = {}
    for c in affected:
        f = claims[c]
        prov = id_list(f.get("provisional_on"))
        u = {"provisional_on": fmt_list(sorted(set(prov) | {cid}, key=lambda d: int(d[1:])))}
        if f.get("status") != "provisional":
            u["base_status"] = f.get("status", "draft")
            u["status"] = "provisional"
        updates[c] = u
    if updates:
        write_claim_fields(Path(root) / ".work" / "claims.md", updates)
    set_card_fields(card["path"], status="provisional", answer=card["recommendation"])
    o = option(card, card["recommendation"])
    log_entry(root, f"{cid} provisional: {o['label']}", "orchestrator", "checkpoint", cid,
              f"recommendation taken until the next checkpoint; provisional claims: {fmt_list(affected)}")
    return affected


def release(root, cid, affected, claims):
    updates = {}
    for c in affected:
        f = claims[c]
        prov = [d for d in id_list(f.get("provisional_on")) if d != cid]
        u = {"provisional_on": fmt_list(prov)}
        if f.get("status") == "provisional" and not prov:
            u["status"] = f.get("base_status") if f.get("base_status") not in (None, "none") else "draft"
            u["base_status"] = "none"
        updates[c] = u
    if updates:
        write_claim_fields(Path(root) / ".work" / "claims.md", updates)


def do_accept(root, cid, opt=None):
    card = load(root, cid)
    if card["status"] in ("accepted", "reversed"):
        raise UsageError(f"{cid} is already {card['status']}")
    if card["status"] == "provisional":
        if opt and opt != card["answer"]:
            return do_reverse(root, cid, opt)
        affected, claims = affected_claims(root, card)
        release(root, cid, affected, claims)
        set_card_fields(card["path"], status="accepted", answered=f"{date.today().isoformat()} by human")
        log_entry(root, f"{cid} accepted: {option(card, card['answer'])['label']}", "human", card["class"], cid,
                  "provisional decision confirmed at a checkpoint")
        return {"accepted": cid, "released": affected}
    key = opt or card["recommendation"]
    option(card, key)
    set_card_fields(card["path"], status="accepted", answer=key, answered=f"{date.today().isoformat()} by human")
    log_entry(root, f"{cid} decided: {option(card, key)['label']}", "human", card["class"], cid, card["question"])
    return {"accepted": cid, "answer": key}


def do_reverse(root, cid, to):
    card = load(root, cid)
    if card["status"] != "provisional":
        raise UsageError(f"{cid} is {card['status']}; only a provisional decision can be reversed")
    option(card, to)
    if to == card["answer"]:
        raise UsageError(f"{cid}: option {to} is the provisional answer; use accept")
    affected, claims = affected_claims(root, card)
    updates = {}
    for c in affected:
        f = claims[c]
        prov = [d for d in id_list(f.get("provisional_on")) if d != cid]
        notes = f.get("notes", "none")
        note = f"requeued by {cid} reversal"
        updates[c] = {"status": "draft", "base_status": "none", "provisional_on": fmt_list(prov), "verified_by": "none",
                      "notes": note if notes in ("", "none") else f"{notes}; {note}"}
    if updates:
        write_claim_fields(Path(root) / ".work" / "claims.md", updates)
    briefs = requeue_briefs(root, affected, cid)
    old = option(card, card["answer"])["label"]
    new = option(card, to)["label"]
    set_card_fields(card["path"], status="reversed", answer=to, answered=f"{date.today().isoformat()} by human")
    add_requeued_to_state(root, [f"briefs/{b}.md ({cid} reversed: {new}; claims {fmt_list(affected)})" for b in briefs]
                          or [f"no brief covers {fmt_list(affected)} ({cid} reversed: {new}); plan one"])
    log_entry(root, f"{cid} reversed: {old} -> {new}", "human", card["class"], cid,
              f"claims back to draft: {fmt_list(affected)}; briefs requeued: {fmt_list(briefs)}")
    return {"reversed": cid, "to": to, "claims": affected, "briefs": briefs}


def digest(root):
    """Logged decisions in decisions.md since the last checkpoint entry, for the human: routing, budget and other
    system-only entries (a routing field, or a title with technical vocabulary) stay in the log and are not shown."""
    p = Path(root) / ".work" / "decisions.md"
    if not p.is_file():
        return []
    entries = re.split(r"(?m)^(?=## )", p.read_text())
    out = []
    for e in entries:
        head = e.splitlines()[0] if e.strip() else ""
        if not head.startswith("## ") or "<" in head:
            continue
        if re.search(r"\|\s*checkpoint closed", head):
            out = []
            continue
        cls = re.search(r"^- class:\s*(\S+)", e, re.M)
        if cls and cls.group(1) != "logged":
            continue
        if not cls and not re.search(r"^- routing:\s*(?!n/a)\S", e, re.M):
            continue
        if re.search(r"^- routing:\s*(?!n/a)\S", e, re.M) or technical_terms(head):
            continue
        out.append(head[3:].strip())
    return out


def checkpoint_screen(root):
    cards = all_cards(root)
    prov = [c for c in cards if c.get("status") == "provisional"]
    opened = [c for c in cards if c.get("status") == "open"]
    out = ["# Checkpoint", ""]
    out.append(f"## Provisional decisions ({len(prov)})")
    out.append("")
    for c in prov:
        o = option(c, c["answer"])
        affected, _ = affected_claims(root, c)
        out.append(f"- **{c['question']}**")
        out.append(f"  - taken: {o['label']}. {o['consequence']}")
        out.append(f"  - why: {c['reason']}")
        others = "; ".join(x["label"] for x in c["options"] if x["key"] != c["answer"])
        out.append(f"  - alternatives: {others}")
        out.append(f"  - {refs(c)}" + (f"; provisional until decided: {fmt_list(affected)}" if affected else ""))
    if not prov:
        out.append("- none")
    out += ["", f"## Open questions ({len(opened)})", ""]
    out += [f"- {c['question']} ({c['class']}; {refs(c)})" for c in opened] or ["- none"]
    out += ["", "## Decided by the system since the last checkpoint", ""]
    out += [f"- {d}" for d in digest(root)] or ["- none"]
    return "\n".join(out) + "\n", prov


def checkpoint_questions(prov):
    if not prov:
        return []
    taken = "; ".join(f"{c['question'].rstrip('?')}: {option(c, c['answer'])['label']}" for c in prov)
    ids_ = ", ".join(c["id"] for c in prov)
    return [{"question": f"Make these {len(prov)} provisional decisions final? {taken}. (Refs: {ids_})", "header": "Checkpoint",
             "multiSelect": False, "options": [
                 {"label": "Accept all (Recommended)", "description": "Every provisional decision becomes final. Work continues."},
                 {"label": "Review individually", "description": "One question per decision; any can be reversed."}]}]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lint"); p.add_argument("ids", nargs="*")
    sub.add_parser("next-id")
    p = sub.add_parser("list"); p.add_argument("--status")
    p = sub.add_parser("compress"); p.add_argument("ids", nargs="+")
    p = sub.add_parser("provisional"); p.add_argument("id")
    p = sub.add_parser("accept"); p.add_argument("id"); p.add_argument("--option")
    p = sub.add_parser("reverse"); p.add_argument("id"); p.add_argument("--to", required=True)
    p = sub.add_parser("checkpoint"); p.add_argument("--questions", action="store_true"); p.add_argument("--close", action="store_true")
    a = ap.parse_args(argv)
    root = a.root
    try:
        if a.cmd == "lint":
            cards = [load(root, i) for i in a.ids] if a.ids else all_cards(root)
            bad = 0
            for c in cards:
                for e in lint_card(c):
                    print(f"{c['id']}: {e}")
                    bad += 1
            print(f"{len(cards)} card(s), {bad} error(s)")
            return 1 if bad else 0
        if a.cmd == "next-id":
            n = max([int(c["id"][1:]) for c in all_cards(root) if c["id"][1:].isdigit()] or [0])
            print(f"D{n + 1}")
            return 0
        if a.cmd == "list":
            for c in all_cards(root):
                if not a.status or c.get("status") == a.status:
                    print(f"{c['id']}  {c.get('class')}  {c.get('status')}  {c.get('question')}")
            return 0
        if a.cmd == "compress":
            cards = [load(root, i) for i in a.ids]
            for c in cards:
                errs = lint_card(c)
                if errs:
                    raise UsageError(f"{c['id']} fails lint: {errs[0]}")
            batches = [[compress(c) for c in cards[i:i + 4]] for i in range(0, len(cards), 4)]
            print(json.dumps(batches if len(batches) > 1 else batches[0], indent=2))
            return 0
        if a.cmd == "provisional":
            print(json.dumps({"provisional": a.id, "claims": do_provisional(root, a.id)}))
            return 0
        if a.cmd == "accept":
            print(json.dumps(do_accept(root, a.id, a.option)))
            return 0
        if a.cmd == "reverse":
            print(json.dumps(do_reverse(root, a.id, a.to)))
            return 0
        if a.cmd == "checkpoint":
            screen, prov = checkpoint_screen(root)
            if a.close:
                log_entry(root, "checkpoint closed", "human", "checkpoint", "none",
                          f"provisional decisions reviewed: {fmt_list([c['id'] for c in prov])}")
                print("checkpoint closed")
            elif a.questions:
                print(json.dumps(checkpoint_questions(prov), indent=2))
            else:
                print(screen, end="")
            return 0
    except UsageError as e:
        print(f"decisions: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
