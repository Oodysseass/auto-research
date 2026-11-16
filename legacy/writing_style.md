# Academic Writing Style Guide

This file defines the writing style for academic prose.
It is to be read before drafting or editing any paper section, abstract, definition, theorem, proof, or related text.

---

## Core principles

**Precision over elegance.**
Every noun, verb, and qualifier must mean exactly one thing in context.
If a term has multiple meanings in the literature, disambiguate it on first use or pick a different term.

**Simple before complex.**
State the simple case first. Generalize only after the reader has the base case.
A sentence that requires re-reading is a bad sentence.

**One idea per sentence.**
Do not join two distinct ideas with a conjunction if each idea can stand alone.
Reserve longer sentences for cases where the relationship between clauses is the point.

**No unsound claims.**
Do not write "clearly", "obviously", "it is easy to see" unless what follows is genuinely immediate from the previous sentence.
If a step requires proof, either prove it or say it is left to the reader and cite a reason.

**No invented vocabulary.**
Do not coin terms unless necessary. When necessary, define them formally before use.
Do not use metaphors or analogies in definitions, theorems, or proofs.

---

## Modeling and notation

**Math is a means, not an end.**
The end is to convey a result and its message. The math exists to state precisely what we intuitively
mean, in a form that supports proofs. Do not do math for the sake of math.

**Do not over-model.**
Model only what the results use. Keep the model as simple as the argument allows.
No cumbersome notation, no extra layers of formalism, no generality that no result needs.
Simplicity is not vagueness: model assumptions and definitions must still be precise and concrete.
Every assumption is stated explicitly, and every definition says exactly which objects it quantifies over.

**Use established notation.**
For objects already established in the literature, use the notation of the bibliography the paper builds on.
Do not rename a known object. Beyond that, follow the author's own notation and the notation of
Dionysis Zindros's papers (e.g. $\Pi$ for a protocol, $\mathcal{A}$ for the adversary, $\Delta$ for the
delay bound, $\mathsf{GST}$ for the global stabilization time, $\kappa$ for the security parameter).

## Economy and rhythm

**No math for its own sake.**
Every result must serve the end goal of the document and must make intuitive sense to the reader.
Before stating a lemma, ask what it buys. If the answer is "nothing the reader needs", drop it.

**Prove only what is necessary and sufficient.**
State the lemmas and theorems the argument needs, and no others. Do not overprove.
Do not prove several variants of a statement when one carries the argument.

**No redundant notation.**
Introduce a symbol only if it is used several times and saves the reader effort.
Do not name an object that is mentioned once. Do not give one object two names.
Prefer the protocol's own variables and macros over fresh symbols.

**Build slowly, then go deep.**
Order the text from the simplest concept to the hardest one, both across the paper and within a section.
Introduce a concept at low technical depth first: what it is, and why it matters.
Be slow at the start. Use a concrete example, with numbers if possible, and give the intuition.
Only once the intuition is built, and the reader can follow, get technical: the precise definition,
the model, the proof technique.
The aim is that a reader thinks "this introduces a very difficult concept in the easiest way possible".
Content being present is not enough. It must also be presentable.

**Rhythm.**
The text must have a beat, both conceptually and as language.
Conceptually, alternate intuition and formality: example, then definition, then consequence.
As language, alternate short and long sentences. A run of long sentences tires the reader; a run of
short ones reads as a list. Place a short sentence where a point must land.
Use punctuation to pace the text: periods to stop, commas to breathe, colons to announce.
The prose should be easy to read through in one pass, and pleasant to read aloud.

---

## Titles: sections, subsections, paragraphs

Every heading, at every level, is a plain noun phrase naming its topic. Nothing else.

A heading is not allowed to be a sentence, a claim, a question, or a rhetorical hook that
reads as the next beat of an argument. This applies to `\section{}`, `\subsection{}`, and
especially `\paragraph{}`, which is used constantly and is where this failure mode creeps in.

**Good**, matching the reference example already in this file:
```
\paragraph{Throughput}
\paragraph{Full nodes}
\paragraph{Censorship}
\paragraph{Recurrent synchrony}
```

**Bad**, and to be rewritten on sight:
```
\paragraph{Silent clients are the binding restriction}
\paragraph{Rational validators force synchrony}
\paragraph{What our setting changes}
\paragraph{Solvability nonetheless coincides}
\paragraph{Clock wrappers do not repair the separation}
\paragraph{Why it is different}
```

The bad examples assert a claim and dangle it like a teaser, the way a talk or a blog post
signposts its next point. That is narrative structure, and it does the reader's inference for
them before the paragraph has earned it. A heading should be retrievable from the table of
contents as a topic, not read as a punchline.

If the point the bad heading was trying to make is worth stating, state it as the first
sentence of the paragraph body, as a plain declarative claim, not as the heading itself.
`\paragraph{Silent clients are the binding restriction}` becomes `\paragraph{Silent clients}`
with "Silent clients are the binding restriction." as the paragraph's opening sentence.

This rule applies uniformly to top-level section titles as well. "Recurrent Synchrony is
Strictly Stronger" is a claim; the section title should be "Recurrent Synchrony" (or, if the
document needs to distinguish it from an earlier definitional section, "The Separation" is
still a claim dressed as a phrase and should be "Separation" or "Comparison to GST").

## Mechanics

- **No em dashes.** Use a comma, a period, or a colon instead.
- **No parenthetical asides mid-sentence** unless they are single symbols or short standard abbreviations.
- **Active voice preferred** in construction descriptions. Passive voice is acceptable in proof steps.
- **Short sentences first.** A paragraph should generally start with its shortest sentence. Complexity builds within the paragraph.
- **No hedging language** ("somewhat", "rather", "quite", "in a sense"). Either the claim holds or it does not.

---

## Sentence structure patterns

**Introducing a concept:**
> We assume [setting]. [Object] is defined as [definition]. [Consequence or motivation].

Not:
> In what follows, we will be considering a setting where [long clause] and [long clause], which [further qualification].

**Stating a result:**
> [Subject] satisfies [property]. [One-sentence proof sketch or forward pointer.]

Not:
> As we will show, [subject], which was introduced earlier, satisfies [property], a fact that will prove instrumental in what follows.

**Proof steps:**
> [Claim]. By [lemma/definition/assumption], [consequence]. Therefore [conclusion].

Not:
> Since [long clause], and given that [long clause], it follows that [conclusion], which is what we wanted.

---

## Terminology discipline

The following terms have fixed meanings throughout this body of work.
Do not substitute synonyms within a proof or definition.

| Term | Meaning |
|---|---|
| finalized | received a quorum of n-f attestations, or induced by a finalized anchor |
| directly finalized | finalized via an explicit n-f quorum |
| indirectly finalized | finalized as a consequence of a finalized anchor (solution or recovery) |
| certificate | n-3f votes over the same payload |
| quorum | n-f votes over the same payload |
| bot certificate | n-f votes with no payload reaching the certificate threshold |
| honest validator | a validator following the prescribed protocol |
| Byzantine validator | a validator deviating arbitrarily |
| nonce | a strictly increasing per-account counter |
| solver | the party responsible for proposing a solution in the CLOB protocol |
| iteration | one round of the CLOB protocol |

---

## LaTeX conventions

The reference project is `podovery`. Follow its conventions exactly.

### Document structure

```
main.tex          — document class, inputs, bibliography
includes.tex      — package imports only
macros.tex        — all macros and theorem environments
01introduction.tex
02model.tex
03construction.tex
04analysis.tex
05evaluation.tex
06further.tex
07related-work.tex
algorithms/       — one file per algorithm, \input'd from construction
bibliography/     — ref.bib
```

Build with: `latexmk -synctex=1 -pdf -outdir=output main.tex`

### Document class

The default format is Financial Cryptography and Data Security (FC): Springer LNCS.

```latex
\documentclass[runningheads]{llncs}
```

`llncs` already defines `definition`, `example`, `remark`, `theorem`, `lemma`, `proposition`,
`corollary` and `proof`. Do not redefine them, and do not load `amsthm`.
Add `\AtEndEnvironment{proof}{\qed}` so that proofs end with a QED mark.
Put keywords inside the abstract with `\keywords{A \and B \and C}`.

### Macros

Always use macros for recurring symbols. Never write raw text where a macro exists.

System name: `\sys` (expands to bold text via `\ensuremath{\textbf{...}}\xspace`)

Transaction fields:
```latex
\tx       % transaction
\pk       % public key
\nonce    % nonce
\body     % body
\parent   % parent
\acc      % account
\st       % state
\pendingst % pending state
\pending  % pending
\finalized % finalized (field)
\lvotes   % vote list \mathcal{L}
\votes    % votes field
\cert     % certificate
\qc       % quorum certificate
\vote     % vote
\ancestors % ancestors function
```

Functions:
```latex
\fn{name}    % typewriter font for function names
\valid       % \fn{valid}
\execute     % \fn{execute}
\apply       % \fn{apply}
\verify      % \fn{verify}
```

Variables:
```latex
\var{name}   % \textsf for variable names
```

Algorithm keywords:
```latex
\true   \false   \concat   \return   \breakk
```

Algorithm block for event handlers:
```latex
\On{event description}
  ...
\EndOn
```

Comments in algorithms:
```latex
\CommentLine{full-line comment}
\Comment{inline comment}   % appears right-aligned with \hfill
```

Author notes (remove before submission):
```latex
\odysseas{note text}   % blue
\giorgos{note text}    % purple
\todo{text}            % brown
```

### Theorem environments

Defined in `macros.tex`. Use as follows:

```latex
\begin{definition}[Name]\label{def.name}
    ...
\end{definition}

\begin{lemma}\label{lem.name}
    ...
\end{lemma}
\begin{proof}
    ...
\end{proof}

\begin{corollary}\label{cor.name}
    ...
\end{corollary}

\begin{theorem}[Name]\label{thm.name}
    ...
\end{theorem}

\begin{assumption}\label{asm.name}
    ...
\end{assumption}

\begin{remark}\label{rem.name}
    ...
\end{remark}
```

### Labels

Use consistent prefixes:
```
def.    — definitions
lem.    — lemmas
cor.    — corollaries
thm.    — theorems
asm.    — assumptions
rem.    — remarks
alg.    — algorithms
sec.    — sections
fig.    — figures
line.   — algorithm lines
```

### Cross-references

Always use `\Cref{}` (capital C, from cleveref). Never `\ref{}` or `\eqref{}`.

```latex
\Cref{lem.unique-direct}         % "Lemma 3"
\Cref{alg.validator.voting}      % "Algorithm 1"
\Cref{line.direct-child}         % "Line 5"
```

For multiple references: `\Cref{lem.a,lem.b}` produces "Lemmas 3 and 4".

### Math

Use `\mathbb{N}` for natural numbers. Use `\kappa` for security parameter.
Quantifiers: `\forall`, `\exists`, `\land`, `\lor`, `\neg`, `\in`, `\notin`, `\subseteq`, `\cup`, `\cap`.
Set comprehension: `\{ x \colon P(x) \}` (use `\colon`, not bare `:`).
Intervals: `[k_1, k_2)` with standard bracket notation.
Concatenation: `\concat` (expands to `\,\|\,`).

### Algorithms

One algorithm per file in `algorithms/`. Input into the section file with `\input{algorithms/alg.name}`.

Use `algpseudocode` style. State lines use `\State`. Conditions use `\If`, `\ElsIf`, `\Else`, `\EndIf`. Loops use `\For`, `\EndFor`, `\While`, `\EndWhile`. Event handlers use `\On`, `\EndOn`.

Label individual lines with `\label{line.name}` placed after the statement on the same line so `\Cref{line.name}` resolves correctly.

### Paragraphs

Use `\paragraph{Name}` for named subsections within a section that do not warrant a `\subsection`.
Example: `\paragraph{Throughput}`, `\paragraph{Voting}`, `\paragraph{Execution}`.

### Citations

Use `\cite{key}` inline. Use `\cite{fastpay}` for Fastpay. Bibliography file is `bibliography/ref.bib`. Style is `splncs04`.

---

## What to avoid

- Em dashes anywhere.
- Semicolons joining long independent clauses.
- Sentences longer than ~30 words in definitions or proof steps.
- Passive constructions that hide the subject in proofs.
- Raw symbols where a macro exists (`tx` instead of `\tx`).
- `\ref{}` instead of `\Cref{}`.
- Hardcoded theorem names instead of `\Cref{}`.
- Section, subsection, or `\paragraph{}` titles phrased as sentences, claims, or rhetorical hooks
  (e.g. "Silent clients are the binding restriction", "What our setting changes"). A title is a
  noun phrase. See "Titles: sections, subsections, paragraphs" above.

**Avoid this pattern:**
> The key insight here is that [paraphrase of what was just said], which allows us to [thing that will be stated formally anyway].

**Avoid this pattern:**
> It is worth noting that [observation], since [long justification that belongs in a proof].

---

## Reference excerpts

### Primary reference: podovery (LaTeX source)

**Good: definition**
```latex
\begin{definition}[Transaction $\tx$]
    We call a transaction the structure
    $\tx = (\pk, \nonce, \body, \parent, \sigma)$, where
    $\pk \in \{0, 1\}^\kappa$ is the public key of the signer,
    $\nonce \in \mathbb{N}$ is the nonce of the transaction, $\body$ is the
    application logic of the transaction, $\parent$ is a transaction $\tx'$ with
    $\tx'.\nonce = \tx.\nonce - 1$ and $\sigma$ is the signature of the client.
\end{definition}
```

Observe: flat enumeration, each field on its own clause, no digression.

**Good: proof**
```latex
\begin{proof}
    Suppose towards a contradiction that two honest validators $R_1$ and $R_2$
    have directly finalized different transactions $\tx$ and $\tx'$ for nonce
    $k$, with $\tx \neq \tx'$. By definition, any honest validator that directly
    finalizes a transaction $\tx$ for nonce $h$ must have received at least $n-f$
    votes on $\tx$. From \Cref{lem.n-f-intersection}, the sets of votes for
    $\tx$ and $\tx'$ must share at least $n-3f$ votes from honest validators.
    From \Cref{alg.validator.voting}, an honest validator only votes once per
    nonce. Thus the shared votes must be on the same transaction. Therefore,
    $\tx' = \tx$. Contradiction.
\end{proof}
```

Observe: assumption stated first. Each sentence advances by one step. "Contradiction." is a single word on its own sentence.

**Good: evaluation paragraph**
```latex
\paragraph{Throughput}

Throughput is the number of transactions that can be finalized per unit of time.
In order to easily evaluate the throughput, we normalize the time w.r.t. the
network delay. Namely, we measure the amount of transactions that can be
finalized in a time window of size $\Delta$.
```

Observe: first sentence is shortest. Each sentence adds one layer.

---

## Checklist before submitting a draft

- [ ] Every term in a proof appears in a definition or is standard in the literature.
- [ ] No sentence in a proof or definition exceeds approximately 30 words.
- [ ] No em dashes.
- [ ] No "clearly", "obviously", "it is easy to see" unless the step is genuinely immediate.
- [ ] First sentence of each paragraph is the shortest.
- [ ] Every heading (section, subsection, `\paragraph{}`) is a noun phrase, not a sentence, claim, or rhetorical hook.
- [ ] No invented terminology without a preceding formal definition.
- [ ] Every `\Cref{}` points to a label that exists.
- [ ] Every macro is used; no raw text where a macro is defined.
- [ ] Every lemma cited in a proof is applicable to the case at hand.
- [ ] Every lemma and theorem is needed by the end goal; nothing is overproved.
- [ ] Every symbol is used more than once and has a single name.
- [ ] Each concept is introduced intuitively, with an example where possible, before its technical detail.
- [ ] Concepts appear in order of difficulty, simplest first.
- [ ] The model contains nothing that no result uses, and every assumption is stated explicitly.
- [ ] Established objects use the notation of the bibliography.
- [ ] Sentence lengths alternate; the text reads through in one pass.
