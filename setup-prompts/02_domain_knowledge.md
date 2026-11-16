# Task: Build the domain knowledge base for my research workflow

## Context

`~/dotclaude` holds my Claude Code research workflow (agents, skills, review gates). It has an empty `skills/domain/` skill. Your job is to fill it with domain knowledge so that every agent understands my field the way a careful researcher in it does: what the adversary is, which network models exist and how they differ, how properties are stated, which assumptions matter, which proof techniques are standard, which attacks are canonical, and what reviewers in this field care about versus what they ignore.

My field: blockchain consensus and security proofs. Proof-of-work and longest-chain protocols (Bitcoin Backbone line), BFT and committee-based consensus, proof-of-stake, light clients and superlight clients (NIPoPoWs), sidechains, finality, accountability, client-side verification, networking assumptions.

The knowledge base must be **grounded**: every substantive statement is backed by a verbatim quote with a source pointer, in the same style as `skills/academic-writing/paper-architecture.md` (read it first as the model for tone and grounding).

## How to work

- Work in stages. Stop after each stage, show me the output and wait for my OK.
- This task spans several sessions. Keep progress in `~/dotclaude/knowledge/PROGRESS.md` (sources done, concepts done, next step). Any new session must be able to resume from that file alone.
- Use subagents for the per-source reading (fresh context per source batch). Route by the `model-routing` skill: Sonnet 5.5 for per-source notes, Opus 5.5 high for concept synthesis, Mythos 5.2 xhigh for the cross-concept consistency pass and for the taste synthesis.
- Never invent a definition. If sources disagree, record every variant with its source. Do not pick a winner unless I say so.
- No em dashes.

---

## Stage A: Corpus inventory

Build `knowledge/corpus.md`, a table of candidate sources with: id, title, authors, year, venue, local path or URL, type (my paper, coauthor paper, reference paper, textbook, lecture notes, reviews received), and priority (core, useful, skip).

Look in:

1. My workspace directory: ask me for the path. Scan every project for `resources/`, `.tex` sources, `.bib` files, PDFs, notes, and reviewer comments (files named like reviews, rebuttal, response, camera-ready notes).
2. My own papers and drafts (LaTeX sources are better than PDFs).
3. The corpus already listed in `skills/academic-writing/paper-architecture.md` section 15, and the note files it mentions under `resources/style/` in the project that produced it (locate that project).
4. Papers frequently cited across my `.bib` files: rank by citation count across my projects, propose the top ones.
5. Open-access copies (IACR ePrint, arXiv) for core papers that are not local. Propose the list of URLs; download only after I approve.

Stop and let me edit the priorities.

---

## Stage B: Per-source notes

For each core and useful source, a subagent writes `knowledge/notes/<id>.md`:

- Model: parties, timing and network model, adversary (power, corruption model, adaptivity, resource bound), setup assumptions. Verbatim quotes with section or page pointers.
- Definitions of properties used (exact statement, parameters).
- Main results: statements with thresholds and parameters.
- Proof techniques used and where.
- Attacks described.
- Notation conventions.
- Anything the paper explicitly says is subtle, wrong in prior work, or commonly misunderstood.

Batch 3 to 5 sources per subagent. Each note lists which quotes it could not verify against the source text. The citation-verifier agent spot-checks 20% of quotes per batch; any failure means the whole batch is redone.

---

## Stage C: Concept files

Synthesize `skills/domain/concepts/<concept>.md`, one file per concept, each with this fixed template:

```
# <Concept>
## Definition(s)
  each variant: statement, source quote and pointer, which papers use it
## Standard notation
## Parameters and thresholds
  e.g. resilience bounds and the model they hold in
## How it is used in proofs
## Common pitfalls and reviewer objections
## Related concepts
  [[links]]
```

Concepts, at minimum (add more if the corpus demands it, and tell me):

- **Adversary**: Byzantine, crash, omission, rational, covert; static, adaptive, mildly adaptive (corruption delay); computationally bounded; resource-bounded (hashing power fraction, stake fraction); rushing; adversary controlling message delivery and order.
- **Network and timing**: lock-step synchronous rounds, bounded delay Δ, partial synchrony with GST (and the unknown-Δ variant), asynchrony, sleepy and dynamic participation, eclipse and partitions, diffusion vs point-to-point, recurrent synchrony if present in my work.
- **Setup assumptions**: PKI, common random string, genesis, random oracle, hash function as oracle, q queries per round, clocks and clock drift.
- **Properties**: safety, liveness, consistency or common prefix, chain growth, chain quality, persistence, finality, accountable safety, liveness under adaptive corruption, ledger safety and liveness as predicates with parameters.
- **Resilience**: honest-majority thresholds per model (e.g. n > 3f for partial synchrony, 1/2 for PoW with the delay discount), what changes them, the role of Δ, and tightness results.
- **Proof techniques**: typical execution, Chernoff and martingale bounds with dependence caveats, convergence opportunities and pairing arguments, hybrid and indistinguishable-worlds arguments, reductions to hash or signature security, quorum intersection, induction on rounds.
- **Attacks**: private mining, selfish mining, balance attack, long-range, nothing-at-stake, grinding, eclipse, double spend, liveness attacks, bribing; each as a named strategy with steps and the property it breaks.
- **Clients**: full nodes, light clients, superlight clients, NIPoPoWs, sync committees, what they trust.
- **Proof-of-stake specifics**: stake distribution, leader election, VRFs, posterior corruption.

Every statement in a concept file carries at least one source pointer to a note file. Statements I am likely to disagree with go into a `## Open` section, not into the body.

---

## Stage D: Taste file

`skills/domain/taste.md`: what matters and what does not in this field, **as practiced by me and my coauthors**. Evidence sources, in order of weight:

1. Reviews my papers received and my responses (if found in Stage A).
2. My own edits: in my git repos, find commits where I rewrote text that was drafted by someone else or by an AI (large prose diffs in `.tex` files). Extract before and after pairs and what changed. These are the strongest signal of my preferences.
3. My own papers versus the reference corpus: what my papers state explicitly that others leave implicit, and the reverse.
4. The existing writing style files.

Format: each entry is a rule plus its evidence (quote or diff pointer). Mark each entry `[evidenced]` or `[proposed]`. A `[proposed]` entry needs my confirmation before agents use it. Do not attribute to me a preference that has no evidence.

Include sections: what a reviewer in this field checks first; which assumptions must always be explicit; what counts as a contribution versus an incremental tweak; standard expectations for model sections and for tightness; typical reasons papers in this area get rejected (only if evidenced by reviews or by the corpus).

---

## Stage E: Verification

1. citation-verifier checks every quote in the concept files and taste file against the note files and the sources.
2. A Mythos 5.2 xhigh consistency pass across all concept files: contradictions between files, wrong thresholds, wrong attributions, definitions that drifted from their source. Output as issue JSON.
3. Codex review of the concept files (via the codex-review skill) for factual errors in the domain. Output as issue JSON.
4. Present me a short list: issues found, and every place where sources disagree. I decide each one.

---

## Stage F: Packaging

- `skills/domain/SKILL.md`: when to load what. An index that maps project types and playbook stages to the concept files they need (e.g. the modeler always loads adversary, network-and-timing, setup-assumptions; the counterexample-hunter loads attacks and the property it targets). Keep each concept file under ~250 lines; split if longer.
- Update every agent file in `agents/` with a line naming which domain files it loads by default.
- Wire `/retro` to propose additions to concept files and taste file, with the same grounding rules.
- Commit.

## Stage G: Writing examples and LaTeX conventions from the workspace

The global writing files currently contain no project-specific examples. They hold placeholders marked `EXAMPLES: to be populated by prompt 02 Stage G`. Fill them from the workspace inspection:

1. **LaTeX conventions.** Compare `macros.tex` (and the equivalents) across all academic projects. A macro pattern used in most of my projects becomes a global convention in `skills/academic-writing/latex.md`. Examples of such patterns: a macro for function names in typewriter, for variable names in sans serif, for algorithm event handlers, for algorithm comments, for author notes. Record each one as a pattern plus the most common macro name, not as one project's list. Everything else stays project-level and goes into that project's glossary during migration. Show me the table: pattern, macro names seen, projects, proposed global form.
2. **Examples.** For each placeholder in `mechanics.md`, `latex.md` and `paper-architecture.md` (definition, proof, theorem statement, model paragraph, evaluation paragraph, attack definition, remark), pick 2 or 3 candidate excerpts from **my own academic papers** across the workspace. Prefer excerpts that need no project-specific macros to understand. Do not use client material. Present the candidates side by side; I choose one per placeholder. Each chosen example gets a short "Observe:" line saying which rules it shows, in the style of the old podovery examples.
3. **Generic terminology.** Terms that have the same fixed meaning across several of my projects (e.g. quorum, certificate, honest party) go into a global `skills/academic-writing/glossaries/common.md`, with the projects they come from. Terms whose meaning differs between projects stay project-level, and you list the conflicts for me.

## Constraints

- Notes and concept files contain quotes short enough to be fair use and always with source pointers. Never copy whole sections of papers.
- Never mark a `[proposed]` taste rule as `[evidenced]` without evidence.
- Do not download anything before I approve the list.
