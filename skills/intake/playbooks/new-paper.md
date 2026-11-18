# Playbook: new-paper

From a research question to a full paper in the venue format of the contract.

## S1 Question
- goal: the research question in one paragraph, with the intended contribution and what counts as a main result.
- agent: orchestrator, from `resources/` and the human.
- output: `contract.md` question; main results marked.
- acceptance: question is specific enough to say what a proof or an attack would settle.
- gates: G5 (contract).

## S2 Literature review
- goal: per-paper notes on the closest work.
- agent: `literature-scout`, one brief per cluster of papers.
- output: `notes/lit/<key>.md` per paper with verbatim quotes and section pointers.
- acceptance: each note has the paper's model, results and the quote that supports each summary sentence.
- gates: G2 (`citation-verifier` on notes against `resources/`).

## S3 Refine question
- goal: the question restated against the literature: what is new, what is known, what is open.
- agent: `question-refiner-mythos`; the orchestrator edits `contract.md` after approval.
- output: proposal `notes/question/<brief-id>.md`; updated `contract.md` question; `decisions.md` entry.
- acceptance: each "known" item cites a note; each "new" item is not in any note.
- gates: G1, G5 (contract change).

## S4 Model
- goal: parties, timing, network, adversary, setup, as A-IDs.
- agent: `modeler`.
- output: `.work/model.md`; model section.
- acceptance: every assumption has an A-ID, a statement and a label.
- gates: G0, G1, G2 (`assumption-auditor`), G5 (model).

## S5 Properties
- goal: definitions and properties as parametrised predicates over executions.
- agent: `property-writer`.
- output: definitions section; `claims.md` entries (type `definition`).
- acceptance: every property used by a planned theorem is defined; uses glossary terms.
- gates: G0, G1, G2 (`assumption-auditor`).

## S6 Design
- goal: the protocol, as pseudocode. Skip if the paper analyses an existing protocol.
- agent: `protocol-designer` (or `-mythos` if marked hard).
- output: `algorithms/*.tex`; protocol section.
- acceptance: one algorithm per file; every line referenced by label.
- gates: G0, G1, G2 (`counterexample-hunter`), G3.

## S7 Theorem statements
- goal: theorem and lemma statements, proof roadmap, typical-execution structure.
- agent: `theorem-writer`.
- output: statements in LaTeX; roadmap note; `claims.md` entries.
- acceptance: every main result is stated; each lemma has a role in the roadmap.
- gates: G0, G1, G2 (`counterexample-hunter` on statements), G5 (statements).

## S8 Proofs
- goal: proofs of every statement.
- agent: `prover` for lemmas, `prover-mythos` for main theorems.
- output: proofs in LaTeX.
- acceptance: each step cites a source; cases closed; boundary cases handled.
- gates: G0, G1, G2 (full), G3 for main theorems.

## S9 Attacks and tightness
- goal: attacks that show assumptions are needed or bounds are tight.
- agent: `attacker`, ladder per routing.md.
- output: attacks section; `claims.md` entries; `.tried.md`.
- acceptance: each tightness claim has an explicit strategy in the model.
- gates: G0, G1, G2 (`assumption-auditor`, `proof-checker`).

## S10 Exposition
- goal: introduction, intuition paragraphs, remarks, contributions, abstract.
- agent: `exposition-writer`.
- output: the named sections.
- acceptance: every contribution maps to a `verified` claim; no claim stronger than its status.
- gates: G0, G1, G4.

## S11 Full review
- goal: the whole paper through every gate at one commit.
- agent: all verifiers per gate; Codex at G3.
- output: issue reports; final `claims.md` statuses.
- acceptance: all gates converged at one commit; every main result `verified`.
- gates: G0, G1, G2, G3, G4, G5 (deliverable).
