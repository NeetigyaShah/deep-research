"""Progress-bar math: mid-run, complete, and fresh states render correctly."""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "progress.py"


def run(state_text):
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "research" / "demo"
        run_dir.mkdir(parents=True)
        (run_dir / "state.md").write_text(state_text, encoding="utf-8")
        out = subprocess.run(
            [sys.executable, str(SCRIPT), str(run_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert out.returncode == 0, out.stderr
        return out.stdout.strip()


mid = run(
    "round: 4\ngoals_total: 6\ngoals_answered: 4\n"
    "findings: 41\ntarget_findings: 54\nfrontier_done: 31\n"
    "frontier_pending: 12\nvisited_pages: 183\nstatus: running\n"
)
assert mid.startswith("[Research 75% | round 4 | 41/54 findings |"), mid
assert mid.endswith("\u2588" * 15 + "\u2591" * 5), mid
print("ok   mid-run renders 75% with 15/20 bar")

done = run(
    "round: 6\ngoals_total: 6\ngoals_answered: 6\n"
    "findings: 58\ntarget_findings: 54\nfrontier_done: 44\n"
    "frontier_pending: 0\nvisited_pages: 240\nstatus: complete\n"
)
assert done.startswith("[Research 100%"), done
assert done.endswith("\u2588" * 20), done
print("ok   complete renders 100% with full bar")

fresh = run(
    "round: 0\ngoals_total: 5\ngoals_answered: 0\n"
    "findings: 0\ntarget_findings: 15\nfrontier_done: 0\n"
    "frontier_pending: 20\nvisited_pages: 0\nstatus: running\n"
)
assert fresh.startswith("[Research 0%"), fresh
print("ok   fresh run renders 0%")

over = run(
    "round: 9\ngoals_total: 4\ngoals_answered: 4\n"
    "findings: 200\ntarget_findings: 12\nfrontier_done: 199\n"
    "frontier_pending: 1\nvisited_pages: 500\nstatus: running\n"
)
assert over.startswith("[Research 99%"), over
print("ok   running never renders 100% (caps at 99)")
print("\nall progress tests passed")
