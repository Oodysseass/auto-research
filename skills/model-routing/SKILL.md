---
name: model-routing
description: Model and effort routing for the research workflow. Which agent, model tier and effort to dispatch for a task, the escalation ladder per agent, and budget rules. Load in the orchestrator before writing a brief or dispatching any agent.
---

# Model routing

Read [routing.md](routing.md) before writing a brief or dispatching an agent.
It is the only source of truth for tiers, per-agent ladders and budgets. Agent files carry the default tier; routing.md says when to leave it.

The orchestrator is the only dispatcher. Agents never spawn agents.
