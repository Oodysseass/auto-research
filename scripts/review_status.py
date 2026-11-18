#!/usr/bin/env python3
"""Convergence status of one artifact's review loop. Stdlib only.

Usage:
  review_status.py <issues-dir> <artifact-slug> [--brief BRIEF.md] [--json]

Gates and G2 reviewers come from the brief's `- gates:` field, e.g. `G0, G1, G2[assumption-auditor], G3`
(default: G1, G2 with all three G2 reviewers, G3 if critical), plus any gate that has reports.

  review_status.py <issues-dir> <artifact-slug> --hashes
      Prints the Review log `hashes` cell for the current content: each file in the brief's
      `- artifact files:` field, .work/model.md, .work/glossary.md, and `claims`, a hash of the
      claims.md entries in the brief's `- claims:` field and their transitive depends_on (content keys
      only: label, type, statement, assumptions, depends_on). Any change to these between two clean
      rounds is an edit: the rounds are not consecutive and a clean round is voided.

Reads every report, producer response and arbiter ruling for the slug in <issues-dir>
(file names per templates/project/.work/issues/README.md), and the brief whose
`- artifact slug:` field equals the slug (default: <issues-dir>/../briefs/*.md).
Applies the review-gates "Stopping rules" in their order (converged, deadlock, stalled,
round limit) to each gate reviewer, then to each gate, then to the artifact.

Prints one line per gate, `open issues: ...`, and a last line
  overall: <status> -> <action> [<gate> <reviewer>]
status: converged | deadlocked | stalled | max_rounds | open
action: none | run | next-gate | arbitrate | arbitrate-mythos | human
`open -> next-gate` means a critical artifact has one clean round of the gate and may move on:
a clean G3 round on the same content completes it. Exit 0, or 2 on usage errors.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

GATE_ORDER = ["G0", "G1", "G2", "G3", "G4", "G5"]
DEFAULT_REVIEWERS = {
    "G0": ["lint-tex"], "G1": ["conformance-reviewer"],
    "G2": ["assumption-auditor", "proof-checker", "counterexample-hunter"],
    "G3": ["codex"], "G4": ["style-reviewer"], "G5": [],
}
MAX_ROUNDS = 5
BAD = ("blocking", "major")


# ---------- loading ----------

def load_dir(d, slug):
    reports, responses, rulings = {}, {}, {}
    s = re.escape(slug)
    rep = re.compile(rf"^{s}\.(G[0-5])\.([a-z0-9-]+)\.r(\d+)\.json$")
    rsp = re.compile(rf"^{s}\.(G[0-5])\.([a-z0-9-]+)\.r(\d+)\.response\.json$")
    rul = re.compile(rf"^{s}\.(G[0-5])\.([a-z0-9-]+)\.i(\d+)\.ruling(\d+)\.json$")
    for p in sorted(Path(d).iterdir()):
        for rx, store in ((rsp, responses), (rep, reports)):
            m = rx.match(p.name)
            if m:
                store.setdefault((m.group(1), m.group(2)), {})[int(m.group(3))] = json.loads(p.read_text())
                break
        m = rul.match(p.name)
        if m:
            r = json.loads(p.read_text())
            iid = r.get("issue_id") or f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
            rulings.setdefault(iid, {})[int(m.group(4))] = r
    return reports, responses, rulings


def parse_brief(path):
    text = Path(path).read_text()
    fields = {}
    for m in re.finditer(r"^- ([a-z ]+):\s*(.*?)\s*$", text, flags=re.M):
        fields.setdefault(m.group(1).strip(), m.group(2).strip().strip("`"))
    m = re.search(r"^\s*-?\s*rounds:\s*(\d+)", text, flags=re.M)
    rounds = int(m.group(1)) if m else None
    log = []
    sec = re.search(r"^## Review log\s*$(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    if sec:
        header = None
        for line in sec.group(1).splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]
            if header is None:
                header = [c.lower() for c in cells]
                continue
            if all(set(c) <= set("-: ") for c in cells):
                continue
            row = dict(zip(header, cells))
            try:
                row["round"] = int(str(row.get("round", "")).lstrip("r"))
            except ValueError:
                continue
            hashes = {}
            for part in re.split(r"[;,]\s*", row.get("hashes", "")):
                if "=" in part:
                    f, h = part.rsplit("=", 1)
                    hashes[f.strip().strip("`")] = h.strip().strip("`")
            row["hashes"] = hashes
            log.append(row)
    return fields, rounds, log


def find_briefs(issues_dir, slug):
    bdir = Path(issues_dir).resolve().parent / "briefs"
    out = []
    for p in sorted(bdir.glob("*.md")) if bdir.is_dir() else []:
        if p.name.startswith("_"):
            continue
        if re.search(rf"^- artifact slug:\s*`?{re.escape(slug)}`?\s*$", p.read_text(), flags=re.M):
            out.append(p)
    return out


def blob_hash(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


CONTEXT_FILES = (".work/model.md", ".work/glossary.md")
CLAIM_CONTENT_KEYS = ("label", "type", "statement", "assumptions", "depends_on")


def parse_claims(path):
    """claims.md -> {C-ID: {key: value}}."""
    claims, cur = {}, None
    if not Path(path).is_file():
        return claims
    for line in Path(path).read_text().splitlines():
        m = re.match(r"^## (C\d+)\s*$", line)
        if m:
            cur = claims.setdefault(m.group(1), {})
            continue
        if line.startswith("## "):
            cur = None
            continue
        m = re.match(r"^- ([a-z_]+):\s*(.*?)\s*$", line)
        if cur is not None and m:
            cur[m.group(1)] = m.group(2)
    return claims


def claim_closure(claims, ids):
    seen, todo = set(), list(ids)
    while todo:
        c = todo.pop()
        if c in seen:
            continue
        seen.add(c)
        deps = claims.get(c, {}).get("depends_on", "none")
        todo += [d for d in re.findall(r"C\d+", deps) if d not in seen]
    return sorted(seen, key=lambda c: int(c[1:]))


def claims_hash(root, ids):
    """Hash of the content keys of the claims `ids` and their transitive dependencies.
    Bookkeeping keys (status, verified_by, refuted_by, notes) are left out, so status updates do not count as edits."""
    claims = parse_claims(Path(root) / ".work" / "claims.md")
    parts = []
    for c in claim_closure(claims, ids):
        entry = claims.get(c)
        body = "missing" if entry is None else "\n".join(f"{k}: {entry.get(k, '')}" for k in CLAIM_CONTENT_KEYS)
        parts.append(f"## {c}\n{body}")
    return hashlib.sha1("\n".join(parts).encode()).hexdigest()


def split_list(field):
    return [x.strip().strip("`") for x in re.split(r"[,;]\s*", field or "") if x.strip() and x.strip().lower() != "none"]


def current_hash(root, key, claim_ids):
    if key == "claims":
        return claims_hash(root, claim_ids)
    p = Path(root) / key
    return blob_hash(p) if p.is_file() else "missing"


def content_hashes(root, fields):
    """The review content of an artifact: its files, model.md, glossary.md, and its claims with dependencies."""
    files = split_list(fields.get("artifact files"))
    if not files:
        raise ValueError("the brief has no `- artifact files:` field")
    ids = split_list(fields.get("claims"))
    keys = files + list(CONTEXT_FILES) + (["claims"] if ids else [])
    return {k: current_hash(root, k, ids) for k in keys}


def format_hashes(h):
    return "; ".join(f"{k}={v[:12]}" for k, v in h.items())


def same_hash(a, b):
    if not a or not b:
        return False
    n = min(len(a), len(b))
    return n >= 7 and a[:n] == b[:n]


def same_content(h1, h2):
    """Two {file: hash} maps describe the same content."""
    return bool(h1) and set(h1) == set(h2) and all(same_hash(h1[f], h2[f]) for f in h1)


# ---------- analysis ----------

class Ctx:
    def __init__(self, reports, responses, rulings, critical, main, budget, log, root, claim_ids=()):
        self.reports, self.responses, self.rulings = reports, responses, rulings
        self.critical, self.main, self.budget, self.root = critical, main, budget, root
        self.hashes = {}
        for row in log:
            key = (row.get("gate", ""), row.get("reviewer", ""), row["round"])
            if row["hashes"]:
                self.hashes[key] = row["hashes"]
        self.current = {}
        self.warnings = []
        if not self.hashes:
            self.warnings.append("no content hashes in the brief's Review log: edit and stall checks skipped")
        for key in {k for h in self.hashes.values() for k in h}:
            self.current[key] = current_hash(root, key, claim_ids)
        self.canon = {}
        for streams in reports.values():
            for rep in streams.values():
                for i in rep.get("issues", []):
                    if i.get("duplicate_of"):
                        self.canon[i["id"]] = i["duplicate_of"]

    def canonical(self, iid):
        return self.canon.get(iid, iid)

    def ruling_state(self, iid):
        """Return (governing ruling or None, pending action or None)."""
        rs = self.rulings.get(iid, {})
        if 2 in rs:
            return rs[2], None
        if 1 in rs:
            if rs[1]["ruling"] == "needs_human" or self.main:
                return None, "arbitrate-mythos"
            return rs[1], None
        return None, None

    def closed(self, iid):
        gov, _ = self.ruling_state(self.canonical(iid))
        return gov is not None and gov["ruling"] == "producer_right"

    def counted(self, rep):
        """Issues of a report that count: not closed by a producer_right ruling."""
        return [i for i in rep.get("issues", []) if not self.closed(i["id"])]

    def is_clean(self, rep):
        return not any(i["severity"] in BAD for i in self.counted(rep))

    def round_hashes(self, gate, reviewer, rnd):
        return self.hashes.get((gate, reviewer, rnd))

    def unedited(self, h):
        """Content reviewed in a round is still the current content (unknown hashes count as unedited)."""
        if h is None:
            return True
        return same_content(h, {f: self.current.get(f, "missing") for f in h})


def stream_status(ctx, gate, reviewer):
    rounds = ctx.reports.get((gate, reviewer))
    if not rounds:
        return {"status": "open", "action": "run", "reason": "not run yet"}
    last = max(rounds)
    rep = rounds[last]
    h_last = ctx.round_hashes(gate, reviewer, last)
    clean = ctx.is_clean(rep)
    valid = clean and ctx.unedited(h_last)

    # 1. Converged.
    if valid:
        needs_two = ctx.critical and gate in ("G1", "G2", "G4")
        if not needs_two:
            return {"status": "converged", "action": "none", "reason": f"clean round r{last}"}
        prev = rounds.get(last - 1)
        h_prev = ctx.round_hashes(gate, reviewer, last - 1)
        if prev is not None and ctx.is_clean(prev) and (
                (h_prev is None and h_last is None) or same_content(h_prev or {}, h_last or {})):
            return {"status": "converged", "action": "none", "reason": f"clean rounds r{last - 1} and r{last}, no edit"}
        if gate in ("G1", "G2"):
            for (g, rv), g3 in ctx.reports.items():
                if g != "G3":
                    continue
                for r3, rep3 in g3.items():
                    h3 = ctx.round_hashes(g, rv, r3)
                    same = same_content(h3 or {}, h_last or {}) if (h3 or h_last) else rep3.get("commit") == rep.get("commit")
                    if ctx.is_clean(rep3) and same:
                        return {"status": "converged", "action": "none",
                                "reason": f"clean round r{last} and clean G3 {rv} r{r3} on the same content"}
            return {"status": "open", "action": "next-gate",
                    "reason": f"one clean round r{last}; a clean G3 round on the same content completes it"}
        return {"status": "open", "action": "run", "reason": f"one clean round r{last}; critical needs two"}
    if clean:
        return {"status": "open", "action": "run", "reason": f"clean round r{last} voided by a later edit; rerun from G1"}

    # 2. Deadlock, per canonical issue present in the last round.
    present = {ctx.canonical(i["id"]) for i in ctx.counted(rep) if i["severity"] in BAD}
    for cid in sorted(present):
        rejections = kept = 0
        for r in sorted(rounds):
            resp = ctx.responses.get((gate, reviewer), {}).get(r)
            if not resp:
                continue
            if any(x["issue_id"] in (cid,) or ctx.canonical(x["issue_id"]) == cid
                   for x in resp["responses"] if x["status"] == "rejected"):
                rejections += 1
                nxt = rounds.get(r + 1)
                if nxt and any(ctx.canonical(i["id"]) == cid for i in nxt.get("issues", [])):
                    kept += 1
        gov, pending = ctx.ruling_state(cid)
        if gov is not None and gov["ruling"] == "reviewer_right":
            if rejections >= 3:
                return {"status": "deadlocked", "action": "human", "issue": cid,
                        "reason": f"{cid} rejected again after a reviewer_right ruling"}
            continue
        if gov is not None and gov["ruling"] == "needs_human":
            return {"status": "deadlocked", "action": "human", "issue": cid,
                    "reason": f"{cid}: governing ruling is needs_human", "question": gov.get("human_question")}
        if pending:
            return {"status": "deadlocked", "action": pending, "issue": cid, "reason": f"{cid}: ruling 1 needs ruling 2"}
        if rejections >= 2 and kept >= 2:
            return {"status": "deadlocked", "action": "arbitrate", "issue": cid,
                    "reason": f"{cid} rejected {rejections} times and kept {kept} times"}

    # 3. Stalled: a revision with fixes but no diff, or a hash that repeats an earlier, different round.
    if h_last is not None:
        h_prev = ctx.round_hashes(gate, reviewer, last - 1)
        resp_prev = ctx.responses.get((gate, reviewer), {}).get(last - 1)
        fixed = resp_prev and any(x["status"] == "fixed" for x in resp_prev["responses"])
        if h_prev is not None and fixed and same_content(h_prev, h_last):
            return {"status": "stalled", "action": "human", "reason": f"r{last - 1} response says fixed, but r{last} has no diff"}
        for r in sorted(rounds):
            h = ctx.round_hashes(gate, reviewer, r)
            if r < last - 1 and h is not None and same_content(h, h_last) and not (h_prev and same_content(h_prev, h_last)):
                return {"status": "stalled", "action": "human", "reason": f"r{last} content repeats r{r}"}

    # 4. Round limit.
    if last >= ctx.budget:
        return {"status": "max_rounds", "action": "human", "reason": f"r{last} reached the round limit {ctx.budget}"}

    resp = ctx.responses.get((gate, reviewer), {}).get(last)
    if resp and any(x["status"] == "needs_human" for x in resp["responses"]):
        return {"status": "open", "action": "human", "reason": "the producer marked an issue needs_human"}
    return {"status": "open", "action": "run", "reason": f"r{last} has blocking or major issues"}


def parse_gates(field):
    """`G0, G1, G2[assumption-auditor proof-checker], G3` -> {gate: [reviewers] or None}."""
    out = {}
    for m in re.finditer(r"(G[0-5])(?:\[([^\]]*)\])?", field or ""):
        out[m.group(1)] = m.group(2).split() if m.group(2) else None
    return out


def gate_status(ctx, gate, named=None):
    present = sorted(rv for (g, rv) in ctx.reports if g == gate)
    base = named or DEFAULT_REVIEWERS[gate]
    reviewers = base + [r for r in present if r not in base]
    waiting, reasons = None, []
    for rv in reviewers:
        s = stream_status(ctx, gate, rv)
        s["reviewer"] = rv
        if s["status"] == "converged":
            reasons.append(f"{rv}: {s['reason']}")
            continue
        if s["action"] == "next-gate":
            waiting = waiting or s
            continue
        return s
    return waiting or {"status": "converged", "action": "none", "reviewer": None, "reason": "; ".join(reasons) or "no reviewers"}


def analyse(issues_dir, slug, brief=None):
    reports, responses, rulings = load_dir(issues_dir, slug)
    briefs = [Path(brief)] if brief else find_briefs(issues_dir, slug)
    fields, rounds, log = {}, None, []
    warnings = []
    if not briefs:
        warnings.append("no brief with this artifact slug: non-critical, round limit 5")
    for b in briefs:
        f, r, lg = parse_brief(b)
        fields, rounds = f, r if r is not None else rounds
        log += lg
    yes = lambda k: fields.get(k, "no").lower().startswith("y")
    main = yes("main theorem")
    critical = yes("critical") or main
    budget = min(MAX_ROUNDS, rounds) if rounds else MAX_ROUNDS
    root = Path(issues_dir).resolve().parent.parent
    ctx = Ctx(reports, responses, rulings, critical, main, budget, log, root, split_list(fields.get("claims")))
    required = parse_gates(fields.get("gates"))
    if not required:
        required = {"G1": None, "G2": None, **({"G3": None} if critical else {})}
    gates = [g for g in GATE_ORDER if g in required or any(k[0] == g for k in reports)]
    per_gate = {g: gate_status(ctx, g, required.get(g)) for g in gates}
    overall = None
    for g in gates:
        s = per_gate[g]
        if s["status"] != "converged" and s["action"] != "next-gate":
            overall = dict(s, gate=g)
            break
    if overall is None:
        waiting = [g for g in gates if per_gate[g]["status"] != "converged"]
        overall = dict(per_gate[waiting[0]], gate=waiting[0]) if waiting else \
            {"status": "converged", "action": "none", "gate": None, "reviewer": None, "reason": "all gates converged"}
    counts = {"blocking": 0, "major": 0, "minor": 0}
    seen = set()
    for streams in reports.values():
        rep = streams[max(streams)]
        for i in ctx.counted(rep):
            cid = ctx.canonical(i["id"])
            if cid not in seen:
                seen.add(cid)
                counts[i["severity"]] += 1
    return {"artifact": slug, "briefs": [str(b) for b in briefs], "critical": critical, "main": main,
            "budget": budget, "gates": per_gate, "open_issues": counts, "overall": overall,
            "warnings": warnings + ctx.warnings}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("issues_dir")
    ap.add_argument("slug")
    ap.add_argument("--brief")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hashes", action="store_true", help="print the Review log `hashes` cell for the current content and exit")
    a = ap.parse_args(argv)
    if not Path(a.issues_dir).is_dir():
        print(f"review_status: {a.issues_dir} is not a directory", file=sys.stderr)
        return 2
    if a.hashes:
        briefs = [Path(a.brief)] if a.brief else find_briefs(a.issues_dir, a.slug)
        if not briefs:
            print(f"review_status: no brief with artifact slug {a.slug}", file=sys.stderr)
            return 2
        try:
            h = content_hashes(Path(a.issues_dir).resolve().parent.parent, parse_brief(briefs[-1])[0])
        except ValueError as e:
            print(f"review_status: {e}", file=sys.stderr)
            return 2
        print(format_hashes(h))
        return 0
    res = analyse(a.issues_dir, a.slug, a.brief)
    if a.json:
        print(json.dumps(res, indent=2))
        return 0
    print(f"artifact: {a.slug}  critical: {'yes' if res['critical'] else 'no'}  main: {'yes' if res['main'] else 'no'}"
          f"  round limit: {res['budget']}  brief: {', '.join(res['briefs']) or 'none'}")
    for g, s in res["gates"].items():
        who = f" {s['reviewer']}" if s.get("reviewer") else ""
        print(f"{g} {s['status']} -> {s['action']}{who}: {s['reason']}")
    c = res["open_issues"]
    print(f"open issues: blocking {c['blocking']}, major {c['major']}, minor {c['minor']}")
    for w in res["warnings"]:
        print(f"warning: {w}")
    o = res["overall"]
    tail = " ".join(x for x in (o.get("gate"), o.get("reviewer"), o.get("issue")) if x)
    print(f"overall: {o['status']} -> {o['action']}" + (f" {tail}" if tail else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
