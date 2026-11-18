---
name: why
description: Explain any claim (C3), assumption (A2), decision (D4), review issue (G2/proof-checker/1) or request (RQ2), or trace a file or commit back to its request, of a research workflow project (.work/) in depth, from the files only. Read-only. Usage /why <ID>.
argument-hint: "<C-ID | A-ID | D-ID | RQ-ID | issue ID | file path | commit, e.g. C3, D2, RQ4, G2/proof-checker/1>"
---

# Why

Target: `$ARGUMENTS`. Read-only: never edit, commit or dispatch. Answer from files only; if a file does not say, say "not recorded".

1. Identify the kind: `C<n>` claim, `A<n>` assumption, `D<n>` decision, `<gate>/<reviewer>/<n>` issue, `OP<n>` open point in `model.md`, `RQ<n>` request, a file path, a commit hash.
2. Gather:
   - Claim: its `claims.md` entry; the statement in the paper at its label; its proof if any; `depends_on` (both directions:
     what it uses, and every claim that uses it); its assumptions with their `model.md` rows; every issue whose `claim` is it
     (`grep -l '"claim": "C<n>"' .work/issues/*.json`), with responses and rulings; decision cards whose `depends` name it;
     the `decisions.md` entries that mention it; why its status is what it is (`verified_by`, `refuted_by`, `provisional_on`).
   - Assumption: its `model.md` row and the source line in `resources/`; claims that use it; decisions that name it.
   - Decision: the card in `.work/decisions/`, every option with its consequence, the evidence pointers (open each), the dependent
     claims (`python3 ~/dotclaude/scripts/decisions.py list`, and the card's `depends`), and what reversing it would requeue.
   - Request: `python3 ~/dotclaude/scripts/request.py show RQ<n>` (registry block and the verbatim text); its files in
     `resources/`; its briefs, cards, claims, gates, review reports, commits and changed files; its `decisions.md` entry.
   - File path or commit: `python3 ~/dotclaude/scripts/request.py trace <path | hash>` names the requests that changed it;
     then explain each as a request. If none: `repos.py log`, the briefs that name the file, "not from a request".
   - Issue: every round of the report that has it, the producer responses, the rulings, the brief, the cited text in the artifact now.
   For every claim, decision and brief, also run `request.py trace <ID>`: if a request caused it, say which (RQ-ID, date, title).
3. Reply in this order: what it is (one or two sentences); why it stands as it does (the chain of evidence, with file:line or
   file#label pointers); what depends on it; what is still uncertain. Research content only: no tokens, budgets, tiers or round counts.
4. If this was asked from inside a dialog ("Other: why D3"), end by repeating the pending question so the orchestrator can ask again.
