# Academic writing: LaTeX conventions

Moved from the former `~/.claude/writing_style.md`. Load for any `.tex` work.
Project macros live in the project's `.work/glossary.md`.

## LaTeX conventions

### Document structure

```
main.tex: document class, inputs, bibliography
includes.tex: package imports only
macros.tex: all macros and theorem environments
01introduction.tex
02model.tex
03construction.tex
04analysis.tex
05evaluation.tex
06further.tex
07related-work.tex
algorithms/: one file per algorithm, \input'd from construction
bibliography/: ref.bib
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
The macro list is project-specific. Read it from the project's `.work/glossary.md`.
The exact macro names come from prompt 02 Stage G and from each project's glossary.
Every project defines macros for the following patterns:

- System name: one macro for the name of the system, typeset in bold.
- Recurring objects and fields: one macro per object or field of the model (transactions, keys,
  counters, states, votes, certificates, and so on).
- Function names: a generic macro that typesets a function name in typewriter font, plus one
  shorthand macro per recurring function.
- Variable names: a generic macro that typesets a variable name in sans serif.
- Algorithm keywords: macros for true, false, return, break and concatenation.
- Algorithm event handlers: a begin and end macro pair for an event-handler block.
- Algorithm comments: one macro for a full-line comment and one for an inline comment, right-aligned.
- Author notes: one colored note macro per author, plus a generic todo macro. Remove all notes before submission.

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
def.: definitions
lem.: lemmas
cor.: corollaries
thm.: theorems
asm.: assumptions
rem.: remarks
alg.: algorithms
sec.: sections
fig.: figures
line.: algorithm lines
```

### Cross-references

Always use `\Cref{}` (capital C, from cleveref). Never `\ref{}` or `\eqref{}`.

EXAMPLES: to be populated by prompt 02 Stage G.
One `\Cref{}` call each for a lemma, an algorithm and an algorithm line, with the rendered text as a comment.

For multiple references: `\Cref{lem.a,lem.b}` produces "Lemmas 3 and 4".

### Math

Use `\mathbb{N}` for natural numbers. Use `\kappa` for security parameter.
Quantifiers: `\forall`, `\exists`, `\land`, `\lor`, `\neg`, `\in`, `\notin`, `\subseteq`, `\cup`, `\cap`.
Set comprehension: `\{ x \colon P(x) \}` (use `\colon`, not bare `:`).
Intervals: `[k_1, k_2)` with standard bracket notation.
Concatenation: use the project's concatenation macro, typeset as `\,\|\,`.

### Algorithms

One algorithm per file in `algorithms/`. Input into the section file with `\input{algorithms/alg.name}`.

Use `algpseudocode` style. State lines use `\State`. Conditions use `\If`, `\ElsIf`, `\Else`, `\EndIf`. Loops use `\For`, `\EndFor`, `\While`, `\EndWhile`. Event handlers use the project's event-handler macro pair.

Label individual lines with `\label{line.name}` placed after the statement on the same line so `\Cref{line.name}` resolves correctly.

### Paragraphs

Use `\paragraph{Name}` for named subsections within a section that do not warrant a `\subsection`.
Example: `\paragraph{Throughput}`, `\paragraph{Voting}`, `\paragraph{Execution}`.

### Citations

Use `\cite{key}` inline. Bibliography file is `bibliography/ref.bib`. Style is `splncs04`.
