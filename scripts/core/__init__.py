"""Core domain models, protocols, and operations for deep-research tooling.

Built following Clean Architecture principles:
- Domain Models & Value Objects (models.py)
- Protocols & Data Interfaces (protocols.py)
- Pure Business Operations (operations.py)
- In-memory test stubs and clean dependency injection
"""

from .models import (
    ProgressMetrics,
    ResearchState,
    RunStats,
    SemVer,
    UpdateResult,
    UpdateStatus,
)
from .operations import (
    bump_manifest_versions,
    calculate_progress,
    check_git_update,
    compile_run_stats,
    format_run_stats,
)
from .document import (
    DocumentPage,
    ObjectiveItem,
    ReconciliationReport,
    TodoItem,
    derive_todos,
    extract_objectives_from_page,
    ingest_document,
    map_overlaps_and_deduplicate,
    reconcile_coverage,
    split_into_pages,
)
from .protocols import GitClient, ManifestStore, StateReader

__all__ = [
    "ProgressMetrics",
    "ResearchState",
    "RunStats",
    "SemVer",
    "UpdateResult",
    "UpdateStatus",
    "calculate_progress",
    "compile_run_stats",
    "format_run_stats",
    "bump_manifest_versions",
    "check_git_update",
    "StateReader",
    "ManifestStore",
    "GitClient",
    "DocumentPage",
    "ObjectiveItem",
    "TodoItem",
    "ReconciliationReport",
    "split_into_pages",
    "extract_objectives_from_page",
    "map_overlaps_and_deduplicate",
    "derive_todos",
    "reconcile_coverage",
    "ingest_document",
]
