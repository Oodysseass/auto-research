# Glossary: backbone-model (PoW, longest-chain) papers

Moved from section 12 of the former `fc_writing_style.md`. Load for PoW or longest-chain projects.
The project's `.work/glossary.md` wins over this file on terminology.

## 12. Vocabulary for backbone-model papers

Fix these once and never substitute synonyms.

| Term | Meaning |
|---|---|
| has a chain at round r | the local chain at the start of round r (Backbone Alg. 4, line 7 variable C) |
| adopts a chain at round r | the output of maxvalid at round r, before mining |
| computed at round r | output of a successful oracle query made at round r |
| sends / receives | the network action and its arrival, with the round of each stated |
| successful round | X_i = 1, some honest party computes a block |
| convergence opportunity | Y_i = 1, exactly one honest party computes a block (Backbone: uniquely successful round) |
| honest block | computed by a party honest at that round; genesis counts as honest |
| typical execution | the named event on which every later statement is conditioned |
| block tree at round r | all blocks computed by round r, including private adversarial blocks |
| length / height | say which counts genesis and which is zero-based, once |
