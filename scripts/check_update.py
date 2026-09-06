"""Check whether this deep-research checkout is behind its upstream branch.

Usage: python scripts/check_update.py [path] [--remote origin] [--branch main]
Works anywhere git exists, on any harness; never wakes the agent.
Exit 0 up to date, 1 update available, 2 cannot check (not a repo, offline).
"""

import argparse
import subprocess
import sys


def git(args, cwd, timeout=20):
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    opts = parser.parse_args()

    local = git(["rev-parse", "HEAD"], opts.path)
    if not local:
        print(f"deep-research: cannot check updates in {opts.path} (not a git checkout?)")
        return 2
    remote = git(["ls-remote", opts.remote, f"refs/heads/{opts.branch}"], opts.path)
    if not remote:
        print("deep-research: cannot reach remote — staying silent (offline?)")
        return 2
    remote_sha = remote.split()[0]
    if remote_sha == local:
        print(f"deep-research: up to date ({local[:7]})")
        return 0
    print(f"deep-research: update available ({local[:7]} → {remote_sha[:7]}) — git pull in {opts.path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
