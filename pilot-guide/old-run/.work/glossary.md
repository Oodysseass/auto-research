# Glossary

This file wins over every global glossary on terminology. Never substitute a synonym for a term listed here.
The G0 lint script reads the Macros table: keep its columns and format.

## Terms

Taken from `resources/notes.md`. Meanings are as fixed there; `model.md` will give the A-IDs.

| Term | Meaning |
|---|---|
| party | one of the n participants |
| honest party | a party not in the corrupted set |
| corrupted party | a party in the set of at most t parties the adversary corrupts before round 1 (static corruption) |
| round | time step r = 1, 2, 3, ...; round 0 is the state before round 1 |
| genesis chain | the chain G; every party holds it at round 0 |
| chain | a sequence of blocks that starts with G; only valid chains exist |
| length | len(C), the number of blocks of C after G; len(G) = 0 |
| adopt | step 2 of an honest round: take the longest of the current and received chains, keeping the current chain on a tie |
| mining attempt | one attempt per party per round; success extends the current chain (honest) or a chain the adversary chooses (corrupted) by one block |
| successful round | a round in which at least one honest mining attempt succeeds |
| broadcast | step 4: an honest party sends its current chain if it changed during the round |
| deliver | a chain broadcast by an honest party in round r reaches every honest party in round r + 1; the adversary may also deliver any chain it knows to any subset of honest parties in any round |
| rushing | the adversary sees the honest broadcasts of round r before choosing its deliveries for round r + 1 |
| C_P^r | the chain of honest party P at the end of round r; C_P^0 = G |
| m_r, M_r | minimum and maximum of len(C_P^r) over all honest P; m_0 = M_0 = 0 |
| Chain growth | Lemma 1 of `resources/notes.md` (main result) |
| Bounded honest spread | Lemma 2 of `resources/notes.md` (auxiliary) |

## Macros

No `.tex` macros exist in `resources/`. The macros below are defined in `paper/macros.tex` (S4 Model).

| Macro | Kind | Meaning | Raw forms |
|---|---|---|---|
| `\genesis` | object | the genesis chain G (`notes:11`, `notes:14`) | |
| `\len{C}` | function | len(C), the number of blocks of C after G; typeset as len(C) | len |
| `\chainat{P}{r}` | object | C_P^r, the chain of honest party P at the end of round r | |
| `\minlen{r}` | object | m_r, the minimum of len(C_P^r) over all honest P | |
| `\maxlen{r}` | object | M_r, the maximum of len(C_P^r) over all honest P | |
| `\begin{assumption}` | environment | theorem-like environment for model assumptions (`asm.` labels), defined with `\spnewtheorem`; `\Cref` prints "Assumption" | |

## Notation conventions

- Indexing: none fixed in `resources/`. No block indexing inside a chain is used.
- Prefix relation: not used in `resources/`.
- Length vs height: len(C) counts blocks after G; len(G) = 0. There is no separate height. Macro `\len{C}`.
- Rounds and time: C_P^r is the state at the end of round r; round 0 is the initial state. Within a round, an honest party receives, adopts, mines, broadcasts, in that order (A6, `asm.honest-round`). The order of events across parties within a round is open (`model.md`, OP6).
- Open term: the corrupted case of the Terms row "mining attempt" (what a successful corrupted attempt produces) is open (`model.md`, OP4). It is not an assumption, and no proof or counterexample may cite it until the human decides OP4.
- Definitions: the notation entries of `model.md` are `definition` environments in `paper/lemmas.tex` with `def.` labels (`def.honest-corrupted`, `def.chain-length`, `def.successful-round`, `def.chain-at`, `def.min-max-len`); cite them with `\Cref{def.<name>}`.
- Assumptions: Assumption k in `paper/lemmas.tex` is Ak of `model.md`; cite it with `\Cref{asm.<name>}`, and a step of the honest round procedure as "step k of `\Cref{asm.honest-round}`".
