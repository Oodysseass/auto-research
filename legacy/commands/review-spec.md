Spawn a sub-agent with NO prior context from this conversation. Its job is an
adversarial fidelity review of the simplified spec against the real pseudocode.
Tell it explicitly: be critical, not affirming. It should hunt for problems, not
validate the work. No praise, no summary of what is correct.

Target: $ARGUMENTS
(a `paper/` section or file; if empty, review all of `paper/consensus.md`.)

The sub-agent must:

1. Read the target `paper/` section and the corresponding `pseudocode/` file(s).
2. Find every place the spec diverges from, omits, or misstates the pseudocode.
3. Classify each finding as **core agreement logic** or
   **optimization/infrastructure**. Report core-logic issues in full; list
   optimization/infrastructure gaps separately and briefly — those are dropped on
   purpose (see the DROP list in CLAUDE.md), so they only matter if one leaked into
   the prose or pseudocode where it shouldn't be.
4. Flag any claim in the spec not supported by the pseudocode (possible
   hallucination), and any silent drop that is missing its "Dropped vs. real impl"
   note.
5. Confirm that everything on CLAUDE.md's DROP list is absent from the prose and
   pseudocode, and appears only as a flowchart reference where allowed
   (wrong-ledger).

Output: a numbered list of issues, each with a `file:section` (or `file::symbol`)
reference and a one-line description, ordered most to least serious.
