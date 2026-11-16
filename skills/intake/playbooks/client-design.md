# Playbook: client-design

Design a protocol or mechanism to a SoW. Deliverable: a design report with property arguments or proofs.

## S1 SoW matrix
- goal: every SoW requirement is an R-ID in `contract.md` with a source pointer, mapped to a deliverable.
- agent: orchestrator; `conformance-reviewer` checks it.
- output: `.work/contract.md`.
- acceptance: no SoW item without an R-ID; scope explicit.
- gates: G1, G5 (contract).

## S2 Requirements
- goal: model (A-IDs) and target properties (predicates) derived from the R-IDs.
- agent: `modeler`, then `property-writer`.
- output: `.work/model.md`; properties section; `claims.md` entries (type `definition`).
- acceptance: each property traces to an R-ID; each assumption has an A-ID and a source.
- gates: G1, G2 (`assumption-auditor`), G5 (model, statements).

## S3 Design
- goal: a protocol meeting the properties under the model, as pseudocode.
- agent: `protocol-designer`; `protocol-designer-mythos` if the brief marks the design as hard.
- output: one algorithm per file in `algorithms/`; design rationale section.
- acceptance: every property has a mechanism that targets it; uses only A-IDs.
- gates: G0, G1, G2 (`counterexample-hunter`), G3.

## S4 Property arguments or proofs
- goal: for each property, an argument or proof that the design satisfies it. The contract says which need proofs.
- agent: `theorem-writer` (statements), then `prover`.
- output: statements and proofs; `claims.md` entries.
- acceptance: each property is covered; each step cites A-IDs, C-IDs or protocol lines.
- gates: G5 (statements, before proving), G0, G1, G2, G3 for main results.

## S5 Attack pass
- goal: attacks against the final design, beyond the G2 counterexample search.
- agent: `attacker`, ladder per routing.md up to `attacker-mythos`.
- output: attack notes; `.tried.md`; design changes go back to S3 as a new brief.
- acceptance: each property attacked at the top rung its importance warrants; results recorded.
- gates: G1, G2 (`assumption-auditor` on each attack).

## S6 Report
- goal: the design report in the client's format.
- agent: `report-writer`; `exposition-writer` for the summary.
- output: report files named in the contract.
- acceptance: client format; every in-scope R-ID covered; no claim stronger than its status.
- gates: G0, G1, G3, G4, G5 (deliverable).
