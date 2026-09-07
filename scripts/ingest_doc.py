"""CLI for document ingestion, page mapping, and todo derivation.

Usage: python scripts/ingest_doc.py <path_to_doc> [--output-dir DIR]
Implements the 9-stage pipeline from research/doc-map-scratchpad/report.md:
- Splits document structurally into discrete pages/sections.
- Emits isolated page extracts into evidence/00-pages/ so divers don't overload context.
- Maps cross-page overlaps and deduplicates objectives.
- Derives acceptance-criteria todos.
- Reconciles coverage deterministically to guarantee zero missed requirements.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.core.document import ingest_document


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a multi-page document into isolated pages and todos.")
    parser.add_argument("doc_path", help="Path to markdown, text, or spec document")
    parser.add_argument("--output-dir", default="research/doc-ingest", help="Directory where artifacts will be written")
    opts = parser.parse_args()

    doc = Path(opts.doc_path)
    if not doc.exists():
        print(f"deep-research: document not found at {doc}", file=sys.stderr)
        return 2

    out_dir = Path(opts.output_dir)
    try:
        report = ingest_document(doc_path=doc, output_dir=out_dir)
    except Exception as err:
        print(f"deep-research: ingestion failed: {err}", file=sys.stderr)
        return 1

    print(f"[Document Ingested] {doc.name}")
    print(f"  Pages mapped: {report.pages_covered}/{report.total_pages} ({report.coverage_percentage}%)")
    print(f"  Todos generated: {report.total_todos}")
    print(f"  Artifacts written to: {out_dir}")
    print(f"    - Pages: {out_dir / 'evidence' / '00-pages'}")
    print(f"    - Objectives: {out_dir / 'objectives.md'}")
    print(f"    - Todos: {out_dir / 'todos.md'}")
    print(f"    - Reconciliation: {out_dir / 'reconciliation.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
