# Glossary

This file wins over every global glossary on terminology. Never substitute a synonym for a term listed here.
The G0 lint script reads the Macros table: keep its columns and format.

## Terms

| Term | Meaning |
|---|---|
| <finalized> | <precise meaning, with thresholds if any> |

## Macros

Kinds: `system`, `object`, `function`, `variable`, `keyword`, `algorithm`, `note`.
Raw forms: comma-separated words that must not appear raw in text mode where the macro exists. Leave empty if none.
Macros of kind `note` are author notes. The lint reports leftover notes as warnings.

| Macro | Kind | Meaning | Raw forms |
|---|---|---|---|
| `<\macro>` | system | system name, bold | <SystemName> |
| `<\macro>` | object | <recurring object or field> | <raw word> |
| `<\macro>{name}` | function | function name in typewriter | |
| `<\macro>{name}` | variable | variable name in sans serif | |
| `<\macro>` | keyword | <true, false, return, break, concatenation> | |
| `<\begin-macro>` / `<\end-macro>` | algorithm | event-handler block | |
| `<\macro>{...}` | algorithm | full-line comment; inline comment, right-aligned | |
| `<\macro>{...}` | note | author note (one per author) or generic todo | |

## Notation conventions

- Indexing: <e.g. C[0] is genesis, C[-1] is the tip, Python-style slices>
- Prefix relation: <e.g. \preceq, and "consistent" when either is a prefix of the other>
- Length vs height: <which counts genesis, which is zero-based>
- Rounds and time: <"by round r" means during rounds 1..r, or as fixed in model.md>
