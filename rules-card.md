# Rules card

1. No em dashes. Use a comma, a period or a colon.
2. Cross-references use `\Cref{}` only. Never `\ref{}` or `\eqref{}`.
3. Use project macros and `.work/glossary.md` terms. Never a synonym, never raw text where a macro exists.
4. Headings at every level are noun phrases. Never sentences, claims or hooks.
5. Never state a claim stronger than its status in `.work/claims.md`. Unproven means say so.
6. Stay inside `.work/contract.md` scope. Out-of-scope work needs approval.
7. Read the brief, contract, model and glossary before producing anything.
8. Write results to the files the brief names, not only to chat.
9. Ask instead of inventing context.
10. No "clearly", "obviously", "it is easy to see", "straightforward", "trivially".
11. One idea per sentence. Shortest sentence first in a paragraph.
12. Do not change the model or an assumption silently. Every step uses listed assumptions (A-IDs) only.
13. Commit messages follow the `commit-style` skill. Name what changed, never the agent, reviewer or tool. No trailers.
14. Two repos: paper and code commit in the project repo, without workflow terms, only via `repos.py commit` (never `git add -A` or `git commit -a`); `.work/` commits in the `.work` repo. Never push `.work` or a `work/*` branch.
15. Text for the human says what each thing is, in plain words: the section, the lemma or what it states, the assumption in words, what the brief says (quote it). Workflow IDs (C36, R13, A25, D1, RQ5, T7) and file:line pointers go only in a short `Refs:` at the end of the item.
