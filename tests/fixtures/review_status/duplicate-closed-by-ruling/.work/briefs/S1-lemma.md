# Brief S1-lemma

- stage: S1
- status: open
- assigned agent: prover
- artifact slug: lemma
- critical: yes
- main theorem: no

## Budget

- rounds: 5
- tokens: 100k

## Review log

| round | gate | reviewer | model | commit | verdict | blocking | major | minor | hashes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | G1 | conformance-reviewer | claude-opus-5-5 | c1 | accept | 0 | 0 | 0 | paper/lemma.tex=6a8f74c6215d |
| 1 | G2 | assumption-auditor | claude-opus-5-5 | c1 | accept | 0 | 0 | 0 | paper/lemma.tex=6a8f74c6215d |
| 1 | G2 | proof-checker | claude-opus-5-5 | c1 | revise | 0 | 1 | 0 | paper/lemma.tex=6a8f74c6215d |
| 2 | G2 | proof-checker | claude-opus-5-5 | c2 | revise | 0 | 1 | 0 | paper/lemma.tex=6a8f74c6215d |
| 3 | G2 | proof-checker | claude-opus-5-5 | c3 | revise | 0 | 1 | 0 | paper/lemma.tex=6a8f74c6215d |
| 1 | G2 | counterexample-hunter | claude-opus-5-5 | c1 | accept | 0 | 0 | 0 | paper/lemma.tex=6a8f74c6215d |
| 1 | G3 | codex | claude-opus-5-5 | c1 | revise | 0 | 1 | 0 | paper/lemma.tex=6a8f74c6215d |
