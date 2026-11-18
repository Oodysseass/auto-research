---
name: escalate
description: Rerun the last review of a claim or issue one rung up the model-routing ladder, in a research workflow project (.work/). Usage /escalate <claim-ID | issue-ID>.
argument-hint: "<claim ID, e.g. C3 | issue ID, e.g. G2/proof-checker/2>"
disable-model-invocation: true
---

# Escalate

Target: `$ARGUMENTS`.

1. Load the `model-routing` and `review-gates` skills.
2. Find the latest review in `.work/issues/` that covers the target: the report with that issue ID, or the latest report whose
   artifact or issues name the claim. If none exists, stop and say so.
3. Read its `reviewer` and `model`. Find that rung in the reviewer's ladder in `routing.md`, and take the next rung.
   If it is already the top rung, stop: the next step is the human. Say so.
4. Log the routing in `decisions.md` (format in routing.md, `class: logged`), with reason `human /escalate`. Commit ("plan rerun of review of <artifact>", per `commit-style`).
5. Rerun the review at the new rung: same reviewer role, same slug and gate, round one higher than the latest.
   Dispatch per review-gates, with the write guard. Codex (G3) has no higher rung below `--effort highest`.
6. Commit the report ("review <artifact>, round <n>", per `commit-style`). Reply with the rung used, the verdict, counts by severity and the report path.
   Do not dispatch producers. Claim statuses change only per review-gates.
