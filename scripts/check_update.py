"""Check whether this deep-research checkout is behind its upstream branch.

Usage: python scripts/check_update.py [path] [--remote origin] [--branch main]
Works anywhere git exists, on any harness; never wakes the agent.
Exit 0 up to date, 1 update available, 2 cannot check (not a repo, offline).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.core import check_git_update
from scripts.core.protocols import SubprocessGitClient


def git(args, cwd, timeout=20):
    """Retained for backwards compatibility with tests and callers."""
    client = SubprocessGitClient()
    return client.run_git(args, cwd, timeout=timeout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    opts = parser.parse_args()

    client = SubprocessGitClient()
    result = check_git_update(git=client, path=opts.path, remote=opts.remote, branch=opts.branch)
    print(result.message)
    return int(result.status)


if __name__ == "__main__":
    sys.exit(main())
