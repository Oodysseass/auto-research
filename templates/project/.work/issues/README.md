# Issues

One JSON file per review. Schemas: `~/dotclaude/schemas/issue-report.schema.json` and `issue-response.schema.json`.

## File names

- Review: `<artifact-slug>.<gate>.<reviewer>.r<round>.json`, e.g. `safety-lemma.G2.proof-checker.r1.json`.
- Producer response: `<artifact-slug>.<gate>.<reviewer>.r<round>.response.json`.

## Review report

```json
{
  "gate": "G2",
  "reviewer": "proof-checker",
  "model": "claude-opus-5-5",
  "artifact": "paper/04analysis.tex#lem.safety",
  "commit": "abc1234",
  "issues": [
    {
      "id": "G2/proof-checker/1",
      "severity": "blocking",
      "location": "paper/04analysis.tex:120",
      "claim": "C3",
      "evidence": "Quoted passage and the reason it fails.",
      "suggested_fix": "One concrete fix."
    }
  ],
  "verdict": "revise"
}
```

- `severity` is required: `blocking`, `major` or `minor`.
- `claim` is a claim ID or `null`.
- `verdict`: `accept` only if there is no blocking or major issue.

## Stable IDs

Issue IDs are `<gate>/<reviewer>/<n>`. In round k, a reviewer reuses the ID of every issue it raised in round k-1 that is still present,
and numbers new issues after the highest ID used so far. An ID is never reused for a different issue.

## Producer response

```json
{
  "producer": "prover",
  "commit": "def5678",
  "responses": [
    { "issue_id": "G2/proof-checker/1", "status": "fixed", "justification": "Added the genesis case at line 124." }
  ]
}
```

`status`: `fixed`, `rejected` (rebuttal goes to the next round) or `needs_human`.
