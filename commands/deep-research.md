---
description: Start a deep-research run on the given topic or multi-page document. Grills to a brief or ingests document into todos, then researches with citations.
argument-hint: <research topic or document path>
---

Run the `deep-research` skill on the topic or document below. Phase 0 first: verify all 4 MCP servers (arxiv, ddg-search, gutenberg, openalex) are available; if even 1 is missing, stop immediately and tell the user: "First install this, only then will deep-research work." If a document path is provided, run Document Ingestion Mode (`python scripts/ingest_doc.py`) to map pages, extract objectives, and derive todos. Then grill to a shared brief (Phase 1), plan, fan out with harness internet search fallback if DuckDuckGo fails, citation-gate, and report per the skill contract.

Topic: everything the user typed after `/deep-research`.
