"""Domain models and value objects for deep-research tooling."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Mapping


@dataclass(frozen=True)
class SemVer:
    """Semantic version Value Object."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version_str: str) -> SemVer:
        parts = version_str.strip().split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid semantic version: '{version_str}'")
        try:
            major, minor, patch = (int(p) for p in parts)
        except ValueError as err:
            raise ValueError(f"Non-integer component in version '{version_str}': {err}") from err
        if major < 0 or minor < 0 or patch < 0:
            raise ValueError(f"Version components must be non-negative: '{version_str}'")
        return cls(major=major, minor=minor, patch=patch)

    def bump_minor(self) -> SemVer:
        return SemVer(major=self.major, minor=self.minor + 1, patch=0)

    def bump_patch(self) -> SemVer:
        return SemVer(major=self.major, minor=self.minor, patch=self.patch + 1)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass
class ResearchState:
    """Domain representation of research/<slug>/state.md."""

    round: int = 0
    target_findings: int = 1
    findings: int = 0
    dropped_findings: int = 0
    frontier_done: int = 0
    frontier_pending: int = 0
    visited_pages: int = 0
    goals_answered: int = 0
    goals_total: int = 0
    status: str = "running"
    started_at: str = ""
    finished_at: str = ""
    raw_values: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ResearchState:
        def _int(key: str, default: int = 0) -> int:
            val = data.get(key)
            if val is None:
                return default
            try:
                return int(val)
            except (ValueError, TypeError):
                return default

        target = _int("target_findings", 1)
        if target <= 0:
            target = 1

        raw = {str(k): str(v) for k, v in data.items()}
        return cls(
            round=_int("round", 0),
            target_findings=target,
            findings=_int("findings", 0),
            dropped_findings=_int("dropped_findings", 0),
            frontier_done=_int("frontier_done", 0),
            frontier_pending=_int("frontier_pending", 0),
            visited_pages=_int("visited_pages", 0),
            goals_answered=_int("goals_answered", 0),
            goals_total=_int("goals_total", 0),
            status=str(data.get("status", "running")),
            started_at=str(data.get("started_at", "")),
            finished_at=str(data.get("finished_at", "")),
            raw_values=raw,
        )

    @property
    def is_complete(self) -> bool:
        return self.status == "complete"


@dataclass(frozen=True)
class ProgressMetrics:
    """Value object capturing research progress calculations."""

    percentage: int
    filled_bars: int
    unfilled_bars: int
    bar: str
    round: int | str
    findings: int | str
    target_findings: int | str
    goals_answered: int | str
    goals_total: int | str
    frontier_pending: int | str
    visited_pages: int | str

    def render(self) -> str:
        return (
            f"[Research {self.percentage}% | round {self.round} | "
            f"{self.findings}/{self.target_findings} findings | "
            f"{self.goals_answered}/{self.goals_total} goals | "
            f"frontier {self.frontier_pending} | {self.visited_pages} pages] {self.bar}"
        )


@dataclass(frozen=True)
class RunStats:
    """Domain model for a completed or in-progress research run."""

    slug: str
    is_complete: bool
    status_tag: str
    elapsed: str
    time_span: str
    rounds: int | str
    pages: int | str
    papers_count: int | str
    web_sources_count: int | str
    findings: int | str
    dropped_findings: int | str
    goals_answered: int | str
    goals_total: int | str
    report_path: str


class UpdateStatus(IntEnum):
    """Exit codes for check_update CLI."""

    UP_TO_DATE = 0
    UPDATE_AVAILABLE = 1
    UNAVAILABLE = 2


@dataclass(frozen=True)
class UpdateResult:
    """Value object describing update status."""

    status: UpdateStatus
    message: str
    local_sha: str = ""
    remote_sha: str = ""
