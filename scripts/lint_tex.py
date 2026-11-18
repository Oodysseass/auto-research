#!/usr/bin/env python3
"""Gate G0: mechanical lint for LaTeX. Stdlib only.

Usage:
  lint_tex.py [FILE_OR_DIR ...] [--root DIR] [--glossary FILE] [--artifact STR]
              [--previous REPORT.json] [--out REPORT.json] [--build]

With no paths, lints every .tex file under --root (default: current directory),
skipping output/ and hidden directories. Labels are collected from every .tex file
under --root, so \\Cref targets resolve across files.

Prints an issue report (schemas/issue-report.schema.json) with gate G0 and reviewer
lint-tex. Errors are `major`, warnings `minor`, a failed --build is `blocking`.
--previous reuses the IDs of issues still present (stable IDs, issues/README.md).
Exit code: 0 if the verdict is accept, 1 if revise, 2 on usage errors.

There is deliberately no sentence-length check (see academic-writing mechanics.md).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

GATE, REVIEWER = "G0", "lint-tex"
LABEL_PREFIXES = ("def", "lem", "cor", "thm", "asm", "rem", "alg", "sec", "fig", "line")
BANNED = ["clearly", "obviously", "it is easy to see", "straightforward", "straightforwardly",
          "trivially", "intuitively", "the key insight"]
DEFAULT_NOTES = ["todo", "odysseas"]
TITLE_CMDS = ("section", "subsection", "subsubsection", "paragraph")
TITLE_VERBS = {
    "is", "are", "was", "were", "be", "has", "have", "had", "does", "do", "did", "can", "cannot",
    "could", "must", "will", "would", "should", "may", "might", "holds", "hold", "implies",
    "guarantees", "achieves", "fails", "works", "breaks", "shows", "proves", "makes", "yields",
    "ensures", "matters", "prevents", "leads", "becomes", "needs", "requires", "gives", "wins",
    "loses", "beats", "suffices", "remains",
}
MATH_ENVS = ("equation", "equation*", "align", "align*", "gather", "gather*", "multline",
             "multline*", "eqnarray", "eqnarray*", "math", "displaymath", "flalign", "flalign*")
VERBATIM_ENVS = ("verbatim", "verbatim*", "lstlisting", "minted", "comment")
DEF_CMDS = re.compile(r"\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand|def|"
                      r"DeclareMathOperator|newenvironment|renewenvironment)\b")
# Commands whose first argument is a key, file name or URL, never prose.
KEY_ARG_CMDS = ("label", "Cref", "cref", "ref", "eqref", "autoref", "cite", "citep", "citet",
                "url", "href", "input", "include", "includegraphics", "bibliography",
                "bibliographystyle", "usepackage", "documentclass", "begin", "end")


# ---------- masking: blank out what is not text mode, keep offsets and newlines ----------

def blank(s):
    return "".join(c if c == "\n" else " " for c in s)


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        out.append(line if m is None else line[:m.start()] + " " * (len(line) - m.start()))
    return "\n".join(out)


def mask_regions(text, pattern):
    return re.sub(pattern, lambda m: blank(m.group(0)), text, flags=re.S)


def no_verbatim(raw):
    """Return `raw` with comments and verbatim-like environments blanked."""
    t = strip_comments(raw)
    for env in VERBATIM_ENVS:
        e = re.escape(env)
        t = mask_regions(t, r"\\begin\{" + e + r"\}.*?\\end\{" + e + r"\}")
    return t


def text_mode(raw):
    """Return `raw` with comments, math, verbatim and key arguments blanked."""
    t = no_verbatim(raw)
    for env in MATH_ENVS:
        e = re.escape(env)
        t = mask_regions(t, r"\\begin\{" + e + r"\}.*?\\end\{" + e + r"\}")
    t = mask_regions(t, r"\\\[.*?\\\]")
    t = mask_regions(t, r"\$\$.*?\$\$")
    t = mask_regions(t, r"(?<!\\)\$.*?(?<!\\)\$")
    t = mask_regions(t, r"\\\(.*?\\\)")
    t = mask_regions(t, r"\\(?:" + "|".join(KEY_ARG_CMDS) + r")\*?(?:\[[^\]]*\])?\{[^}]*\}")
    return t


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


# ---------- glossary ----------

def read_glossary(path):
    """Return (raw_forms: {word: macro}, note_macros: [name]) from the Macros table."""
    raw, notes = {}, []
    if path is None or not Path(path).is_file():
        return raw, notes
    in_macros = False
    for line in Path(path).read_text().splitlines():
        if line.startswith("## "):
            in_macros = line.strip().lower() == "## macros"
            continue
        if not in_macros or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() == "macro" or set(cells[0]) <= set("-: "):
            continue
        macro = cells[0].strip("`").strip()
        if macro.startswith("<"):  # template placeholder
            continue
        names = re.findall(r"\\([A-Za-z]+)", macro)
        if not names:
            continue
        if cells[1].lower() == "note":
            notes.append(names[0])
        for form in cells[3].split(","):
            form = form.strip()
            if form and not form.startswith("<"):
                raw[form] = "\\" + names[0]
    return raw, notes


# ---------- checks ----------

class Finding:
    def __init__(self, rule, severity, path, line, snippet, evidence, fix):
        self.rule, self.severity, self.path, self.line = rule, severity, path, line
        self.snippet, self.evidence, self.fix = snippet, evidence, fix


def check_file(path, rel, labels, raw_forms, note_macros):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    nocomment = no_verbatim(raw)
    txt = text_mode(raw)
    found = []

    def add(rule, sev, off, snippet, evidence, fix, src=raw):
        found.append(Finding(rule, sev, rel, line_of(src, off), snippet, evidence, fix))

    for m in re.finditer("\u2014", strip_comments(raw)):
        add("em-dash", "major", m.start(), "\u2014", "Em dash character.", "Rewrite as two sentences, or use a comma, colon or parentheses.")
    for m in re.finditer(r"(?<!-)---(?!-)", txt):
        add("em-dash", "major", m.start(), "---", "Em dash (---) in text mode.", "Rewrite as two sentences, or use a comma, colon or parentheses.")

    for m in re.finditer(r"\\(ref|eqref|cref|autoref|vref)\{([^}]*)\}", nocomment):
        add("ref", "major", m.start(), m.group(0), f"\\{m.group(1)}{{}} used.", f"Use \\Cref{{{m.group(2)}}}.")

    for word in BANNED:
        pat = r"(?<![A-Za-z])" + r"\s+".join(map(re.escape, word.split())) + r"(?![A-Za-z])"
        for m in re.finditer(pat, txt, flags=re.I):
            add("banned-word", "major", m.start(), word, f"Banned phrase \"{word}\".", "Delete it, or give the actual reason the step holds.")

    for m in re.finditer(r"\\(" + "|".join(TITLE_CMDS) + r")\*?(?:\[[^\]]*\])?\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", nocomment):
        title = re.sub(r"\\[A-Za-z]+\*?|[{}$]", " ", m.group(2)).strip()
        words = title.split()
        reasons = []
        if title.endswith((".", "?", "!", ":", ";")):
            reasons.append("ends with punctuation")
        if len(words) > 6:
            reasons.append(f"has {len(words)} words (more than 6)")
        verbs = sorted({w.lower().strip(".,;:?!") for w in words} & TITLE_VERBS)
        if verbs:
            reasons.append("contains the verb " + ", ".join(verbs))
        if reasons:
            add("title", "minor", m.start(), m.group(0), f"\\{m.group(1)}{{{title}}} looks like a sentence: " + "; ".join(reasons) + ".",
                "Use a plain noun phrase.")

    skip_lines = {line_of(nocomment, d.start()) for d in DEF_CMDS.finditer(nocomment)}
    for form, macro in raw_forms.items():
        for m in re.finditer(r"(?<![A-Za-z\\])" + re.escape(form) + r"(?![A-Za-z])", txt):
            if line_of(txt, m.start()) in skip_lines:
                continue
            add("raw-word", "major", m.start(), form, f"Raw \"{form}\" where macro {macro} exists (glossary.md).", f"Use {macro}.")

    for m in re.finditer(r"\\label\{([^}]*)\}", nocomment):
        name = m.group(1)
        if not re.match(r"(" + "|".join(LABEL_PREFIXES) + r")\.[^.]", name):
            add("label-prefix", "major", m.start(), name, f"Label \"{name}\" lacks an allowed prefix.",
                "Rename with one of " + ", ".join(p + "." for p in LABEL_PREFIXES) + " and update its \\Cref calls.")

    for m in re.finditer(r"\\[Cc]ref\*?\{([^}]*)\}", nocomment):
        for target in (t.strip() for t in m.group(1).split(",")):
            if target and target not in labels:
                add("unresolved-ref", "major", m.start(), target, f"\\Cref target \"{target}\" has no \\label in any .tex file.",
                    "Fix the label name or add the label.")

    for name in sorted(set(DEFAULT_NOTES) | set(note_macros)):
        for m in re.finditer(r"\\" + re.escape(name) + r"(?![A-Za-z])\*?\s*(\[[^\]]*\])?\s*\{", nocomment):
            if line_of(nocomment, m.start()) in skip_lines:
                continue
            add("author-note", "minor", m.start(), "\\" + name, f"Author note \\{name}{{}} left in the text.", "Resolve and remove it.")
    return found


def collect_tex(root, paths):
    def walk(d):
        for p in sorted(Path(d).rglob("*.tex")):
            parts = p.relative_to(d).parts
            if any(x.startswith(".") or x == "output" for x in parts[:-1]):
                continue
            yield p
    if not paths:
        return list(walk(root))
    files = []
    for p in map(Path, paths):
        files += list(walk(p)) if p.is_dir() else [p]
    return files


def collect_labels(root):
    labels = set()
    for p in collect_tex(root, []):
        labels.update(re.findall(r"\\label\{([^}]*)\}", strip_comments(p.read_text(encoding="utf-8", errors="replace"))))
    return labels


def build(root):
    try:
        r = subprocess.run(["latexmk", "-synctex=1", "-pdf", "-interaction=nonstopmode", "-outdir=output", "main.tex"],
                           cwd=root, capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        return Finding("build", "blocking", "main.tex", 1, "latexmk", "latexmk is not installed.", "Install TeX Live / latexmk.")
    if r.returncode == 0:
        return None
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-15:])
    return Finding("build", "blocking", "main.tex", 1, "latexmk", "latexmk failed. Last lines:\n" + tail, "Fix the build errors.")


# ---------- report ----------

def issue_key(path, evidence):
    return (path, evidence)


def assign_ids(findings, previous):
    """Reuse the ID of a previous issue with the same file and evidence (in order); number new ones after the max."""
    prev, top = {}, 0
    if previous and Path(previous).is_file():
        for issue in json.loads(Path(previous).read_text()).get("issues", []):
            n = int(issue["id"].rsplit("/", 1)[1])
            top = max(top, n)
            prev.setdefault(issue_key(issue["location"].rsplit(":", 1)[0], issue["evidence"]), []).append(n)
    out = []
    for f in findings:
        ids = prev.get(issue_key(f.path, f"[{f.rule}] {f.evidence}"))
        if ids:
            out.append((ids.pop(0), f))
        else:
            top += 1
            out.append((top, f))
    return out


def head_commit(root):
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True)
        return r.stdout.strip() or "none"
    except FileNotFoundError:
        return "none"


def report(findings, artifact, commit, previous=None):
    issues = []
    for n, f in sorted(assign_ids(findings, previous), key=lambda x: x[0]):
        issues.append({
            "id": f"{GATE}/{REVIEWER}/{n}", "severity": f.severity, "location": f"{f.path}:{f.line}",
            "claim": None, "evidence": f"[{f.rule}] {f.evidence}", "suggested_fix": f.fix,
        })
    bad = any(i["severity"] in ("blocking", "major") for i in issues)
    return {"gate": GATE, "reviewer": REVIEWER, "model": "none", "artifact": artifact,
            "commit": commit, "issues": issues, "verdict": "revise" if bad else "accept"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--root", default=".")
    ap.add_argument("--glossary")
    ap.add_argument("--artifact")
    ap.add_argument("--previous")
    ap.add_argument("--out")
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    glossary = a.glossary or (root / ".work" / "glossary.md")
    raw_forms, notes = read_glossary(glossary)
    labels = collect_labels(root)
    files = collect_tex(root, a.paths)
    if not files:
        print("lint_tex: no .tex files found", file=sys.stderr)
        return 2
    findings = []
    for p in files:
        p = p.resolve()
        rel = str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
        findings += check_file(p, rel, labels, raw_forms, notes)
    if a.build:
        b = build(root)
        if b:
            findings.append(b)
    artifact = a.artifact or ",".join(sorted({f.path for f in findings} or {str(files[0])}))
    rep = report(findings, artifact, head_commit(root), a.previous)
    text = json.dumps(rep, indent=2)
    if a.out:
        Path(a.out).write_text(text + "\n")
    else:
        print(text)
    return 0 if rep["verdict"] == "accept" else 1


if __name__ == "__main__":
    sys.exit(main())
