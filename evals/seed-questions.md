# Seed questions (12)

Each: the question, the family, what a good run produces. Score per evals/README.md.

## Tech explainers

1. How does SQLite's write-ahead log recover after a crash? — good: WAL frames/checkpoint/salt mechanism from sqlite.org docs, 6+ kept claims.
2. What does the Raft protocol guarantee during a network partition? — good: leader election + log matching from the Raft paper/thesis, no uncited safety claims.
3. How does Python's GIL affect multithreaded CPU-bound code in 3.12? — good: cites docs + a benchmark source, states version scope.

## Policy and regulation

4. What are India's CCTS emission-intensity targets for cement in FY25-26? — good: BEE notification numbers with gazette quotes.
5. How does the EU CBAM deduct domestic carbon prices paid abroad? — good: Article 9 mechanism from EUR-Lex, worked example or explicit gap.
6. What must an NHTSA Part 573 defect report contain? — good: itemized from 49 CFR 573.6 primary text.

## Product comparisons

7. How do Consensus, Elicit, and Scite differ in grounding answers? — good: retrieve-first vs meter vs sentence-links, each from vendor docs.
8. Which free academic APIs need no account, and what are their rate limits? — good: OpenAlex/Semantic Scholar/OpenAlex-key facts from official docs.
9. What do Perplexity's first-party docs say about its Deep Research cycles? — good: vendor docs only, or an honest gap when primaries block.

## Science

10. What is the observer-vs-agentic gap reported for deep-research inertia bias? — good: 2608.23045 figures with sections, plus the paper's own limits.
11. How does ParallelSearch cut turns versus sequential search? — good: 2508.09303 turn counts plus transfer numbers.
12. What fraction of sensemaking happens without tools, and why? — good: 2411.07206 survey figures with reasons breakdown.

## Scoring note

A run scoring under 0.5 kept-claim rate fails regardless of coverage — it guessed more than it grounded. Under 6 kept claims on a 4-question brief fails on depth.
