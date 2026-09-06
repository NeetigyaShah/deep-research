"""Print the end-of-run log for a deep-research run.

Usage: python scripts/stats.py research/<slug>
Reads stats.json when the run finished, otherwise derives partial numbers
from state.md. Works in any terminal on any harness; never wakes the agent.
Exit 0 ok, 2 when no run is found.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.core import compile_run_stats, format_run_stats
from scripts.core.operations import format_duration, parse_iso_time
from scripts.core.protocols import FileSystemStateReader, parse_markdown_state_text


def parse_state(path: Path) -> dict:
    """Retained for backwards compatibility with tests and callers."""
    if not path.exists():
        return {}
    return parse_markdown_state_text(path.read_text(encoding="utf-8"))


def parse_time(value: str) -> Optional[datetime]:
    """Retained for backwards compatibility with tests and callers."""
    return parse_iso_time(value)


def fmt_elapsed(seconds: float) -> str:
    """Retained for backwards compatibility with tests and callers."""
    return format_duration(seconds)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python scripts/stats.py research/<slug>")
        return 2
    run_dir = Path(sys.argv[1])
    state_path = run_dir / "state.md"
    stats_path = run_dir / "stats.json"
    if not state_path.exists() and not stats_path.exists():
        print(f"deep-research: no run found at {run_dir}")
        return 2

    reader = FileSystemStateReader()
    state = reader.read_state(state_path) if state_path.exists() else None
    stats_data = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else None

    compiled = compile_run_stats(slug=run_dir.name, run_dir=run_dir, state=state, stats=stats_data)
    print(format_run_stats(compiled))
    return 0


if __name__ == "__main__":
    sys.exit(main())
