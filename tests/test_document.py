"""Unit and integration tests for document ingestion, page mapping, and todo derivation."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.core.document import (
    derive_todos,
    extract_objectives_from_page,
    ingest_document,
    map_overlaps_and_deduplicate,
    reconcile_coverage,
    split_into_pages,
)


def test_split_into_pages_with_table_preservation() -> None:
    sample_text = (
        "# Page 1: Overview\n\n"
        "Here is the overview of the project with general requirements.\n\n"
        "| Feature | Priority | Effort |\n"
        "| --- | --- | --- |\n"
        "| Auth | P0 | S |\n"
        "| Billing | P1 | M |\n"
        "| Reporting | P2 | L |\n\n"
        "<!-- page 2 -->\n\n"
        "# Page 2: Authentication\n\n"
        "Detailed authentication specifications.\n"
        "- **OAuth2 Flow**: Support Google and GitHub providers.\n"
        "  - Criteria: Validates token on redirect.\n"
    )

    pages = split_into_pages(sample_text)
    assert len(pages) == 2, f"Expected 2 pages, got {len(pages)}"
    assert pages[0].page_number == 1
    assert "| Feature | Priority | Effort |" in pages[0].content
    assert pages[1].page_number == 2
    assert "OAuth2 Flow" in pages[1].content
    print("ok   structural pagination with table preservation verified")


def test_extract_and_derive_todos() -> None:
    sample_doc = (
        "# Feature List: User Management\n\n"
        "<!-- page 1 -->\n"
        "## User Roles and Permissions\n"
        "System must support Role-Based Access Control (RBAC).\n"
        "- Criteria: Admin, Editor, and Viewer roles.\n"
        "- Criteria: Deny unauthorized API calls with 403.\n\n"
        "<!-- page 2 -->\n"
        "## User Roles and Permissions\n"
        "Additional security constraints for RBAC roles.\n"
        "- Criteria: Audit log on every permission change.\n\n"
        "<!-- page 3 -->\n"
        "## Session Revocation\n"
        "Admins can instantly revoke active sessions.\n"
        "- Criteria: Revocation propagates across nodes within 500ms.\n"
    )

    pages = split_into_pages(sample_doc)
    assert len(pages) == 3

    all_objs = []
    for p in pages:
        all_objs.extend(extract_objectives_from_page(p))

    # Expect 3 raw objectives
    assert len(all_objs) == 3

    # Map overlaps and dedup: the two 'User Roles and Permissions' objectives should merge
    merged = map_overlaps_and_deduplicate(all_objs)
    assert len(merged) == 2, f"Expected 2 merged objectives, got {len(merged)}"

    rbac_obj = next(o for o in merged if "Roles" in o.title)
    assert 1 in rbac_obj.related_pages and 2 in rbac_obj.related_pages
    assert len(rbac_obj.acceptance_criteria) >= 3

    # Derive todos
    todos = derive_todos(merged)
    assert len(todos) == 2
    assert todos[0].id == "TODO-01"
    assert len(todos[0].acceptance_criteria) >= 3
    assert "Source Page" in todos[0].context_extract

    # Reconcile coverage
    report = reconcile_coverage(pages, todos)
    assert report.is_fully_covered
    assert report.coverage_percentage == 100.0
    print("ok   objective extraction, overlap deduplication, and todo derivation verified")


def test_end_to_end_ingest_document() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        doc_path = Path(tmp) / "sample_spec.md"
        doc_path.write_text(
            "# System Spec Document\n\n"
            "<!-- page 1 -->\n"
            "## Data Ingestion Pipeline\n"
            "High-throughput event ingestion queue.\n"
            "- Criteria: Ingest 10k events/sec.\n\n"
            "<!-- page 2 -->\n"
            "## Storage Engine\n"
            "Append-only columnar storage engine.\n"
            "- Criteria: Read latency under 20ms.\n",
            encoding="utf-8",
        )

        out_dir = Path(tmp) / "research" / "test-run"
        report = ingest_document(doc_path=doc_path, output_dir=out_dir)

        assert report.total_pages == 2
        assert report.pages_covered == 2
        assert report.is_fully_covered

        # Verify artifacts
        p1 = out_dir / "evidence" / "00-pages" / "page-01.md"
        p2 = out_dir / "evidence" / "00-pages" / "page-02.md"
        assert p1.exists() and "Data Ingestion Pipeline" in p1.read_text(encoding="utf-8")
        assert p2.exists() and "Storage Engine" in p2.read_text(encoding="utf-8")

        obj_file = out_dir / "objectives.md"
        todo_file = out_dir / "todos.md"
        recon_file = out_dir / "reconciliation.md"

        assert obj_file.exists() and "Total Pages: 2" in obj_file.read_text(encoding="utf-8")
        assert todo_file.exists() and "TODO-01" in todo_file.read_text(encoding="utf-8")
        assert recon_file.exists() and "Coverage: 100.0%" in recon_file.read_text(encoding="utf-8")

    print("ok   end-to-end ingest_document with scratchpad artifacts verified")


if __name__ == "__main__":
    test_split_into_pages_with_table_preservation()
    test_extract_and_derive_todos()
    test_end_to_end_ingest_document()
    print("\nAll document ingestion tests passed!")
