# podovery: content removed from the global style files

Moved verbatim from `skills/academic-writing/mechanics.md` and `latex.md` (originally `~/.claude/writing_style.md`).
Migration (prompt 03) uses it for the podovery project. Each block is the exact removed text.

## mechanics.md header note

<<<<<<< removed text
The reference excerpts at the end use podovery macros; see `templates/project/glossary.podovery.md`.
>>>>>>> end

## mechanics.md, Titles section, lead-in to good examples (pointed at the podovery evaluation excerpt)

<<<<<<< removed text
**Good**, matching the reference example already in this file:
>>>>>>> end

## mechanics.md, What to avoid (fixed sentence-length limit, replaced by the verbosity and rhythm rule; not podovery-specific)

<<<<<<< removed text
- Sentences longer than ~30 words in definitions or proof steps.
>>>>>>> end

## mechanics.md, What to avoid, macro example

<<<<<<< removed text
- Raw symbols where a macro exists (`tx` instead of `\tx`).
>>>>>>> end

## mechanics.md, Reference excerpts (podovery)

<<<<<<< removed text
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
>>>>>>> end

## mechanics.md, Checklist (fixed sentence-length limit, replaced; not podovery-specific)

<<<<<<< removed text
- [ ] No sentence in a proof or definition exceeds approximately 30 words.
>>>>>>> end

## latex.md header note

<<<<<<< removed text
Project macros live in the project's `.work/glossary.md` (example: `templates/project/glossary.podovery.md`).
>>>>>>> end

## latex.md, LaTeX conventions intro

<<<<<<< removed text
The reference project is `podovery`. Follow its conventions exactly.
>>>>>>> end

## latex.md, Macros (generic patterns added)

<<<<<<< removed text
The macro list is project-specific. Read it from the project's `.work/glossary.md`.
>>>>>>> end

## latex.md, Cross-references examples (podovery labels)

<<<<<<< removed text
```latex
\Cref{lem.unique-direct}         % "Lemma 3"
\Cref{alg.validator.voting}      % "Algorithm 1"
\Cref{line.direct-child}         % "Line 5"
```
>>>>>>> end

## latex.md, Math, concatenation macro

<<<<<<< removed text
Concatenation: `\concat` (expands to `\,\|\,`).
>>>>>>> end

## latex.md, Algorithms, event-handler macros

<<<<<<< removed text
 Event handlers use `\On`, `\EndOn`.
>>>>>>> end

## latex.md, Citations

<<<<<<< removed text
 Use `\cite{fastpay}` for Fastpay.
>>>>>>> end
