#!/usr/bin/env python3
"""Check an approval packet (.work/packets/<stage>.md). Stdlib only.

Usage: check_packet.py <packet.md> [--root R]

Checks: the five sections, in order, each non-empty; every provisional decision card (status provisional in
.work/decisions/) is named; no technical vocabulary (tokens, budgets, model tiers, effort, review round counts,
file formats). Exit 0 if the packet passes, 1 otherwise.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rw_vocab import technical_terms  # noqa: E402
import decisions  # noqa: E402

SECTIONS = ["What was produced", "What changed since the last approval", "Review findings and resolution",
            "What remains uncertain", "What approval unlocks"]


def check(path, root):
    text = Path(path).read_text()
    errs = []
    heads = [m.group(1).strip() for m in re.finditer(r"^## (.+)$", text, re.M)]
    pos = -1
    for s in SECTIONS:
        if s not in heads:
            errs.append(f"missing section `## {s}`")
            continue
        i = heads.index(s)
        if i < pos:
            errs.append(f"section `## {s}` out of order")
        pos = i
        body = re.search(rf"^## {re.escape(s)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S).group(1).strip()
        if not body:
            errs.append(f"section `## {s}` is empty (write `none` if there is nothing)")
    for c in decisions.all_cards(root):
        if c.get("status") == "provisional" and not re.search(rf"\b{c['id']}\b", text):
            errs.append(f"provisional decision {c['id']} is not named")
    for word, what in technical_terms(text):
        errs.append(f"technical term {word!r} ({what})")
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("packet")
    ap.add_argument("--root", default=".")
    a = ap.parse_args(argv)
    errs = check(a.packet, a.root)
    for e in errs:
        print(f"{a.packet}: {e}")
    print("OK" if not errs else f"{len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
