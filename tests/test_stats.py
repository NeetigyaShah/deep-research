"""Stats emission: complete, partial, and missing runs render correctly."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "stats.py"


def run_state(files):
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "research" / "demo"
        run_dir.mkdir(parents=True)
        for name, content in files.items():
            (run_dir / name).write_text(content, encoding="utf-8")
        out = subprocess.run(
            [sys.executable, str(SCRIPT), str(run_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return out


STATE = (
    "round: 6\ngoals_total: 6\ngoals_answered: 6\n"
    "findings: 58\ndropped_findings: 12\ntarget_findings: 54\n"
    "frontier_done: 44\nfrontier_pending: 0\nvisited_pages: 240\n"
    "papers_cited: 7\nstarted_at: 2026-09-06T10:00:00+00:00\n"
    'finished_at: 2026-09-06T11:02:03+00:00\nstatus: complete\n'
)
STATS = {
    "slug": "demo",
    "started_at": "2026-09-06T10:00:00+00:00",
    "finished_at": "2026-09-06T11:02:03+00:00",
    "elapsed": "1h 2m 3s",
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

done = run_state({"state.md": STATE, "stats.json": json.dumps(STATS)})
assert done.returncode == 0, done.stderr
assert "[Research done] demo — 6/6 goals, 58 findings" in done.stdout, done.stdout
assert "Time: 1h 2m 3s (2026-09-06T10:00:00+00:00 → 2026-09-06T11:02:03+00:00 UTC)" in done.stdout, done.stdout
assert "Papers cited: 7 | Web sources: 31" in done.stdout, done.stdout
assert "Report: research/demo/report.html" in done.stdout, done.stdout
print("ok   finished run renders full end log")

partial = run_state(
    {
        "state.md": (
            "round: 2\ngoals_total: 5\ngoals_answered: 1\n"
            "findings: 9\ntarget_findings: 15\nfrontier_done: 12\n"
            "frontier_pending: 18\nvisited_pages: 40\npapers_cited: 0\n"
            "started_at: 2026-09-06T10:00:00+00:00\n"
            'finished_at: ""\nstatus: running\n'
        )
    }
)
assert partial.returncode == 0, partial.stderr
assert "[Research running] demo" in partial.stdout, partial.stdout
assert "(in progress — numbers are partial)" in partial.stdout, partial.stdout
print("ok   unfinished run derives partial log from state.md")

with tempfile.TemporaryDirectory() as tmp:
    missing = subprocess.run(
        [sys.executable, str(SCRIPT), str(Path(tmp) / "research" / "nope")],
        capture_output=True,
        text=True,
        timeout=60,
    )
assert missing.returncode == 2, missing.stdout
assert "no run found" in missing.stdout, missing.stdout
print("ok   missing run exits 2 with guidance")

print("\nall stats tests passed")
