"""Technical vocabulary that must never reach the human in a question, decision card or approval packet. Stdlib only.

Questions to the human are about research content, scope and direction. Tokens, budgets, model tiers, effort levels,
review round counts and file formats are decided by the system and logged.
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
