"""Unit tests for core domain models, operations, and protocol stubs.

Follows the Clean Architecture testing strategy:
- Tests domain logic in memory without subprocesses or disk I/O.
- Verifies Value Objects, immutability, and boundary rules.
- Exercises Protocol stubs (DataInterface pattern) for deterministic isolated runs.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.core import (
    ProgressMetrics,
    ResearchState,
    RunStats,
    SemVer,
    UpdateResult,
    UpdateStatus,
    bump_manifest_versions,
    calculate_progress,
    check_git_update,
    compile_run_stats,
    format_run_stats,
)
from scripts.core.operations import format_duration, parse_iso_time
from scripts.core.protocols import GitClient, ManifestStore, parse_markdown_state_text

# ============================================================================
# Stubs (Clean Architecture Protocol Implementations for In-Memory Testing)
# ============================================================================


class ManifestStoreStub:
    """In-memory stub implementing ManifestStore Protocol."""

    def __init__(self, versions: set[str]):
        self.versions = set(versions)
        self.written: list[str] = []

    def read_versions(self, root: Path) -> set[str]:
        return set(self.versions)

    def write_version(self, root: Path, version: str) -> None:
        self.versions = {version}
        self.written.append(version)


class GitClientStub:
    """In-memory stub implementing GitClient Protocol."""

    def __init__(self, responses: dict[tuple[str, ...], str | None]):
        self.responses = responses
        self.calls: list[list[str]] = []

    def run_git(self, args: list[str], cwd: Path | str, timeout: int = 20) -> str | None:
        self.calls.append(args)
        return self.responses.get(tuple(args))


# ============================================================================
# Test Cases
# ============================================================================


def test_semver_value_object() -> None:
    v = SemVer.parse("0.5.0")
    assert v.major == 0 and v.minor == 5 and v.patch == 0
    assert str(v) == "0.5.0"

    minor_bump = v.bump_minor()
    assert str(minor_bump) == "0.6.0"

    patch_bump = v.bump_patch()
    assert str(patch_bump) == "0.5.1"

    v_with_patch = SemVer.parse("1.2.3")
    assert str(v_with_patch.bump_minor()) == "1.3.0"
    assert str(v_with_patch.bump_patch()) == "1.2.4"

    # Invalid semver raises ValueError
    try:
        SemVer.parse("invalid")
        assert False, "Expected ValueError for invalid semver"
    except ValueError:
        pass

    try:
        SemVer.parse("1.2")
        assert False, "Expected ValueError for incomplete semver"
    except ValueError:
        pass

    print("ok   SemVer value object: parsing, bumping, validation verified")


def test_manifest_store_stub_bump() -> None:
    root = Path("/fake/root")

    # Happy path minor bump
    store = ManifestStoreStub({"0.5.0"})
    curr, new = bump_manifest_versions(store, root, "minor")
    assert str(curr) == "0.5.0"
    assert str(new) == "0.6.0"
    assert store.versions == {"0.6.0"}

    # Happy path patch bump
    store = ManifestStoreStub({"0.6.0"})
    curr, new = bump_manifest_versions(store, root, "patch")
    assert str(curr) == "0.6.0"
    assert str(new) == "0.6.1"
    assert store.versions == {"0.6.1"}

    # Disagreeing versions refused
    mismatch_store = ManifestStoreStub({"0.5.0", "0.5.1"})
    try:
        bump_manifest_versions(mismatch_store, root, "minor")
        assert False, "Expected ValueError on version mismatch"
    except ValueError as err:
        assert "disagree" in str(err)

    print("ok   ManifestStore Protocol stub: in-memory version bumping verified")


def test_research_state_parsing_and_progress() -> None:
    text = (
        "round: 4\n"
        "goals_total: 6\n"
        "goals_answered: 4\n"
        "findings: 41\n"
        "target_findings: 54\n"
        "frontier_done: 31\n"
        "frontier_pending: 12\n"
        "visited_pages: 183\n"
        "status: running\n"
    )
    raw = parse_markdown_state_text(text)
    state = ResearchState.from_dict(raw)
    assert not state.is_complete
    assert state.round == 4
    assert state.target_findings == 54

    metrics = calculate_progress(state)
    assert metrics.percentage == 75
    assert metrics.filled_bars == 15
    assert metrics.unfilled_bars == 5
    assert metrics.bar == "\u2588" * 15 + "\u2591" * 5
    assert "[Research 75% | round 4 | 41/54 findings |" in metrics.render()

    # Complete run renders 100%
    state.status = "complete"
    assert state.is_complete
    metrics_done = calculate_progress(state)
    assert metrics_done.percentage == 100
    assert metrics_done.filled_bars == 20
    assert metrics_done.bar == "\u2588" * 20

    print("ok   ResearchState and calculate_progress: metrics and visual bar verified")


def test_stats_compilation_and_formatting() -> None:
    run_dir = Path("/tmp/research/demo")
    state = ResearchState.from_dict({
        "round": "6",
        "goals_total": "6",
        "goals_answered": "6",
        "findings": "58",
        "dropped_findings": "12",
        "target_findings": "54",
        "frontier_done": "44",
        "frontier_pending": "0",
        "visited_pages": "240",
        "started_at": "2026-09-06T10:00:00+00:00",
        "finished_at": "2026-09-06T11:02:03+00:00",
        "status": "complete",
    })
    stats_data = {
        "slug": "demo",
        "started_at": "2026-09-06T10:00:00+00:00",
        "finished_at": "2026-09-06T11:02:03+00:00",
        "rounds": 6,
        "findings": 58,
        "dropped_findings": 12,
        "papers_cited": ["2509.13312", "2601.05960"],
        "papers_count": 7,
        "web_sources_count": 31,
        "visited_pages": 240,
        "goals_answered": 6,
        "goals_total": 6,
        "report": "research/demo/report.html",
    }

    compiled = compile_run_stats(slug="demo", run_dir=run_dir, state=state, stats=stats_data)
    assert compiled.is_complete
    assert compiled.status_tag == "Research done"
    assert compiled.elapsed == "1h 2m 3s"
    assert compiled.papers_count == 7

    rendered = format_run_stats(compiled)
    assert "[Research done] demo — 6/6 goals, 58 findings" in rendered
    assert "Time: 1h 2m 3s" in rendered
    assert "(in progress" not in rendered

    # In-progress run formatting
    in_progress_state = ResearchState.from_dict({
        "round": "2",
        "goals_total": "5",
        "goals_answered": "2",
        "findings": "15",
        "status": "running",
        "started_at": "2026-09-06T10:00:00+00:00",
    })
    now = datetime(2026, 9, 6, 10, 15, 30, tzinfo=timezone.utc)
    in_prog_compiled = compile_run_stats(slug="demo", run_dir=run_dir, state=in_progress_state, stats=None, now=now)
    assert not in_prog_compiled.is_complete
    assert in_prog_compiled.status_tag == "Research running"
    assert in_prog_compiled.elapsed == "15m 30s so far"
    in_prog_rendered = format_run_stats(in_prog_compiled)
    assert "(in progress — numbers are partial)" in in_prog_rendered

    print("ok   RunStats compilation and formatting: complete and partial verified")


def test_git_client_stub_update_check() -> None:
    # 1. Up to date
    stub_current = GitClientStub({
        ("rev-parse", "HEAD"): "abcdef1234567890",
        ("ls-remote", "origin", "refs/heads/main"): "abcdef1234567890\trefs/heads/main",
    })
    res = check_git_update(stub_current, Path("/fake/repo"))
    assert res.status == UpdateStatus.UP_TO_DATE
    assert "up to date" in res.message

    # 2. Update available
    stub_behind = GitClientStub({
        ("rev-parse", "HEAD"): "1111111234567890",
        ("ls-remote", "origin", "refs/heads/main"): "2222222234567890\trefs/heads/main",
    })
    res_behind = check_git_update(stub_behind, Path("/fake/repo"))
    assert res_behind.status == UpdateStatus.UPDATE_AVAILABLE
    assert "update available (1111111 → 2222222)" in res_behind.message
    # 2b. Ahead of remote (remote is ancestor of HEAD)
    stub_ahead = GitClientStub({
        ("rev-parse", "HEAD"): "3333333234567890",
        ("ls-remote", "origin", "refs/heads/main"): "2222222234567890\trefs/heads/main",
        ("merge-base", "--is-ancestor", "2222222234567890", "HEAD"): "",
    })
    res_ahead = check_git_update(stub_ahead, Path("/fake/repo"))
    assert res_ahead.status == UpdateStatus.UP_TO_DATE
    assert "up to date" in res_ahead.message

    # 3. Not a repo
    stub_not_repo = GitClientStub({
        ("rev-parse", "HEAD"): None,
    })
    res_not_repo = check_git_update(stub_not_repo, Path("/fake/not-repo"))
    assert res_not_repo.status == UpdateStatus.UNAVAILABLE
    assert "not a git checkout" in res_not_repo.message

    # 4. Remote offline
    stub_offline = GitClientStub({
        ("rev-parse", "HEAD"): "abcdef1234567890",
        ("ls-remote", "origin", "refs/heads/main"): None,
    })
    res_offline = check_git_update(stub_offline, Path("/fake/repo"))
    assert res_offline.status == UpdateStatus.UNAVAILABLE
    assert "cannot reach remote" in res_offline.message

    print("ok   GitClient Protocol stub: all update branches verified")


if __name__ == "__main__":
    test_semver_value_object()
    test_manifest_store_stub_bump()
    test_research_state_parsing_and_progress()
    test_stats_compilation_and_formatting()
    test_git_client_stub_update_check()
    print("\nAll Clean Architecture unit tests passed!")
