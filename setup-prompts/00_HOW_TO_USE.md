# Research workflow setup: how to use these prompts

Three prompts, run in this order. Each one is staged and stops for your approval after every stage.

| Prompt | Run where | What it builds |
|---|---|---|
| `01_setup_global.md` | a new empty dir `~/dotclaude` | the global setup: consolidated style files, agents, skills, commands, hooks, templates, lint script |
| `02_domain_knowledge.md` | `~/dotclaude` | the domain knowledge base (adversaries, network models, properties, proof techniques, attacks, taste) from your workspace and papers |
| `03_migrate_project.md` | inside each existing project | non-destructive migration of an existing project into the `.work/` structure |

## Recommended sequence

1. Start Claude Code in `~/dotclaude`, paste `01_setup_global.md`. Approve stage by stage.
2. Same directory, paste `02_domain_knowledge.md`. Expect this to be the longest run. Budget it over several sessions; the prompt is written so a fresh session can resume.
3. Pilot: run `03_migrate_project.md` on one project first (pick the one with the cleanest LaTeX). Fix the setup if something is off. Then migrate the rest one at a time.
4. After a project milestone, run `/retro` so lessons flow back into the knowledge base.

## Daily use after setup

- New project: create the dir, put inputs in `resources/` (SoW, papers, notes), run `/intake`.
- Work: `/orch` starts a fresh orchestrator, which does one stage and writes a handoff. When it says so, start a new session and run `/orch` again.
- `/wstatus` shows the stage, open issues, claims, pending approvals, whether both repos are clean, and new inputs.
- Two repos per project: the project repo (paper, code, shared) and `.work/` (workflow state, local, never pushed).
  The project repo never tracks `.work/`, `CLAUDE.md`, `.claude/`, `resources/` or `output/` (`.git/info/exclude`).
- `resources/` is append-only: drop new inputs there at any time; the next session reads them and asks if they change the contract.
- `/gate <artifact>` runs the review gates on demand.

## Model note

Your current default model is Mythos 5.2 at xhigh. The orchestrator mostly reads state, routes and dispatches, so the setup sets the orchestrator to Opus 5.5 (high) and calls Mythos 5.2 through the routing rules for hard stages. If you prefer Mythos everywhere, change one line in `skills/model-routing/routing.md`.
