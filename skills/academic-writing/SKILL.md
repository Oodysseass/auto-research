---
name: academic-writing
description: Writing style for academic prose and LaTeX (papers, reports, definitions, lemmas, theorems, proofs, remarks, evaluation). Load before drafting, editing or reviewing any such text or any .tex file.
---

# Academic writing

## Precedence

`mechanics.md` governs sentence mechanics (no em dashes, short sentences, noun-phrase headings,
macros, `\Cref`). `paper-architecture.md` governs the architecture of the paper and the shape of
statements and proofs. Where the corpus does something that `mechanics.md` forbids
(parenthetical asides, rhetorical questions, "clearly", a personified adversary),
`mechanics.md` wins.

On terminology, the project's own `.work/glossary.md` always wins over any global glossary.

## Which file to load

Read the files before drafting or editing, not after.

| Task | Load |
|---|---|
| Any academic prose: paper section, abstract, definition, theorem, proof, remark, evaluation, report | [mechanics.md](mechanics.md) |
| Any `.tex` file | [latex.md](latex.md), plus the project's `.work/glossary.md` for macros |
| Model sections, definitions, theorems, proofs, attacks, remarks, contributions, paper structure | [paper-architecture.md](paper-architecture.md) |
| PoW or longest-chain projects | [glossaries/backbone.md](glossaries/backbone.md) |
| Any project | `.work/glossary.md` (terms, macros, notation), if it exists |
