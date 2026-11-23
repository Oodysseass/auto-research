---
name: workflow-guide
description: Answers the human's questions about how the research workflow works, or what a workflow command (/orch, /intake, /gate, /why, /wstatus, rw, raw:), file, gate, claim status or decision class means, from ~/dotclaude/README.md (usage) and ~/dotclaude/DESIGN.md (design). Read-only. Usage /workflow-guide <question>.
argument-hint: "<question about the workflow>"
disable-model-invocation: true
---

# Workflow guide

Question: `$ARGUMENTS`. If it is empty, ask what the human wants to know.

Answer the human's question about the workflow. Read-only: never edit, commit, dispatch or run workflow scripts.

1. Read `~/dotclaude/README.md` (how to use it) and `~/dotclaude/DESIGN.md` (what it is meant to do, and why) in full.
   They are the sources for every answer: README for "how do I", DESIGN for "why" and "what is built".
2. Answer from it, in plain language, as briefly as the question allows. Name the section you used (e.g. "README, Everything you can type" or "DESIGN.md, section 6").
3. If neither covers the question, say so first. Then, only if it helps, read the one implementation file that defines the thing
   (e.g. `~/dotclaude/skills/<command>/SKILL.md`), and label that part of the answer "from the implementation, not the README or DESIGN.md".
   Mention that the documentation has a gap there.
4. If the README, DESIGN.md and an implementation file you read disagree, report both and say they disagree. Do not pick one.
5. Questions about a specific project item (a claim `C3`, a decision `D2`, an issue) belong to `/why`. Point the human there.
6. Never invent behavior. If neither source says, answer "not recorded".
