# Playbook: client-security-review

Review an existing protocol, spec or code against a SoW. Deliverable: a findings report in the client's format.

## S1 SoW matrix
- goal: every SoW requirement is an R-ID in `contract.md` with a source pointer, mapped to a deliverable.
- agent: orchestrator (intake already drafted it); `conformance-reviewer` checks it.
- output: `.work/contract.md` (Requirements, Scope, Deliverables).
- acceptance: no SoW item without an R-ID; every in-scope item has an R-ID; out-of-scope list explicit.
- gates: G1, G5 (contract).

## S2 Threat model
- goal: parties, trust assumptions, network and timing, adversary power and limits, as A-IDs.
- agent: `modeler`.
- output: `.work/model.md`; threat-model section of the report.
- acceptance: every component in scope appears; every assumption has an A-ID and a source (SoW, spec or human).
- gates: G1, G5 (model).

## S3 Property list
- goal: the security properties the system must satisfy, as predicates over executions.
- agent: `property-writer`.
- output: properties in the report draft; one `claims.md` entry each (type `definition`).
- acceptance: each property traces to an R-ID; parametrised by the A-IDs it needs.
- gates: G1, G2 (`assumption-auditor` only), G5 (statements).

## S4 Attack search per property
- goal: for each property, attacks the model allows, or the strategies tried and why they fail.
- agent: `attacker`, one brief per property. Ladder per routing.md.
- output: attack notes per property; `.tried.md` per attempt.
- acceptance: every property has either a candidate finding or a tried-strategies list at the top rung its severity warrants.
- gates: G1; G2 (`counterexample-hunter` against each "no attack found" property, `assumption-auditor` on each attack).

## S5 Findings
- goal: each confirmed attack as a finding: severity, affected R-ID and property, argument or PoC, recommendation.
- agent: `report-writer` (text); `simulator` only if a brief asks for a numeric check.
- output: findings section; one `claims.md` entry per finding (type `finding`).
- acceptance: every finding has a severity, a reproducible argument or PoC, and a recommendation.
- gates: G1, G2 (`proof-checker` on the argument, `counterexample-hunter` on the fix where one is claimed).

## S6 Report
- goal: the full report in the client's format.
- agent: `report-writer`; `exposition-writer` for the executive summary.
- output: report files named in the contract.
- acceptance: client format; no claim stronger than its status; no out-of-scope content.
- gates: G0, G1, G3, G4.

## S7 Conformance vs SoW
- goal: final check that every in-scope R-ID is covered by the report.
- agent: `conformance-reviewer` on the final report against `contract.md`.
- output: G1 report; R-ID coverage table appended to the brief.
- acceptance: every in-scope R-ID covered or explicitly marked as not covered with a reason.
- gates: G1, G5 (deliverable).
