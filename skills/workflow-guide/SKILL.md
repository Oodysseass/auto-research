---
name: workflow-guide
description: Answers the human's questions about how the research workflow works, or what a workflow command (/orch, /intake, /gate, /why, /wstatus, rw, raw:), file, gate, claim status or decision class means, from ~/dotclaude/DESIGN.md. Load only when the human asks such a question. Never load it on your own to plan or do work. Read-only.
---

# Workflow guide

Answer the human's question about the workflow. Read-only: never edit, commit, dispatch or run workflow scripts.

1. Read `~/dotclaude/DESIGN.md` in full. It is the source for every answer.
2. Answer from it, in plain language, as briefly as the question allows. Name the section you used (e.g. "DESIGN.md, section 6").
3. If DESIGN.md does not cover the question, say so first. Then, only if it helps, read the one implementation file that defines the thing
   (e.g. `~/dotclaude/skills/<command>/SKILL.md`), and label that part of the answer "from the implementation, not DESIGN.md".
   Mention that DESIGN.md has a gap there.
4. If DESIGN.md and an implementation file you read disagree, report both and say they disagree. Do not pick one.
5. Questions about a specific project item (a claim `C3`, a decision `D2`, an issue) belong to `/why`. Point the human there.
6. Never invent behavior. If neither source says, answer "not recorded".
