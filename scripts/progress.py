"""Print a deep-research progress bar from research/<slug>/state.md.

Usage: python scripts/progress.py research/<slug>
Works anywhere Python exists; reads only state.md, never wakes the agent.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.core import calculate_progress
from scripts.core.protocols import FileSystemStateReader, parse_markdown_state_text


def parse_state(path: Path) -> dict:
    """Retained for backwards compatibility with tests and callers."""
    if not path.exists():
        return {}
    return parse_markdown_state_text(path.read_text(encoding="utf-8"))


def main() -> None:
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    reader = FileSystemStateReader()
    state = reader.read_state(run_dir / "state.md")
    metrics = calculate_progress(state)
    print(metrics.render())


if __name__ == "__main__":
    main()
