# FC Writing Style: proofs and text for blockchain security papers

Scope. This file records how strong papers in crypto-style blockchain security write model
sections, definitions, theorem statements, proofs, attacks and remarks. It was distilled from
36 papers: FC 2021 to 2025 consensus papers, the papers of Dionysis Zindros and coauthors, and
the longest-chain analysis line from the Bitcoin Backbone onward (list in Section 15). Every
rule below is backed by a quote from one of them.

Precedence: see `SKILL.md`. Mechanics (`mechanics.md`) wins over this file where they conflict.

---

## 1. Paper architecture

The successful papers share one skeleton. Use it unless the venue forces otherwise.

1. Introduction with a "results" paragraph that states the main claim as a characterization or
   a concrete quantity, then a numbered contributions list. "The main contribution of this
   paper is a full characterization of the achievable security in all such scenarios."
   (Adversary Majority, FC 2025)
2. Model: parties, rounds and network, adversary and its limits, oracle, protocol, then the
   notation paragraph and the random variables.
3. One theorem that pays for all randomness ("typical execution"), then deterministic lemmas.
4. Analysis: counting lemmas, main theorem, corollaries in the form the user needs.
5. Tightness: a named attack, stated as a definition with numbered steps, and a theorem.
6. Remarks: scope caveats, admitted looseness, open questions.

Body theorems may be informal if the rigorous version is deferred, but say so: "We state our
security theorems informally in this section. For the rigorous theorem statements and proofs,
see Appendix G." (Light Clients for Lazy Blockchains, FC 2024). In an LNCS paper with a page
limit, proofs go to an appendix before content is cut.

## 2. Model section

**Order.** Parties, then timing, then adversary powers and limits, then protocol. "We first
discuss these three aspects, and then the adversary's powers and limits." (Goldfish, FC 2024)

**Reuse, do not restate.** Import a standard model by citation and summarize only what the
proofs use. "Our modeling of the protocol and its execution environment adopts and extends the
model from [GKR20, GRR22] ... We summarize the model here for completeness." (Gaži, Ren,
Russell, CRYPTO 2023). Point to an appendix for the rest: "Other standard aspects: App. B."
(Adversary Majority)

**Tie vocabulary to pseudocode.** When two words could be confused, fix them against the
protocol's variables, in a footnote if needed. "we say a party 'has' a chain C* at round r, if
the value of variable C at line 7 of Algorithm 4 is C*, while it 'adopts' a chain C* if the
value of variable C̃ is equal to C*" (Bitcoin Backbone, fn. 16)

**Convention sentences.** Every phrase that could be read two ways gets one sentence fixing its
meaning, before first use. "Throughout this paper, 'by time t' means 'during (0, t]'" (Li,
Guo, Ren, AFT 2021). Typical candidates: "computed at round r", "by round r", "at the
beginning of round r", "in a round of S".

**Justify modelling choices once, in the direction that strengthens the result.** "As our main
result is a lower bound, this only makes our result stronger." (PoSpace (In)security, FC 2025)

## 3. Notation

Front-load indexing in one short paragraph, before any definition, and attribute the
convention. "For chain addressing we use Python brackets C[.] as in [22]" (NIPoPoW, FC 2020).
"C[i] indicates the ith block, starting from C[0], the genesis block. C[-i] indicates the ith
block from the end, with C[-1] being the tip" (Proof-of-Stake Sidechains, S&P 2019). Use ⪯
for prefix. If two chains can be prefixes of each other in either order, name that relation:
"If either X ⪯ Y or Y ⪯ X, then X and Y are said to be consistent" (Lazy Blockchains).

Name intermediate quantities with short symbols and gloss each once, right where it is
introduced. "γ should be thought of as a 'discounted' version of α" (Pass, Seeman, shelat).
Per-round indicator variables are defined before any lemma uses them: "if Xi = 1, we call i a
successful round and if Yi = 1, a uniquely successful round" (Bitcoin Backbone, Sec. 4.1).

## 4. Definitions

Template: "Definition n (Name). A ... is ... if ..." or "We say that ... if ...". One property
per definition, universally quantified over parties, rounds and chains. "for any pair of honest
players P1, P2 adopting the chains C1, C2 at rounds r1 ≤ r2 ... C1⌈k ⪯ C2" (Bitcoin Backbone,
Def. 3).

Properties are parametrised predicates, and the parameter travels to the theorem instead of
being fixed in the definition. "Predicate growth(τ, k) is satisfied if and only if for every
slot t ≤ Tmax − τ, ..." (Availability-Accountability Dilemma, FC 2022)

Two-part properties are two short parallel clauses, not one long sentence. "Safety: For all
rounds r' ≥ r + ν: L ⪯ L∪r'. Liveness: For all rounds r' ≤ r − ν: L∩r' ⪯ L" (Proofs of
Proof-of-Stake with Sublinear Complexity, AFT 2023)

A dense definition is followed by one plain sentence saying what it means. "Intuitively, the
firewall property above gives the following guarantee" (Sidechains). Under
`mechanics.md`, write that sentence as a plain declarative, without "intuitively".

Keep one definition template throughout. Weak papers drift: "Definition 1. (Monotonicity)"
against "Definition 5 (Suffix sensitivity)" in the same paper (NIPoPoW).

## 5. Randomness: pay once

The single most consistent device in the corpus. Define the random variables, define a
"typical execution" as a list of inequalities and structural conditions, prove in one theorem
that executions are typical with high probability, then write every later statement as a
deterministic claim about a typical execution. "An execution is typical with probability
1 − e^{−Ω(ε²λf + κ − log L)}" (Bitcoin Backbone, Thm. 10); "we assume a typical execution in
all proofs" (Blink, FC 2025); "A typical execution of ... is timely(v)." (On-Chain Timestamps,
FC 2024)

Give the exponent, not just "negligible", when it is available. "with probability at least
1 − e^{−Ω(min{ρ^{1−ε}, κ})}" (PoSAT, FC 2021)

Name bad events before bounding them, and chain the bound in one display.
"Pr[...|Bad] ≤ Pr[Discrepancy] + Pr[Invalid-Proof] ≤ negl(λ)" (Lazy Blockchains)

Flag dependence before any concentration bound. "But Yi and Yi+1 are dependent (both depend
on Xi+1), so we cannot directly invoke Chernoff bounds. Luckily, Yi and Yi+2 are independent."
(Ren, Analysis of Nakamoto Consensus). Flag random stopping times before using distributional
facts: "T0 and T1 are random variables ... so the proof cannot invoke properties of Poisson for
intervals defined by them" (Ren)

Defer standard steps explicitly instead of reproving them: "The proof uses standard Chernoff
bounds, along the lines of [20]" (Mining in Logarithmic Space, CCS 2021). Do not defer a step
that is specific to your setting.

## 6. Statements

Quantify everything explicitly and carry the parameters. "Suppose a (1/2, 3Δ)-compliant
execution of Goldfish in the synchronous sleepy network model. Then, w.o.p., Goldfish is secure
with transaction confirmation time Tconf = 2κ + 2 slots." (Goldfish)

State the positive result and the matching attack at the same threshold, ideally in one
theorem. "If p_a < θ(p_h, δ) then ... k-consistency and u-liveness [hold] ... If p_a > θ(p_h,
δ), then the private chain attack is successful" (Gaži, Kiayias, Russell, CCS 2020)

A top-level theorem may be a one-line consequence of named lemmas. "Executions are typical with
overwhelming probability (Theorem 3). Typical executions are safe (Theorem 1), and live
(Theorem 2), from which security follows" (PoEM). "Proof of Thm. 4. From Lems. 2 and 3."
(Adversary Majority)

Import external facts by their exact number with a plain nickname. "Lemma 4 (Lemma 4.2 in
[10], (aka Chain Growth))" (Blink). Say what changed when a proof is adapted: "The proof of
Lemma 5 is an adaptation of the proof of Lemma 8 from [GKR20] to our setting" (Gaži, Ren,
Russell). Compare to a prior lemma rather than silently reproving it: "The above lemma
resembles [49, Lemma 4]" (PoPoS Sublinear)

Give tightness its own titled theorem, not a remark. "Theorem 2 (The attack from Theorem 1 is
tight up to φ)" (PoSpace (In)security)

## 7. Proofs

**Opening.** Restate the setting and name the method in the first sentence. "Consider a typical
execution and let C1 be the chain of honest player P1 at round r1" (Bitcoin Backbone, Lemma 25).
For contradiction, put the negated claim in the same sentence: "Assume, towards a
contradiction, an execution in which the assumptions of the lemma hold, but either C1⌈k ⪯̸ C2
or ..." (Bitcoin Backbone, Lemma 14). When a minimal counterexample is used, say so: "Towards
contradiction, let r be the smallest round such that ..." (Adversary Majority)

**Roadmap.** A multi-step proof announces its steps. "In order to prove Lemma 2, we proceed in
six steps as illustrated in Fig. 5." (PoSAT). A multi-lemma section names the role of each
lemma in one sentence: "Lem. 1 shows that ...; Lem. 2 shows ...; Finally, Lem. 3 shows ..."
(Goldfish)

**Chaining.** One claim per sentence, each justified by a named source: "By Lemma X", "From
Lemma X", "Via Lemma 1 (recency property), b' must be on the checkpoint-respecting LC"
(Availability-Accountability Dilemma). Cite the fact, not "the proof of" a lemma; if a proof
step is needed elsewhere, promote it to a lemma.

**Cases.** Label them and confirm every case closes. "Case 1: ... Case 2: ... Case 3: ... All
three cases result in a contradiction, concluding the proof" (Sidechains). Name disjoint sets
before splitting on them (Blink). When a case is omitted by symmetry, say so: "The other two
cases are fully analogous" (Gaži, Ren, Russell, CCS 2022)

**Pairing arguments.** The uniquely successful round pairing is the load-bearing combinatorial
step of the whole line; write it as an explicit injective map, not as a count. "Each y in Y can
now be paired with a distinct malicious block in Z as follows." (Ren)

**Boundary cases.** Genesis, the empty range and the first round get one line each, or their
own lemma. "Lemma 9. B' exists. Proof. The genesis block satisfies the definition of B'."
(Blink). "By induction on s − r ≥ 0. For the basis (s = r), observe that ..." (Bitcoin
Backbone, Lemma 7). Carry exact round arithmetic through: "received by party P at the beginning
of round r' + 1" (On-Chain Timestamps)

**Without loss of generality** is justified, never bare. "Without loss of generality, we may
assume that n is even; otherwise, Z puts one node to sleep throughout the execution"
(Availability-Accountability Dilemma)

**Closing.** Name the fact that is contradicted or the inequality that was reached. "But then
Z(S) ≥ Y(S) contradicts Lemma 11." (Bitcoin Backbone). "This is a contradiction with the fact
that t' ∈ [t1 + Δ, t2 − Δ] is a checkpoint-strong pivot." (Availability-Accountability
Dilemma). A long derivation closes by pointing at the numbered steps: "where (18) is due to
Lemma 5 and Corollary 11, (19) is due to (11), and (20) is due to (13)." (Guo, Ren, AFT 2022)

**Register.** Present tense. "We" for author actions. Displayed math only for the load-bearing
chain of inequalities; connective arithmetic stays inline. Ren's note contains zero occurrences
of "clearly", "easy to see" or "trivial".

## 8. Intuition and roadmaps

Intuition comes before the formal argument and is short: one paragraph at lemma level, up to a
page at section level, with a concrete small instance. "For intuition, consider the scenario
with n = 4, f = 1." (Accountable Safety Implies Finality, FC 2024). A lemma is paraphrased in
plain words right before its statement: "Informally, the lemma says that if the number of
blocks the adversary obtained ... then there exist y − 2z blocks that will always belong to the
chain of every honest party" (Mining in Logarithmic Space). A sketch given in the introduction
is reused, not repeated: "We already sketched the general idea in Section 1.4 and will make it
more formal here." (PoSpace (In)security)

Under `mechanics.md`, the intuition sentence is a declarative statement of what the lemma
says, with no metaphor and no "the key insight is".

## 9. Attacks and tightness

An attack is a named strategy with numbered steps, defined once and referenced by name. "every
adversarial block extends a longest blockchain that does not contain tx ... All adversarial
blocks are kept private until ..." (Guo, Ren, Def. 2). "A does the following: 1. On round
i = 1, it forks the chain to create ..." (PoSpace (In)security). "We construct an adversary A
that breaks the superchain quality at level μ. A works as follows" (NIPoPoW)

Motivate the bound by the attack before proving the bound tight (Velvet Path, AFT 2021). Argue
optimality sample-path-wise when possible, not only in expectation: "the private-mining attack
is a best attack for every sample path, regardless of statistics" (Guo, Ren)

Impossibility proofs use named indistinguishable worlds: "Consider the following two worlds:
World A. ... World B." (On-Chain Timestamps)

Correct prior claims precisely, with the reason: "It was claimed in [2, Appendix F] that the
private-mining attack is optimal ... but the proof therein does not apply to the case when the
target block is mined by an adversary." (Guo, Ren)

## 10. Remarks, hedging, limitations

Remarks carry scope and modelling caveats, not results and not proofs. "While our analysis can
be adapted to a probabilistic setting, we don't do so as it does not lead to any more
interesting insight." (PoSpace (In)security)

Hedge by stating exactly what is open, never by softening a claim. "its exact resilience, if
any, remains unknown" (Blink). "we do not attempt to prove any such fact here, and indeed our
framework is not appropriate for such an analysis." (Byzantine Generals in the Permissionless
Setting, FC 2023). Admit looseness and say why: "we give an upper bound rather than an exact
recurrence in the critical region" (Gaži, Ren, Russell, CRYPTO 2023)

Conjectures are labelled as such and kept out of theorems: "we conjecture that the bound
y − 2z cannot be substantially increased" (Mining in Logarithmic Space)

## 11. Contributions, abstract, related work

Contributions: a short paragraph, then a numbered list of "We <verb>" items with section
pointers. "(1) We put forth the first light client for lazy blockchains ... (2) We show our
system is complete, sound, and succinct with reduction-based proofs (Section 5)" (Lazy
Blockchains)

Give one concrete numeric instantiation of the main result, not only asymptotics. "our upper
and lower bounds are within 90 seconds of each other for 1-hour settlement assuming 10 second
network delays and a 10% adversary" (Gaži, Ren, Russell, CCS 2022)

Related work is compared by proof technique, and cited at the point of use: "we use the
techniques developed in the Backbone line of work [16]. We follow their definitions" (Velvet
Path)

## 13. Anti-patterns

Each of these appears in a published paper and reads as a weakness.

- "It is not hard to see that", "This is obvious", "The proof is straightforward", "The theorem
  follows." standing in for an argument.
- A proof step attributed to "the proof of Lemma X" instead of a stated lemma.
- Re-deriving the same typicality fact twice in one paper instead of citing it once.
- An unnumbered "Claim." paragraph inside a proof whose own proof starts "This is true because".
- Personified or colorful asides in technical text: "Nakamoto blocks have a god-like
  permanence"; "This charmingly simple protocol"; exclamation marks.
- Stacked abbreviations "Lem., Prop., Def., App." forcing many forward references.
- A pronoun whose referent is unclear ("its round", "this block") when two objects are in play.
- Deferring a definition to an appendix with no substitute sentence in the body.
- Skipping a symmetric case silently.
- Typos in camera-ready text: "contradiciton", "Consequenty", "cruicially", "schdeuling".

## 14. Checklist

- [ ] Model paragraphs in the order parties, timing, adversary, protocol, notation.
- [ ] Every ambiguous phrase has a convention sentence before first use.
- [ ] Random variables defined before any lemma; one typicality theorem; everything else
      deterministic "in a typical execution".
- [ ] Every theorem quantifies its rounds, chains and parties explicitly.
- [ ] Every imported fact cites source and number, with a nickname.
- [ ] Every contradiction proof opens with the negated claim and closes by naming the
      contradicted fact.
- [ ] Every multi-lemma section has a one-sentence roadmap naming each lemma's role.
- [ ] Boundary cases (genesis, empty range, first round) handled in one visible line each.
- [ ] Attack stated as a named definition with numbered steps; tightness stated as a theorem.
- [ ] Open questions and looseness stated explicitly in a remarks section.
- [ ] One concrete numeric instantiation of the main coefficient or bound.
- [ ] No "clearly", "obviously", "easy to see", "straightforward".

## 15. Corpus and provenance

Per-paper notes with verbatim quotes and section pointers live in the project that produced
this file, under `resources/style/` (`notes_fc.md`, `notes_zindros.md`, `notes_consensus.md`,
and the three `report_*.md` syntheses). Papers consulted:

FC: Light Clients for Lazy Blockchains (2024); Goldfish (2024); Accountable Safety Implies
Finality (2024); On-Chain Timestamps Are Accurate (2024); Consensus Under Adversary Majority
Done Right (2025); Blink (2025); On the (In)Security of PoSpace Longest-Chain Blockchains
(2025); Composability Treatment of Bitcoin's Ledger with Variable Difficulty (2025); Byzantine
Generals in the Permissionless Setting (2023); Proof of Necessary Work (2023);
Availability-Accountability Dilemma (2022); PoSAT (2021).

Zindros and coauthors: NIPoPoW (FC 2020); Proof-of-Stake Sidechains (S&P 2019); Mining in
Logarithmic Space (CCS 2021); The Velvet Path (AFT 2021); Proofs of Proof-of-Stake with
Sublinear Complexity (AFT 2023); A Better PoW Fork Choice Rule (2024); Rollerblade (2024);
Better Safe than Sorry (2023).

Longest-chain analysis: Bitcoin Backbone (GKL, latest ePrint); Pass, Seeman, shelat
(EUROCRYPT 2017); Everything is a Race (CCS 2020); Tight Consistency Bounds for Bitcoin (CCS
2020); Practical Settlement Bounds for PoW (CCS 2022) and for Longest-Chain Consensus (CRYPTO
2023); Bitcoin's Latency-Security Analysis Made Simple (AFT 2022); Close Latency-Security
Trade-off (AFT 2021); Full Analysis of Nakamoto Consensus in Bounded-Delay Networks (2020);
PoW Consensus in Expected-Constant Time (EUROCRYPT 2024); Nakamoto Consensus under Bounded
Processing Capacity (CCS 2024); Ren, Analysis of Nakamoto Consensus (2019); Infinitely Running
Blockchain Protocols (anonymous draft, read locally).
