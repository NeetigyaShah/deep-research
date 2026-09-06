"""Protocols and concrete storage/process adapters for deep-research tooling.

Follows the Clean Architecture DataInterface pattern:
- Protocols define structural subtyping for I/O and external systems.
- Concrete adapters implement protocols for disk and subprocess execution.
- Stubs implement protocols in-memory for zero-I/O unit testing.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Mapping, Protocol

from .models import ResearchState


class StateReader(Protocol):
    """Protocol for reading research state."""

    def read_state(self, path: Path) -> ResearchState:
        ...


class ManifestStore(Protocol):
    """Protocol for reading and writing plugin manifest versions."""

    def read_versions(self, root: Path) -> set[str]:
        ...

    def write_version(self, root: Path, version: str) -> None:
        ...


class GitClient(Protocol):
    """Protocol for interacting with Git."""

    def run_git(self, args: list[str], cwd: Path | str, timeout: int = 20) -> str | None:
        ...


def parse_markdown_state_text(text: str) -> dict[str, str]:
    """Pure helper to parse key: value lines from markdown state files."""
    vals: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            vals[key.strip()] = value.strip()
    return vals


class FileSystemStateReader:
    """Concrete filesystem implementation of StateReader."""

    def read_state(self, path: Path) -> ResearchState:
        if not path.exists():
            return ResearchState()
        text = path.read_text(encoding="utf-8")
        raw_dict = parse_markdown_state_text(text)
        return ResearchState.from_dict(raw_dict)


class FileManifestStore:
    """Concrete implementation of ManifestStore operating on JSON files."""

    DEFAULT_MANIFESTS = (
        Path("package.json"),
        Path(".claude-plugin/plugin.json"),
        Path(".codex-plugin/plugin.json"),
    )

    def __init__(self, manifests: tuple[Path, ...] = DEFAULT_MANIFESTS):
        self.manifests = manifests

    def read_versions(self, root: Path) -> set[str]:
        versions: set[str] = set()
        for manifest in self.manifests:
            path = root / manifest
            data = json.loads(path.read_text(encoding="utf-8"))
            version = data.get("version")
            if version is not None:
                versions.add(str(version))
        return versions

    def write_version(self, root: Path, version: str) -> None:
        for manifest in self.manifests:
            path = root / manifest
            data = json.loads(path.read_text(encoding="utf-8"))
            data["version"] = version
            path.write_text(json.dumps(data), encoding="utf-8")


class SubprocessGitClient:
    """Concrete implementation of GitClient using subprocess."""

    def run_git(self, args: list[str], cwd: Path | str, timeout: int = 20) -> str | None:
        try:
            proc = subprocess.run(
                ["git", *args],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        if proc.returncode != 0:
            return None
        return proc.stdout.strip()
