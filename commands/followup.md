---
description: Ask about a finished deep-research run; say 'research more' to dig deeper with the same tools.
argument-hint: [run] <question>
---

Follow the `deep-research` skill Phase 7 (follow-up). Resolve the run first: if the first word names a directory under `research/` containing `state.md`, that is the run and the rest is the question; otherwise use the run with the newest `state.md` and treat everything as the question.

Load `brief.md`, `report.md`, `state.md`, `outline.md` read-only — never re-grill, never rewrite the brief. Answer strictly from kept evidence with existing `[n]` cites, end with exactly one verdict line (`ANSWERED FROM EVIDENCE` or `NEEDS MORE RESEARCH: ...`), and only spawn new diver batches on explicit user confirmation, gating new claims and updating evidence/state/report/stats before printing a fresh STATS block.

Question: everything the user typed after `/followup` (minus an optional leading run name).
