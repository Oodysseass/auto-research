---
name: wstatus
description: Status of a research workflow project (.work/). Playbook stage, recent requests, open issues by severity, claims by status, pending decisions, requeued work, both git repos, new inputs in resources/. Read-only. Named wstatus because /status is a built-in command.
disable-model-invocation: true
---

# Workflow status

Read-only. Never edit or commit.

1. Run `python3 ~/dotclaude/scripts/wstatus.py` from the project root, as one Bash call and nothing else. It prints
   every input below as `## <name>` sections: state, agenda, approvals log, latest handoff, claims, ideas, pending
   captures, decisions, issues, requests, repos, resources. Never compose your own shell pipeline for these (in zsh, a separator such as `echo ====` fails as `=`
   expansion and aborts the chain). A section that ends in `(exit N)` failed: report it as a fault, with its output.
2. Issues: the `issues` section is `review_status.py --all`: one line per artifact slug, one per legacy file
   (`legacy*.json`, issues without a `status` count as open), and the total `open issues:` line. For the per-artifact
   status of a non-converged slug, run `python3 ~/dotclaude/scripts/review_status.py .work/issues <slug>`.
3. Read the latest handoff named in its section only if the state section does not say what is next.
4. Reply as one short block, in plain words (rules card 15: say what each item is; IDs only as a trailing `Refs:`):
   - stage: the current thread `<T-ID> (<stage> <name>)`, active brief, branch, last handoff
   - agenda: the open threads in order, one line each (position, T-ID, title, status, next); `rw` takes the first committed one
   - ideas: open questions first, then open ideas, one line each; pending captures, if any
   - issues: blocking / major / minor open, and per non-converged artifact its status (`open | deadlocked | stalled | max_rounds | converged-provisional`)
   - claims: count per status (`draft checked provisional verified refuted legacy-unverified`)
   - requests: the 5 most recent, one line each (RQ-ID, date, status, title, briefs and cards); open and deferred first
   - decisions: open and provisional cards, one line each (D-ID, class, question); requeued briefs
   - repos: project repo clean or dirty, `.work` repo clean or dirty; workflow files tracked by the project repo: `none`
     (anything else is a fault: say so first); missing exclude lines if any. For a project in a subdirectory of the
     project repo (`project:` line), name the subdirectory: every check covers it only, and changes elsewhere in the repo
     (coauthors' folders, sibling projects) are not reported. Each `also loaded:` line (a `CLAUDE.md` above the project,
     e.g. `reports/CLAUDE.md`) is reported once, as "also loaded", never as an error
   - resources: new files not yet processed (the next session handles them), unwarned edits or deletions, and
     `resources/` files still tracked by the project repo
   - no tokens or budgets: those are never the human's concern
