# Model

Binding for every agent. Proofs and arguments may use only the assumptions listed here.
Changing it after approval needs human approval (see `approvals.md`).

- status: <draft | approved>
- approved at commit: <hash>

## Parties

<Who participates, how many, which are honest. Example: n validators, at most f Byzantine.>

## Timing and network

<Synchronous, partially synchronous (GST), asynchronous, or rounds. Delay bound and who knows it.>

## Adversary

Powers: <corruption model (static, adaptive, mildly adaptive), message scheduling, computational power or stake fraction.>

Limits: <what the adversary cannot do: forge signatures, exceed the corruption bound, delay beyond Delta after GST.>

## Oracle or setup

<Random oracle, PKI, common reference string, genesis, trusted setup. "None" if none.>

## Protocol

<Pointer to the protocol: file, section and algorithm labels. Do not restate it here.>

## Notation

<One paragraph: indexing conventions, prefix relation, length vs height, rounds vs slots, "by round r" convention.
Point to `glossary.md` for terms and macros.>

## Assumptions

One row per assumption. A proof step that uses something not listed here is model drift.

| ID | Statement | LaTeX label |
|---|---|---|
| A1 | <one line> | <asm.name or none> |
