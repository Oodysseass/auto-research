# Project: <name>

- type: <project type>
- playbook: <playbook name>
- inputs: `resources/` (read fully before producing anything)
- intent: `resources/BRIEF.md` (project brief) is authoritative. The SoW governs scope; the project brief governs approach.

## Workflow state

All state lives in `.work/`, its own local git repo. The project repo never tracks `.work/`, this file, `.claude/`,
`resources/` or `output/` (`.git/info/exclude`). Paper and code commit in the project repo, without workflow terms, through
`python3 ~/dotclaude/scripts/repos.py commit`, which stages only this project's directory; `.work/` commits in the `.work` repo. Neither `.work` nor a `work/*` branch is ever pushed. Read these before any work:

- `.work/contract.md`: scope, requirements (R-IDs), deliverables. Binding.
- `.work/model.md`: model and assumptions (A-IDs). Binding.
- `.work/glossary.md`: terms, macros, notation. Wins over global glossaries.
- `.work/claims.md`: claim registry. Never state a claim stronger than its status.
- `.work/threads.md`: the agenda, in priority order. `rw` works on the first `committed` thread.
- `.work/state.md`: current thread, next actions, pending decisions, requeued briefs.
- `.work/ideas.md`, `.work/sessions/`: ideas, open questions and session summaries kept from discussions.
- `.work/approvals.md`: the class of every question to me (blocking, checkpoint, logged).
- `.work/decisions/`: one card per question to me. `.work/packets/`: approval packets.
- `.work/briefs/`, `.work/issues/`, `.work/handoffs/`, `.work/decisions.md`, `.work/deadends.md`.
- `.work/resources.manifest`: every file seen in `resources/`, which is append-only. New files are processed at session start.

Run `rw` from the project root (the directory that contains `.work/`). It loops: one orchestrator session per agenda thread, each with
fresh context, asking me inside the session and notifying me when my input is needed. `/why <ID>` explains any claim,
assumption, decision, issue, request, thread or idea. `/agenda` shows the agenda and changes it.

## Working mode

A plain `claude` session here is a research conversation with the project's context (`converse` skill). Discussion changes
no paper, claim, contract, model or agenda file. Work is committed when I ask for it ("write it up", "prove it",
"restructure", "drop X", "make Y first") or accept the session's offer; then the `request` skill records it in
`resources/BRIEF.md`, checks it against the contract, model and claims, does it with proportional gates, reports a short
packet, commits in both repos and waits. A `quick:` or `full:` prefix commits a prompt at once and sets the gate depth.
`raw:` answers outside the harness; `/` is a command. At natural breaks the session offers a capture dialog: only what I
tick is kept (`capture` skill). Registry: `.work/requests.md`.

## Build

<e.g. `latexmk -synctex=1 -pdf -outdir=output main.tex` in `paper/`>

## Project-specific rules

- <rule | none>
