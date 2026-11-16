# Playbook: open-ended

Explore a direction without a fixed deliverable. Time-boxed rounds, each ending in a decision.

## S1 Hypothesis log
- goal: the hypotheses to explore, each with what would confirm or kill it.
- agent: orchestrator, with the human.
- output: `.work/hypotheses.md`: H-IDs, statement, kill criterion, time box (sessions or tokens).
- acceptance: every hypothesis has a kill criterion and a time box.
- gates: G5 (contract).

## S2 Exploration round (repeat)
- goal: one round on one hypothesis, inside its time box.
- agent: chosen per round from routing.md (`literature-scout`, `attacker`, `prover`, `simulator`, ...).
- output: round note `notes/rounds/<H-ID>-r<n>.md`.
- acceptance: the round ends in exactly one of:
  - promote: a new contract for a project of another type. Needs human approval.
  - park: reason and what would reopen it, in the hypothesis log.
  - kill: one line in `deadends.md` with the reason.
- gates: G1 on the round note; G2 (`counterexample-hunter`) on any claim the round promotes; G5 (promote).

A round never runs past its time box. On overrun, the orchestrator parks the hypothesis and asks the human.
