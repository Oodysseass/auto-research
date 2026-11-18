# Brief S4-model

- stage: S4 Model
- status: open
- assigned agent: modeler
- model: claude-opus-5-5
- effort: high
- artifact slug: model
- artifact files: .work/model.md, paper/lemmas.tex, paper/main.tex, paper/macros.tex
- claims: C1, C2, C3, C4, C5
- critical: no
- main theorem: no
- gates: G0, G1, G2[assumption-auditor], G5

## Goal

`.work/model.md` states the model of `resources/notes.md`, section "Model", without changes, as numbered assumptions A1, A2, ...
`paper/lemmas.tex` contains the matching model section, and `paper/main.tex` is the `llncs` wrapper that inputs it.

## Inputs

- resources/notes.md: section "Model" (lines 3-36) is the only source of the model. Section "Statements" is context only.
- resources/BRIEF.md: intent; the model is fixed (lines 22-24).
- .work/contract.md: R3, R7, G1 checks P1, P2, N1 to N5, scope.
- .work/glossary.md: terms (binding), and the empty Macros table to fill.
- .work/model.md: the template to fill.

## Output

- .work/model.md: every section of the template filled; `status: draft`; one Assumptions row per assumption, each with a LaTeX label `asm.<name>`.
- paper/lemmas.tex: one section "Model" (noun-phrase heading, label `sec.model`). Each assumption is a labelled `asm.` environment or item whose label matches its `model.md` row. Project macros for G, len, C_P^r, m_r, M_r and any other repeated notation, defined in `paper/main.tex` preamble or a `paper/macros.tex` input.
- paper/main.tex: `llncs` wrapper (`\documentclass{llncs}`, `cleveref`, the macros, `\input{lemmas}`). It must build with `latexmk -synctex=1 -pdf -outdir=output main.tex` in `paper/`.
- .work/glossary.md: Macros table filled with every macro defined (columns unchanged), and the "Notation conventions" updated if needed. Terms table unchanged in meaning.

## Acceptance criteria

- [ ] Every statement in `resources/notes.md` lines 5-36 maps to at least one A-ID or notation entry, and every A-ID cites the `resources/notes.md` line(s) it comes from in `model.md`. (R3)
- [ ] No A-ID adds, removes, strengthens or weakens anything relative to `resources/notes.md`. Where the notes are silent or ambiguous (for example, which chains the adversary "knows", or whether an honest party receives its own broadcast), the point is listed under a heading "Open points" in `model.md`, quoting the source line, and is not resolved by the modeler. (R3, N2)
- [ ] The network assumptions are stated separately and precisely enough that a later proof can cite exactly the A-IDs it uses for "every honest party sees every honest chain within one round", and no A-ID states that property unless the notes do. (P2, R3)
- [ ] `model.md` and the model section in `paper/lemmas.tex` agree one to one: same A-IDs, same content, same labels. (R3)
- [ ] The honest round procedure (receive, adopt, mine, broadcast) is given in its source order, with the tie rule. Pointer to it in "Protocol". (R3, N2)
- [ ] `paper/main.tex` uses `llncs` and builds; `paper/lemmas.tex` builds under it. (R7)
- [ ] No lemma statement, proof, introduction, exposition, literature or probabilistic content in `paper/lemmas.tex`. Lemma 1 and Lemma 2 are not stated in this stage. (R4, N1, N3, N5)

## Constraints

- Assumptions in force: none yet; this brief creates them.
- Style: academic-writing skill; rules card; project glossary and macros; `\Cref{}` only; no em dashes.
- Out of bounds: `resources/`, `.work/contract.md`, `.work/claims.md`, `.work/approvals.md`, `.work/state.md`. Do not state or prove any lemma. Do not change the model.
- Filling the template `.work/model.md` and the empty Macros table of `.work/glossary.md` is this stage's approved output (state.md, S4) and is not an overwrite needing approval. Do not overwrite any other existing file.

## Budget

- rounds: 5
- tokens: 300k
Overrun means stop and escalate to me.

## Revision r2

Respond to the round-1 reports, then revise. Answer canonical issues only (`duplicate_of` set means answered by its canonical issue).
- `.work/issues/model.G1.conformance-reviewer.r1.json`: G1/conformance-reviewer/1, G1/conformance-reviewer/2
- `.work/issues/model.G2.assumption-auditor.r1.json`: G2/assumption-auditor/3 (issues 1 and 2 are duplicates of the G1 issues)

Write one response file per report: `.work/issues/model.G1.conformance-reviewer.r1.response.json` and
`.work/issues/model.G2.assumption-auditor.r1.response.json` (schema `~/dotclaude/schemas/issue-response.schema.json`).
An issue whose fix lies outside your bounds (Constraints) or needs a decision about the model gets `needs_human`, with the question in `justification`.

## Review log

One row per review round. `hashes`: the output of `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug> --hashes`,
taken after the round's reports are committed. It covers the artifact files, `model.md`, `glossary.md`, and the `claims.md`
entries of the claims above and their dependencies. `review_status.py` reads this table: keep the columns.

| round | gate | reviewer | model | commit | verdict | blocking | major | minor | hashes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | G0 | lint-tex | none | 1a2b568 | accept | 0 | 0 | 0 | .work/model.md=1800531a944b; paper/lemmas.tex=7e46a707b2a1; paper/main.tex=fa5c84ed5f96; paper/macros.tex=6375a7245364; .work/glossary.md=ae9cdf714afa |
| 1 | G1 | conformance-reviewer | claude-opus-5-5 | 39f4d3b | accept | 0 | 0 | 2 | .work/model.md=1800531a944b; paper/lemmas.tex=7e46a707b2a1; paper/main.tex=fa5c84ed5f96; paper/macros.tex=6375a7245364; .work/glossary.md=ae9cdf714afa |
| 1 | G2 | assumption-auditor | claude-opus-5-5 | a67d968 | revise | 0 | 1 | 2 | .work/model.md=1800531a944b; paper/lemmas.tex=7e46a707b2a1; paper/main.tex=fa5c84ed5f96; paper/macros.tex=6375a7245364; .work/glossary.md=ae9cdf714afa |

## Result

Files written or changed:
- `.work/model.md`: template filled, `status: draft`. Sections Parties, Timing and network, Adversary, Oracle or setup, Protocol, Notation, Assumptions (A1 to A13), plus two added sections: "Source map" (every content line of `notes:5-36` to an A-ID or notation entry) and "Open points" (OP1 to OP7).
- `paper/lemmas.tex` (new): `\section{Model}` (`sec.model`), 13 `assumption` environments with labels matching `model.md` one to one and in the same order; notation entries as unlabelled plain text.
- `paper/macros.tex` (new, allowed by the brief): `assumption` environment (`\spnewtheorem`, with `\crefname`), `\genesis`, `\len`, `\chainat`, `\minlen`, `\maxlen`.
- `paper/main.tex` (new): `\documentclass[runningheads]{llncs}`, amsmath, amssymb, etoolbox, cleveref, `\input{macros}`, `\input{lemmas}`.
- `.work/glossary.md`: Macros table filled (6 rows, columns unchanged); "Notation conventions" extended. Terms table untouched.

A-IDs: added A1 to A13 (asm.static-corruption, asm.corruption-bounds, asm.rounds, asm.genesis, asm.valid-chains, asm.honest-round, asm.honest-mining, asm.corrupted-mining, asm.success-patterns, asm.honest-delivery, asm.no-drop, asm.adversarial-delivery, asm.rushing). Changed: none. Removed: none. No claim uses any A-ID yet.

Claims proposed or touched: none. The model section contains prose definitions taken verbatim from the notes (chain and length `notes:14`, successful round `notes:26`, C_P^r `notes:35`, m_r and M_r `notes:36`) and the glossary meaning of honest and corrupted party. They are recorded as notation entries in `model.md` and are not in `definition` environments. Orchestrator to decide whether they need claim entries or are covered by the approval of `model.md`.

Acceptance criteria:
- [x] R3 source mapping: `model.md` "Source map"; each Assumptions row ends with `[notes:N]`.
- [x] No change to the notes; ambiguities listed, quoted and unresolved: `model.md` "Open points" OP1 to OP7 (adversary knowledge, own broadcast, ties among received chains, result of a corrupted success, forging and validity, within-round order across parties, current chain vs held chain).
- [x] Network assumptions separate: A10 to A13; `model.md` "Timing and network" states that no A-ID gives "every honest party sees every honest chain within one round" and that step 4 of A6 fixes when an honest party broadcasts.
- [x] One-to-one agreement: same 13 labels in the same order (checked by script); statements worded identically up to macros.
- [x] Honest round procedure in source order with tie rule: A6, `asm.honest-round`; pointer in `model.md` "Protocol".
- [x] Builds: `latexmk -synctex=1 -pdf -outdir=output main.tex` in `paper/` exits 0, no undefined references. G0 lint (`lint_tex.py --root paper --build`) verdict accept, 0 issues.
- [x] No lemma, proof, introduction, exposition, literature or probabilistic content in `paper/lemmas.tex`.

Open questions and notes for the orchestrator:
- OP1 to OP7 need a human decision before any proof relies on them. OP4 and OP5 matter most for Lemma 1 and Lemma 2 (what adversarial chains can exist). OP4: the glossary term "mining attempt" says a corrupted success extends the chosen chain by one block; the notes do not say this. I did not edit the Terms table (out of my bounds); the human may want it aligned with whatever OP4 decides.
- The LaTeX section follows the order of the notes (parties, rounds, chains, honest procedure, mining, network, notation), not the parties, timing, adversary, protocol order of `paper-architecture.md`, to keep the source order visible.
- `model.md` needs human approval (approvals.md) before S7.

## Result (revision r2)

Files written or changed:
- `.work/model.md`: "Oracle or setup" replaced by "The notes state no setup beyond the genesis chain (A4). Whether a mining attempt succeeds is part of the execution (A9)." "Notation" now gives a `def.` label for each entry and states that the entries add no assumption. OP4 now says the corrupted case of the glossary row "mining attempt" is not an assumption and may not be cited until OP4 is decided.
- `paper/lemmas.tex`: the five notation entries are `definition` environments with labels `def.honest-corrupted`, `def.chain-length`, `def.successful-round`, `def.chain-at`, `def.min-max-len`. Wording unchanged. Assumption environments unchanged.
- `.work/glossary.md`: "Notation conventions" gained two lines ("Open term" for OP4, "Definitions" listing the `def.` labels). Terms and Macros tables unchanged.
- `.work/issues/model.G1.conformance-reviewer.r1.response.json`, `.work/issues/model.G2.assumption-auditor.r1.response.json` (both validate).

A-IDs: added none, changed none, removed none. A1 to A13 are unchanged in text and label. No claim uses any A-ID yet.

Claims proposed (new, type `definition`, status `draft`, assumptions none, verified_by none):
- new: `def.honest-corrupted`: the corrupted parties are the parties in the set of A1; the other parties are honest. Depends on: none. Refers to A1.
- new: `def.chain-length`: a chain is a sequence of blocks that starts with G; len(C) is the number of blocks of C after G, so len(G) = 0. Depends on: none.
- new: `def.successful-round`: round r is successful if at least one honest mining attempt succeeds in round r. Depends on: `def.honest-corrupted`.
- new: `def.chain-at`: C_P^r is the chain of honest party P at the end of round r; C_P^0 = G. Depends on: `def.honest-corrupted`, `def.chain-length`.
- new: `def.min-max-len`: m_r and M_r are the minimum and maximum of len(C_P^r) over all honest P; m_0 = M_0 = 0. Depends on: `def.chain-at`, `def.chain-length`.

Issue responses:
- G1/conformance-reviewer/1: fixed (model.md "Oracle or setup").
- G1/conformance-reviewer/2: needs_human. The human must decide OP4 and then align the glossary row "mining attempt" and record it in approvals.md. Both edits are outside my bounds. I added a mitigation within bounds (model.md OP4, glossary "Notation conventions").
- G2/assumption-auditor/3: fixed (definitions with `def.` labels; claims proposed above).

Acceptance criteria: all r1 pointers still hold. One-to-one agreement holds: same 13 `asm.` labels in the same order, and the 5 `def.` labels match the model.md "Notation" entries. Build: `latexmk` in `paper/` exits 0. G0 lint (`lint_tex.py --root paper --build`): accept, 0 issues. Llncs numbers definitions on their own counter, so Assumption k is still Ak.

Open: OP1 to OP7 still need a human decision, OP4 first because of the glossary conflict.
