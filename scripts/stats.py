"""Print the end-of-run log for a deep-research run.

Usage: python scripts/stats.py research/<slug>
Reads stats.json when the run finished, otherwise derives partial numbers
from state.md. Works in any terminal on any harness; never wakes the agent.
Exit 0 ok, 2 when no run is found.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_state(path: Path) -> dict:
    vals: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            vals[key.strip()] = value.strip()
    return vals


def parse_time(value: str):
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment


def fmt_elapsed(seconds: float) -> str:
    total = max(int(seconds), 0)
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


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

    state = parse_state(state_path) if state_path.exists() else {}
    stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else {}
    slug = run_dir.name
    complete = state.get("status") == "complete" or bool(stats)

    started = parse_time(stats.get("started_at") or state.get("started_at", ""))
    finished = parse_time(stats.get("finished_at") or state.get("finished_at", ""))
    if started and finished:
        elapsed = fmt_elapsed((finished - started).total_seconds())
        span = f"{state.get('started_at', stats.get('started_at', '?'))} → {state.get('finished_at', stats.get('finished_at', '?'))} UTC"
    elif started:
        elapsed = fmt_elapsed((datetime.now(timezone.utc) - started).total_seconds()) + " so far"
        span = f"{state.get('started_at', stats.get('started_at', '?'))} → … UTC"
    else:
        elapsed, span = "?", "?"

    kept = stats.get("kept_claims", state.get("kept_claims", "?"))
    dropped = stats.get("dropped_claims", state.get("dropped_claims", "?"))
    papers = stats.get("papers_cited", [])
    papers_count = stats.get("papers_count", len(papers) if isinstance(papers, list) else state.get("papers_cited", "?"))
    web = stats.get("web_sources_count", "?")
    rounds = stats.get("rounds", state.get("round", "?"))
    pages = stats.get("visited_pages", state.get("visited_pages", "?"))
    covered = stats.get("must_answer_covered", state.get("must_answer_covered", "?"))
    total = stats.get("must_answer_total", state.get("must_answer_total", "?"))
    report = stats.get("report", str(run_dir / "report.md"))

    tag = "Research done" if complete else "Research running"
    print(f"[{tag}] {slug} — {covered}/{total} questions, {kept} kept claims")
    print(f"  Time: {elapsed} ({span}) | Rounds: {rounds} | Pages: {pages}")
    print(f"  Papers cited: {papers_count} | Web sources: {web} | Dropped: {dropped}")
    print(f"  Report: {report}")
    if not complete:
        print("  (in progress — numbers are partial)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
