#!/usr/bin/env python3
"""Build agents/<base>-mythos.md from agents/<base>.md. Stdlib only.

The variant has the base body unchanged, the base tools, disallowedTools and
skills, `model: claude-mythos-5-2`, `effort: xhigh`, a GENERATED header and a
line fixing the role name to <base>.

Usage:
  build_mythos_variants.py           write all variants
  build_mythos_variants.py --check   exit 1 if any variant is missing or out of date
"""
import re
import sys
from pathlib import Path

AGENTS = Path(__file__).resolve().parent.parent / "agents"
BASES = ["prover", "proof-checker", "counterexample-hunter", "attacker", "protocol-designer", "question-refiner", "arbiter"]
MODEL = "claude-mythos-5-2"
EFFORT = "xhigh"
COPIED = ["tools", "disallowedTools", "skills"]


def split(text, path):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        sys.exit(f"{path}: no frontmatter")
    fields = {}
    for line in m.group(1).splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            sys.exit(f"{path}: unsupported frontmatter line {line!r}")
        fields[key.strip()] = value.strip()
    return fields, m.group(2)


def build(base):
    path = AGENTS / f"{base}.md"
    fields, body = split(path.read_text(), path)
    if fields.get("name") != base:
        sys.exit(f"{path}: name is {fields.get('name')!r}, expected {base!r}")
    lines = [
        "---",
        f"name: {base}-mythos",
        f"description: Mythos 5.2 tier of {base}. {fields['description']}",
        f"model: {MODEL}",
        f"effort: {EFFORT}",
    ]
    lines += [f"{k}: {fields[k]}" for k in COPIED if k in fields]
    lines += [
        "---",
        "",
        f"<!-- GENERATED from {base}.md, do not edit. Rebuild with scripts/build_mythos_variants.py. -->",
        "",
        f"Tier: you are the Mythos 5.2 tier of `{base}`. The role name for issue IDs, file names "
        f"and `reviewer` or `producer` fields is `{base}`, never `{base}-mythos`.",
    ]
    return "\n".join(lines) + "\n" + body


def main(argv):
    check = argv == ["--check"]
    if argv and not check:
        print(__doc__)
        return 1
    stale = []
    for base in BASES:
        out = AGENTS / f"{base}-mythos.md"
        want = build(base)
        if out.exists() and out.read_text() == want:
            continue
        if check:
            stale.append(out.name)
        else:
            out.write_text(want)
            print(f"wrote {out.name}")
    if stale:
        print("Out of date Mythos variants: " + ", ".join(stale))
        print("Run: python3 scripts/build_mythos_variants.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
