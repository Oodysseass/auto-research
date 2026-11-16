# Glossary: podovery (EXAMPLE, belongs to the podovery project)

This file is not global. It was moved from the former `~/.claude/writing_style.md`.
Migration (prompt 03) places it in the podovery project as `.work/glossary.md`.
Other projects use it only as a format example.

## Terms

The following terms have fixed meanings throughout the podovery project.
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

## Macros

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
