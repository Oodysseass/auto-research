# Academic writing: mechanics

Moved verbatim from the former `~/.claude/writing_style.md`. Applies to all academic prose.

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

**Good**:
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

## What to avoid

- Em dashes anywhere.
- Semicolons joining long independent clauses.
- Unnecessary verbosity. A sentence is too long when it can be split, or shortened, without losing
  meaning. A long sentence is fine when the relationship between its clauses is the point. See
  "One idea per sentence" and "Rhythm" above.
- Passive constructions that hide the subject in proofs.
- Raw symbols where a macro exists (raw text instead of the project's macro).
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

EXAMPLES: to be populated by prompt 02 Stage G.

Each example is a short good excerpt in LaTeX, followed by one "Observe:" line naming the rules it shows.
No example may come from a single client or research project.

- Definition: a structure or property defined as a flat enumeration, one field per clause, no digression.
- Proof: a contradiction proof that states the assumption first, advances one step per sentence with a named source, and closes on the contradicted fact.
- Evaluation paragraph: a `\paragraph{}` with a noun-phrase title whose first sentence is the shortest and each later sentence adds one layer.

---

## Checklist before submitting a draft

- [ ] Every term in a proof appears in a definition or is standard in the literature.
- [ ] No unnecessary verbosity: no sentence can be split or shortened without losing meaning, and the text keeps its rhythm (see "One idea per sentence" and "Rhythm").
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
