---
name: followup
description: Ask questions about finished deep-research runs, verify answers strictly from kept evidence, or trigger targeted follow-up research.
---

# Follow-up (Deep Research Phase 7)

Follow-up interface for completed deep-research runs. Allows the user to ask questions about findings, see supporting evidence, or expand research into specific sub-topics without re-running the entire intake pipeline.

## When to Apply
- The user asks a question about a prior research run (e.g. `/skill:followup [slug] <question>` or `/followup <question>`).
- Asking for a summary, clarification, or synthesis of results in `research/<slug>/`.
- Exploring whether an existing report answers a new angle, or confirming if deeper research is needed.

## Protocol
1. **Target Run Resolution**:
   - If an argument explicitly names a directory under `research/` containing `state.md`, that is the target run.
   - Otherwise, resolve the run with the newest `state.md` under `research/`.
   - If no runs exist, notify the user and stop.
2. **Read-Only Evidence Pass**:
   - Load read-only: `brief.md`, `report.md`, `state.md`, `outline.md`, and relevant files in `evidence/`.
   - Never re-grill. Never rewrite `brief.md`.
   - Answer strictly from kept evidence, reusing the report's existing `[n]` citations.
   - Do NOT search the web or make new unverified factual claims in this step.
3. **Verdict Line**:
   - Conclude every answer with exactly one verdict line:
     - `ANSWERED FROM EVIDENCE`
     - or `NEEDS MORE RESEARCH: <what is missing> + <proposed queries>`
4. **Targeted Deep Dive (Only on User Confirmation)**:
   - If the user confirms digging deeper ("research more", "dig deeper", "expand this"):
     - Spawn ONE targeted diver batch using the same Phase 3 tools.
     - Gate new findings through peer verification (Phase 4).
     - Append to `evidence/NN-<diver>.md` (continuing numbering).
     - Update `state.md`, `outline.md`, `report.md`, `report.html`, and `stats.json`.
     - Append the Q/A and outcome to `followups.md`.
     - Print the updated progress bar and STATS block.
