---
description: Start a deep-research run on the given topic. Grills to a shared goal contract first, then researches until every goal is answered.
argument-hint: <research topic>
---

Run the `deep-research` skill on the topic below. Phase 0 first: verify all 4 MCP servers (arxiv, ddg-search, gutenberg, openalex) are available; if even 1 is missing, stop immediately and tell the user: "First install this, only then will deep-research work." Then grill to a shared goal contract (Phase 1: WHAT, OUTCOME goals, DONE-WHEN criteria), plan, fan out with harness internet search fallback if DuckDuckGo fails, iterate until every goal is answered, and deliver the white-paper HTML report per the skill contract.

Topic: everything the user typed after `/deep-research`.
