# Brief <id>

File name: `briefs/<id>.md`, with `<id>` = `<stage>-<short-slug>`, e.g. `S4-safety-lemma`.

- stage: <playbook stage>
- status: <open | done | escalated | requeued>
- stage type: <literature | refine | model | properties | statements | design | proof-lemma | proof-main | attacks | exposition | report | review | other>
- assigned agent: <agent name>
- model: <model ID>
- effort: <low | medium | high | xhigh | max>
- artifact slug: <slug used in .work/issues/ file names>
- artifact files: <comma-separated paths of the artifact's files>
- claims: <C-IDs the artifact states or proves | none>
- critical: <yes | no>  (main theorem, design, or final deliverable)
- main theorem: <yes | no>
- gates: <from the playbook stage, e.g. G0, G1, G2[assumption-auditor proof-checker], G3>

## Goal

<One or two sentences. What must exist when this brief is done.>

## Inputs

- <file path>: <why it is needed>

## Output

- <file path>: <format, e.g. LaTeX section, issue JSON, markdown notes>

## Acceptance criteria

Each criterion traces to requirement IDs (R-IDs) or claim IDs (C-IDs).

- [ ] <criterion> (R1, C3)

## Constraints

- Assumptions in force: <A1, A2>
- Style: academic-writing skill; project glossary and macros.
- Out of bounds: <anything this brief must not touch>

## Budget

Automatic. Never shown to the human. `tokens` from `python3 ~/dotclaude/scripts/budgets.py get <stage type>`.
`review_status.py` applies it: one 50% extension when the latest round raised new issues, else the loop counts as stalled.

- rounds: 5
- tokens: <from budgets.py>
- extended: no

## Review log

One row per review round. `hashes`: the output of `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug> --hashes`,
taken after the round's reports are committed. It covers the artifact files, `model.md`, `glossary.md`, and the `claims.md`
entries of the claims above and their dependencies. `commit`: `<project>+<.work>` from `repos.py rev`.
`review_status.py` reads this table: keep the columns.

| round | gate | reviewer | model | commit | verdict | blocking | major | minor | hashes |
|---|---|---|---|---|---|---|---|---|---|
