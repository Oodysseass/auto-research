"""Text that must never reach the human in a question, decision card or approval packet. Stdlib only.

Questions to the human are about research content, scope and direction. Tokens, budgets, model tiers, effort levels,
review round counts and file formats are decided by the system and logged (technical_terms).
Workflow IDs (C36, R13, A25, D1, DL1, RQ5, T7, I2, S4, issue IDs) and file pointers (BRIEF.md:48, contract.md#N5) are
bookkeeping: text for the human says what each thing is in plain words, and IDs go only in a trailing `Refs:` part of a
line (workflow_refs).
"""
import re

PATTERNS = [
    (r"\btokens?\b", "token"),
    (r"\bbudgets?\b", "budget"),
    (r"\beffort\b", "effort level"),
    (r"\b(opus|sonnet|haiku|mythos|fable|gpt-[\w.-]+)\b", "model name"),
    (r"\btiers?\b", "model tier"),
    (r"\bescalation ladder\b", "routing"),
    (r"\b(review|max(imum)?|extra|more)\s+rounds?\b", "review round count"),
    (r"\bround (limit|budget|count)s?\b", "review round count"),
    (r"\brounds? used\b", "review round count"),
    (r"\bcontext (window|usage)\b", "context usage"),
    (r"\b(json|yaml|tsv|schema)\b", "file format"),
]
_COMPILED = [(re.compile(p, re.I), what) for p, what in PATTERNS]


def technical_terms(text):
    """Return [(matched text, category)] for every technical term in `text`."""
    out = []
    for rx, what in _COMPILED:
        for m in rx.finditer(text or ""):
            out.append((m.group(0), what))
    return out


ID_RX = re.compile(r"\b(?:RQ\d+|DL\d+|[RNPACDTIS]\d+|G[0-5]/[a-z0-9-]+/\d+)\b")
POINTER_RX = re.compile(r"[\w./-]+\.(?:md|tex|pdf|json|py|bib|txt)(?::\d+(?:-\d+)?|#[\w.-]+)")
REFS_RX = re.compile(r"\(?\bRefs?:.*$", re.I | re.M)


def workflow_refs(text):
    """Return [(matched text, kind)] for every workflow ID or file pointer outside a trailing `Refs:` part of a line."""
    body = REFS_RX.sub("", text or "")
    out = [(m.group(0), "file pointer") for m in POINTER_RX.finditer(body)]
    body = POINTER_RX.sub("", body)
    out += [(m.group(0), "workflow ID") for m in ID_RX.finditer(body)]
    return out
