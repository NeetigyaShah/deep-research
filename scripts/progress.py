"""Print a deep-research progress bar from research/<slug>/state.md.

Usage: python scripts/progress.py research/<slug>
Works anywhere Python exists; reads only state.md, never wakes the agent.
"""

import sys
from pathlib import Path


def parse_state(path: Path) -> dict:
    vals: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            vals[key.strip()] = value.strip()
    return vals


def main() -> None:
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    state = parse_state(run_dir / "state.md")

    def num(key: str) -> int:
        try:
            return int(state.get(key, 0))
        except ValueError:
            return 0

    kept = num("kept_claims")
    target = max(num("target_claims"), 1)
    done = num("frontier_done")
    pending = num("frontier_pending")

    if state.get("status") == "complete":
        pct = 100
    else:
        coverage = min(kept / target, 1.0)
        drain = done / max(done + pending, 1)
        pct = min(99, round(100 * (0.7 * coverage + 0.3 * drain)))

    filled = round(pct / 5)
    bar = "\u2588" * filled + "\u2591" * (20 - filled)
    print(
        f"[Research {pct}% | round {state.get('round', '?')} | "
        f"{kept}/{state.get('target_claims', '?')} claims | "
        f"{state.get('must_answer_covered', '?')}/{state.get('must_answer_total', '?')} questions | "
        f"frontier {pending} | {state.get('visited_pages', '?')} pages] {bar}"
    )


if __name__ == "__main__":
    main()
