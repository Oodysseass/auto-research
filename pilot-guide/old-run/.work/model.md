# Model

Binding for every agent. Proofs and arguments may use only the assumptions listed here.
Changing it after approval needs human approval (see `approvals.md`).

- status: draft
- approved at commit: none

Source: `resources/notes.md`, section "Model" (lines 3-36), without changes (R3). Line references `notes:N` are to that file.
LaTeX: `paper/lemmas.tex`, `\section{Model}` (`sec.model`). Assumption k in the PDF is Ak below; the label is the binding link.

## Parties

There are n parties (A1). The adversary corrupts a fixed set of at most t parties before the execution starts (A1).
The parties in that set are corrupted; the other parties are honest (glossary terms "corrupted party", "honest party").
At least two parties are honest, n - t >= 2, and the adversary may corrupt at least one party, t >= 1 (A2).

## Timing and network

Rounds r = 1, 2, 3, ...; every party knows the current round (A3). Round 0 is the state before round 1 (A4).

Network assumptions, stated separately so that a proof cites exactly the ones it uses:
- A10: a chain an honest party broadcasts in round r is delivered to every honest party in round r + 1.
- A11: the adversary cannot drop or delay the deliveries of A10.
- A12: in any round, the adversary may deliver any chain it knows to any subset of the honest parties, and to none of the others.
- A13: rushing.

When an honest party broadcasts is fixed by step 4 of A6, not by the network assumptions.
No A-ID states that every honest party sees every honest chain within one round. The notes do not state it
(it appears only as the position in `resources/BRIEF.md:12`). A proof that relies on such a property must
derive it and cite the A-IDs it uses (contract check P2).

## Adversary

Powers:
- Static corruption of a fixed set of at most t parties before the execution starts (A1), with t >= 1 (A2).
- One mining attempt per corrupted party per round, on any chain the adversary chooses (A8).
- Delivery of any chain it knows to any subset of the honest parties, and to none of the others, in any round (A12).
- Rushing: in round r it sees the honest broadcasts of round r before it chooses its own deliveries for round r + 1 (A13).

Limits:
- Corrupts at most t parties, and at least two parties are honest (A1, A2).
- Cannot forge blocks; only valid chains exist; every chain an honest party receives is valid (A5).
- Cannot drop or delay the deliveries of A10 (A11).
- One mining attempt per corrupted party per round (A8).

## Oracle or setup

The notes state no setup beyond the genesis chain (A4). Whether a mining attempt succeeds is part of the execution (A9).

## Protocol

The honest round procedure is A6: `paper/lemmas.tex`, `\paragraph{Honest round procedure}`, label `asm.honest-round`,
steps 1 to 4 in source order (receive, adopt with the tie rule, mine, broadcast), from `notes:17-21`.
There is no algorithm file. Cite a step as "step k of `asm.honest-round`".

## Notation

Notation entries, each stated in `paper/lemmas.tex` in a `definition` environment with the `def.` label given, under the
paragraph named in brackets. They define notation only and add no assumption. Macros are in `paper/macros.tex` and listed in `glossary.md`.

- Corrupted and honest parties, `def.honest-corrupted` [Parties and corruption]: the corrupted parties are the parties in the set of A1; the other parties are honest. Source: `glossary.md` Terms; the notes use both words without a definition.
- Chain and length, `def.chain-length` [Chains], `notes:14`: a chain is a sequence of blocks that starts with `\genesis`. Its length `\len{C}` is the number of blocks of C after `\genesis`, so `\len{\genesis} = 0`.
- Successful round, `def.successful-round` [Mining], `notes:26`: round r is successful if at least one honest mining attempt succeeds in round r.
- `\chainat{P}{r}`, `def.chain-at` [Notation], `notes:35`: the chain of honest party P at the end of round r; `\chainat{P}{0} = \genesis`.
- `\minlen{r}`, `\maxlen{r}`, `def.min-max-len` [Notation], `notes:36`: the minimum and the maximum of `\len{\chainat{P}{r}}` over all honest P; so `\minlen{0} = \maxlen{0} = 0`.

Conventions: length counts the blocks after G, so len(G) = 0; there is no separate height. Round 0 is the state before
round 1, and `\chainat{P}{r}` is the state at the end of round r. No indexing of blocks inside a chain and no prefix relation
are used by the notes. Terms and macros: `glossary.md`.

## Assumptions

One row per assumption. A proof step that uses something not listed here is model drift.

| ID | Statement | LaTeX label |
|---|---|---|
| A1 | There are n parties. The adversary corrupts a fixed set of at most t parties before the execution starts. [notes:6] | asm.static-corruption |
| A2 | At least two parties are honest: n - t >= 2. The adversary may corrupt at least one party: t >= 1. [notes:7] | asm.corruption-bounds |
| A3 | The execution proceeds in rounds r = 1, 2, 3, .... Every party knows the current round. [notes:10] | asm.rounds |
| A4 | Before round 1, that is, in round 0, every party holds the genesis chain G. [notes:11] | asm.genesis |
| A5 | Only valid chains exist. The adversary cannot forge blocks. Every chain an honest party receives is valid. [notes:15] | asm.valid-chains |
| A6 | In round r, an honest party P executes, in this order: (1) receive every chain delivered to P in round r; (2) adopt the longest chain among its current chain and the received chains, and on a tie keep the current chain; (3) make one mining attempt, and on success extend the current chain by one block; (4) if the current chain changed during round r, broadcast it. [notes:17-21] | asm.honest-round |
| A7 | Each honest party makes one mining attempt per round. [notes:24] | asm.honest-mining |
| A8 | Each corrupted party makes one mining attempt per round, on any chain the adversary chooses. [notes:24] | asm.corrupted-mining |
| A9 | Whether a mining attempt succeeds is part of the execution. Every pattern of successes is a possible execution. [notes:25] | asm.success-patterns |
| A10 | A chain that an honest party broadcasts in round r is delivered to every honest party in round r + 1. [notes:29] | asm.honest-delivery |
| A11 | The adversary cannot drop or delay the deliveries of A10. [notes:30] | asm.no-drop |
| A12 | In any round, the adversary may deliver any chain it knows to any subset of the honest parties, and to none of the others. [notes:31] | asm.adversarial-delivery |
| A13 | The adversary is rushing: in round r, it sees the honest broadcasts of round r before it chooses its own deliveries for round r + 1. [notes:32] | asm.rushing |

## Source map

Every line of `resources/notes.md` lines 5-36 with content, and where it is stated.

| notes line | Content | A-ID or notation entry |
|---|---|---|
| 5 | heading "Parties and corruption" | paragraph heading |
| 6 | n parties; static corruption of a fixed set of at most t parties | A1 |
| 7 | n - t >= 2; t >= 1 | A2 |
| 9 | heading "Time" | paragraph heading "Rounds" |
| 10 | rounds 1, 2, 3, ...; every party knows the current round | A3 |
| 11 | round 0; every party holds G | A4 |
| 13 | heading "Chains" | paragraph heading |
| 14 | chain starts with G; len(C); len(G) = 0 | notation: chain and length |
| 15 | only valid chains; no forging; received chains valid | A5 |
| 17 | honest party P in round r, in this order | A6 |
| 18-21 | steps 1 to 4 (receive, adopt with tie rule, mine, broadcast) | A6, steps 1 to 4 |
| 23 | heading "Mining" | paragraph heading |
| 24 | one honest attempt per round; one corrupted attempt per round on any chain the adversary chooses | A7, A8 |
| 25 | success is part of the execution; every pattern is possible | A9 |
| 26 | successful round | notation: successful round |
| 28 | heading "Network" | paragraph heading |
| 29 | honest broadcast in r delivered to every honest party in r + 1 | A10 |
| 30 | no dropping or delaying | A11 |
| 31 | adversarial delivery to any subset | A12 |
| 32 | rushing | A13 |
| 34 | heading "Notation" | paragraph heading |
| 35 | C_P^r; C_P^0 = G | notation: `\chainat{P}{r}` |
| 36 | m_r, M_r; m_0 = M_0 = 0 | notation: `\minlen{r}`, `\maxlen{r}` |

## Open points

Points on which `resources/notes.md` is silent or ambiguous. They are not resolved here. A proof that needs one of them
resolved must stop and report it. Each needs a human decision before it can become an assumption.

- OP1. Chains the adversary knows. `notes:31`: "the adversary may deliver any chain it knows". The notes do not say which
  chains the adversary knows: for example G, the honest broadcasts (seen by `notes:32`), chains received by corrupted parties,
  or chains extended by successful corrupted attempts. `notes:24` ("on any chain the adversary chooses") does not say
  whether the chosen chain must be one the adversary knows.
- OP2. Own broadcast. `notes:29`: "A chain an honest party broadcasts in round r is delivered to every honest party in
  round r + 1." The notes do not say whether the broadcasting party itself is among the receivers.
- OP3. Ties among received chains. `notes:19`: "Adopt the longest chain among its current chain and the received chains.
  On a tie, keep the current chain." The tie rule covers a tie with the current chain. The notes do not say which chain
  is adopted when two or more received chains have the same greatest length and are longer than the current chain.
- OP4. Result of a successful corrupted attempt. `notes:24`: "Each corrupted party makes one mining attempt per round, on
  any chain the adversary chooses." The notes state the result of a success only for honest parties (`notes:20`: "On
  success, extend the current chain by one block"). They do not state what a successful corrupted attempt produces.
  The `glossary.md` term "mining attempt" says a corrupted success extends the chosen chain by one block; that reading
  is not in the notes, and no A-ID states it. Until the human decides OP4, the corrupted case of that glossary row is
  not an assumption, and no proof or counterexample may cite it.
- OP5. Forging and validity. `notes:15`: "Only valid chains exist: the adversary cannot forge blocks, and every chain an
  honest party receives is valid." The notes define neither "valid" nor "forge". They do not state that every block
  after G in a chain comes from a successful mining attempt.
- OP6. Order of events within a round across parties. The notes fix the order of steps for one honest party
  (`notes:17`: "in this order"). They do not say: whether a chain an honest party broadcasts in round r can be received
  by another honest party in step 1 of the same round r; whether a chain the adversary delivers "in any round" r
  (`notes:31`) is received in step 1 of round r; when in a round the corrupted mining attempts (`notes:24`) take place
  relative to the adversary's deliveries; or whether the deliveries of `notes:29` can arrive before round r + 1.
  `notes:32` fixes one point only: the adversary sees the honest broadcasts of round r before it chooses "its own
  deliveries for round r + 1".
- OP7. Current chain and held chain. The notes use "holds" (`notes:11`), "its current chain" (`notes:19-21`) and "the
  chain of honest party P" (`notes:35`). They do not say explicitly that these denote the same chain.
