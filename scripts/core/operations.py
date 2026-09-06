"""Pure business operations for deep-research tooling.

Decoupled from CLI arguments and concrete storage backends:
- All operations operate on Domain Models and Protocols.
- Return structured Value Objects or domain results.
- Fully testable via in-memory stubs without disk I/O or subprocesses.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

from .models import (
    ProgressMetrics,
    ResearchState,
    RunStats,
    SemVer,
    UpdateResult,
    UpdateStatus,
)
from .protocols import GitClient, ManifestStore


def calculate_progress(state: ResearchState) -> ProgressMetrics:
    """Compute progress metrics and visual progress bar from ResearchState."""
    kept = state.kept_claims
    target = max(state.target_claims, 1)
    done = state.frontier_done
    pending = state.frontier_pending

    if state.is_complete:
        pct = 100
    else:
        coverage = min(kept / target, 1.0)
        drain = done / max(done + pending, 1)
        pct = min(99, round(100 * (0.7 * coverage + 0.3 * drain)))

    filled = round(pct / 5)
    unfilled = 20 - filled
    bar = "\u2588" * filled + "\u2591" * unfilled

    raw = state.raw_values
    return ProgressMetrics(
        percentage=pct,
        filled_bars=filled,
        unfilled_bars=unfilled,
        bar=bar,
        round=raw.get("round", state.round),
        kept_claims=kept,
        target_claims=raw.get("target_claims", state.target_claims),
        must_answer_covered=raw.get("must_answer_covered", state.must_answer_covered),
        must_answer_total=raw.get("must_answer_total", state.must_answer_total),
        frontier_pending=pending,
        visited_pages=raw.get("visited_pages", state.visited_pages),
    )


def parse_iso_time(value: str) -> Optional[datetime]:
    """Parse ISO timestamp with UTC fallback."""
    if not value:
        return None
    try:
        moment = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    total = max(int(seconds), 0)
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def compile_run_stats(
    slug: str,
    run_dir: Path,
    state: Optional[ResearchState] = None,
    stats: Optional[Mapping[str, Any]] = None,
    now: Optional[datetime] = None,
) -> RunStats:
    """Compile RunStats domain model from state and stats representations."""
    state_raw = state.raw_values if state else {}
    stats_dict = dict(stats) if stats else {}
    complete = (state and state.is_complete) or bool(stats_dict)

    started_str = stats_dict.get("started_at") or state_raw.get("started_at", "")
    finished_str = stats_dict.get("finished_at") or state_raw.get("finished_at", "")
    started = parse_iso_time(started_str)
    finished = parse_iso_time(finished_str)

    current_time = now or datetime.now(timezone.utc)
    if started and finished:
        elapsed = format_duration((finished - started).total_seconds())
        span = f"{state_raw.get('started_at', stats_dict.get('started_at', '?'))} → {state_raw.get('finished_at', stats_dict.get('finished_at', '?'))} UTC"
    elif started:
        elapsed = format_duration((current_time - started).total_seconds()) + " so far"
        span = f"{state_raw.get('started_at', stats_dict.get('started_at', '?'))} → … UTC"
    else:
        elapsed, span = "?", "?"

    kept = stats_dict.get("kept_claims", state_raw.get("kept_claims", "?"))
    dropped = stats_dict.get("dropped_claims", state_raw.get("dropped_claims", "?"))

    papers = stats_dict.get("papers_cited", [])
    if isinstance(papers, list):
        default_papers = len(papers)
    else:
        default_papers = state_raw.get("papers_cited", "?")
    papers_count = stats_dict.get("papers_count", default_papers)

    web = stats_dict.get("web_sources_count", "?")
    rounds = stats_dict.get("rounds", state_raw.get("round", "?"))
    pages = stats_dict.get("visited_pages", state_raw.get("visited_pages", "?"))
    covered = stats_dict.get("must_answer_covered", state_raw.get("must_answer_covered", "?"))
    total = stats_dict.get("must_answer_total", state_raw.get("must_answer_total", "?"))
    report = stats_dict.get("report", str(run_dir / "report.md"))

    tag = "Research done" if complete else "Research running"
    return RunStats(
        slug=slug,
        is_complete=complete,
        status_tag=tag,
        elapsed=elapsed,
        time_span=span,
        rounds=rounds,
        pages=pages,
        papers_count=papers_count,
        web_sources_count=web,
        kept_claims=kept,
        dropped_claims=dropped,
        must_answer_covered=covered,
        must_answer_total=total,
        report_path=report,
    )


def format_run_stats(stats: RunStats) -> str:
    """Format RunStats into the standard terminal block."""
    lines = [
        f"[{stats.status_tag}] {stats.slug} — {stats.must_answer_covered}/{stats.must_answer_total} questions, {stats.kept_claims} kept claims",
        f"  Time: {stats.elapsed} ({stats.time_span}) | Rounds: {stats.rounds} | Pages: {stats.pages}",
        f"  Papers cited: {stats.papers_count} | Web sources: {stats.web_sources_count} | Dropped: {stats.dropped_claims}",
        f"  Report: {stats.report_path}",
    ]
    if not stats.is_complete:
        lines.append("  (in progress — numbers are partial)")
    return "\n".join(lines)


def bump_manifest_versions(store: ManifestStore, root: Path, part: str = "minor") -> tuple[SemVer, SemVer]:
    """Verify lockstep versions across manifests, bump the chosen part, and persist."""
    versions = store.read_versions(root)
    if len(versions) != 1:
        raise ValueError(f"refusing: manifest versions disagree ({versions})")

    current = SemVer.parse(next(iter(versions)))
    if part == "patch":
        new_ver = current.bump_patch()
    elif part == "minor":
        new_ver = current.bump_minor()
    else:
        raise ValueError(f"Unknown part to bump: '{part}', expected 'minor' or 'patch'")

    store.write_version(root, str(new_ver))
    return current, new_ver


def check_git_update(
    git: GitClient,
    path: Path | str,
    remote: str = "origin",
    branch: str = "main",
) -> UpdateResult:
    """Check whether local git checkout is behind upstream branch."""
    local = git.run_git(["rev-parse", "HEAD"], path)
    if not local:
        return UpdateResult(
            status=UpdateStatus.UNAVAILABLE,
            message=f"deep-research: cannot check updates in {path} (not a git checkout?)",
        )

    remote_output = git.run_git(["ls-remote", remote, f"refs/heads/{branch}"], path)
    if not remote_output:
        return UpdateResult(
            status=UpdateStatus.UNAVAILABLE,
            message="deep-research: cannot reach remote — staying silent (offline?)",
        )

    remote_sha = remote_output.split()[0]
    if remote_sha == local:
        return UpdateResult(
            status=UpdateStatus.UP_TO_DATE,
            local_sha=local,
            remote_sha=remote_sha,
            message=f"deep-research: up to date ({local[:7]})",
        )

    # If remote_sha is already an ancestor of HEAD, local has unpushed commits ahead of upstream
    is_ancestor = git.run_git(["merge-base", "--is-ancestor", remote_sha, "HEAD"], path)
    if is_ancestor is not None:
        return UpdateResult(
            status=UpdateStatus.UP_TO_DATE,
            local_sha=local,
            remote_sha=remote_sha,
            message=f"deep-research: up to date ({local[:7]})",
        )

    return UpdateResult(
        status=UpdateStatus.UPDATE_AVAILABLE,
        local_sha=local,
        remote_sha=remote_sha,
        message=f"deep-research: update available ({local[:7]} → {remote_sha[:7]}) — git pull in {path}",
    )
