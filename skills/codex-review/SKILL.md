---
name: codex-review
description: Gate G3 cross-model review with the OpenAI Codex CLI (ChatGPT subscription, read-only sandbox). Runs codex_review.sh, which writes a validated issue report to .work/issues/ and aborts if Codex changed any file. Load in the orchestrator when G3 is due (main theorems, designs, final deliverables).
---

# Codex review (G3)

Run from the project root. The orchestrator runs it; agents never do.

```
${CLAUDE_SKILL_DIR}/codex_review.sh --artifact <path[#label]> --slug <slug> --round <n> --brief <.work/briefs/<id>.md> \
    [--claims C1,C3] [--model <codex model>] [--effort <level>]
```

Defaults: model `$CODEX_REVIEW_MODEL` or `gpt-6.1-sol`; effort `$CODEX_REVIEW_EFFORT` or `high`. Log non-default choices per routing.md.

## What the script does

1. Refuses to run unless the contract allows Codex: `ai_tools_allowed` in `.work/contract.md` must list `codex`.
   A contract without that line uses the default (`claude, codex`).
2. Refuses to run unless the tree is clean (write guard, before dispatch) and Codex is signed in with ChatGPT.
3. Unsets `OPENAI_API_KEY` and `CODEX_API_KEY` in its subprocess. Subscription only.
4. Fills [prompt.md](prompt.md) and runs `codex exec` in the project root with `--sandbox read-only`, `--ephemeral`,
   `--output-schema` ([codex-output.schema.json](codex-output.schema.json)) and `--output-last-message`.
5. Builds the full report (gate `G3`, reviewer `codex`, model, artifact, commit) and validates it against
   `~/dotclaude/schemas/issue-report.schema.json`, plus: IDs `G3/codex/<n>`, no `duplicate_of`, verdict consistent with severities.
   On invalid output it re-asks once with the errors. A second failure exits 4 and writes nothing.
6. Checks `git status` before writing the report. If Codex changed anything, it reverts per
   [write-guard.md](../review-gates/write-guard.md), prints a loud error and exits 3. The review is discarded.
7. Writes `.work/issues/<slug>.G3.codex.r<round>.json`. It never overwrites an existing report.

Exit codes: 0 written; 2 refused (contract, dirty tree, auth, arguments); 3 Codex wrote files; 4 invalid output twice; 5 `codex exec` failed.

## After the script

- Exit 0: commit the report, then treat it like any other review (review-gates skill). Codex IDs are stable across rounds:
  the script passes the previous round's report to Codex.
- Exit 3: log "reviewer write violation" in `decisions.md` (write-guard step 4.5). A second violation on the same artifact is a deadlock.
- Exit 4 or 5: log it and escalate to the human. Do not substitute a Claude reviewer for G3.
