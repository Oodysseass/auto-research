---
name: retro
description: After a milestone of a research workflow project (.work/), propose additions to the domain skill, the playbooks or the rules card, based on issues found and dead ends. Proposals only; the human approves each one.
disable-model-invocation: true
---

# Retro

Proposals only. Nothing in `~/dotclaude` changes without the human's approval of that specific proposal.

1. Read `.work/issues/` (all reports, responses and rulings), `.work/deadends.md`, `.work/decisions.md` and the handoffs since the last retro
   (the last `retro` entry in `decisions.md`, or the start).
2. Find patterns: issue types raised more than once, rebuttals the reviewer kept, deadlocks, escalations, dead ends that recur across briefs.
3. Write `.work/retro/<YYYY-MM-DD>.md`, one numbered proposal per pattern:
   - target file: `~/dotclaude/skills/domain/<file>`, `~/dotclaude/skills/intake/playbooks/<playbook>.md` or `~/dotclaude/rules-card.md`;
   - the exact text to add or change, as a diff;
   - evidence: the issue IDs or dead-end lines it comes from.
   The rules card has a hard budget of 15 lines. A rules-card proposal over budget must say which line it replaces.
   Domain knowledge stays general: no client names, no confidential details.
4. Ask the human with AskUserQuestion, one question per proposal (at most 4 per call): approve or refuse. Apply only the approved ones in `~/dotclaude`,
   then run `python3 ~/dotclaude/scripts/build_mythos_variants.py` if an agent file changed, and commit there per the `commit-style` skill.
5. Append to the project's `decisions.md`: `retro`, the proposals approved and refused. Commit.
