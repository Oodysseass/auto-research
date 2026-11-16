# Brief <id>

File name: `briefs/<id>.md`, with `<id>` = `<stage>-<short-slug>`, e.g. `S4-safety-lemma`.

- stage: <playbook stage>
- status: <open | done | escalated>
- assigned agent: <agent name>
- model: <model ID>
- effort: <low | medium | high | xhigh | max>

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

- rounds: <max review rounds, at most 5>
- tokens: <rough size, e.g. 200k>
Overrun means stop and escalate to me.
