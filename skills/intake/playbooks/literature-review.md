# Playbook: literature-review

Survey work on a topic and end with a sharper question.

## S1 Search
- goal: a list of candidate papers with one line each on relevance.
- agent: `literature-scout`.
- output: `notes/lit/index.md`.
- acceptance: search terms and sources listed; inclusion rule stated; each entry has a bibkey.
- gates: G1.

## S2 Per-paper notes
- goal: one note per included paper.
- agent: `literature-scout`, one brief per batch.
- output: `notes/lit/<key>.md` with model, results, techniques, verbatim quotes and section pointers.
- acceptance: every summary sentence is backed by a quote with a section pointer.
- gates: G1.

## S3 Citation verification
- goal: every quote and every attributed result matches its source in `resources/`.
- agent: `citation-verifier`.
- output: G2 reports.
- acceptance: no unchecked citation left without a flag.
- gates: G2 (`citation-verifier`).

## S4 Synthesis
- goal: a comparison of models, results and techniques, and the open problems.
- agent: `exposition-writer`.
- output: synthesis document named in the contract.
- acceptance: each comparison cell cites a note; open problems are stated as precise questions.
- gates: G0 for LaTeX, G1, G4.

## S5 Question refinement
- goal: one or more research questions with what is known and what is open.
- agent: `question-refiner-mythos`.
- output: proposal `notes/question/<brief-id>.md`; proposed contract for a follow-up project.
- acceptance: each question cites the notes that make it open.
- gates: G1, G5 (deliverable).
