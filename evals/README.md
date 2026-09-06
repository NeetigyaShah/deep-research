# evals/ — the solo measurement loop

One question matters more than any feature: did the change make runs better?
This folder answers it without infrastructure.

## The loop

1. Pick a seed question below matching the change area.
2. Run `/deep-research` on it (fresh directory, same brief shape each time).
3. Score the finished run:
   - **kept-claim rate** = kept / (kept + dropped) from `stats.json`.
   - **judge accuracy** = spot-check 10 kept claims against their quotes; fraction entailed.
   - **turns-per-kept-claim** from `state.md` (`turns_this_round` summed / kept).
4. Record the row in `scoreboard.md` (create it): date, change, question, three numbers.
5. Ablation rule: test one change at a time. Two changes in one run teaches nothing.

## Cadence

- `check_repo.py` in CI guards the contract (files exist, schema valid).
- Eval runs are manual or nightly — they spend model calls, so they never block PRs.

## Growing the set

Add questions with known-good answers only: a question whose answer you cannot verify by hand within 10 minutes does not belong here. Prefer topics with stable primary sources (docs, standards, textbooks) over fast-moving news.
