"""Bump the plugin version across all manifests in lockstep.

Usage: python scripts/bump_version.py [--part minor|patch] [--root DIR]
Defaults to minor (0.x.0 -> 0.x+1.0); patch does 0.0.x -> 0.0.x+1.
Prints the new version. check_repo.py enforces the lockstep in CI.
"""

import argparse
import json
import sys
from pathlib import Path

MANIFESTS = [
    Path("package.json"),
    Path(".claude-plugin/plugin.json"),
    Path(".codex-plugin/plugin.json"),
]


def bump(version: str, part: str) -> str:
    major, minor, patch = (int(p) for p in version.split("."))
    if part == "patch":
        patch += 1
    else:
        minor += 1
        patch = 0
    return f"{major}.{minor}.{patch}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", default="minor", choices=("minor", "patch"))
    parser.add_argument("--root", default=".")
    opts = parser.parse_args()

    root = Path(opts.root)
    versions = set()
    for manifest in MANIFESTS:
        data = json.loads((root / manifest).read_text(encoding="utf-8"))
        versions.add(data.get("version"))
    if len(versions) != 1 or None in versions:
        print(f"refusing: manifest versions disagree ({versions})", file=sys.stderr)
        return 1

    new_version = bump(versions.pop(), opts.part)
    for manifest in MANIFESTS:
        path = root / manifest
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = new_version
        path.write_text(json.dumps(data), encoding="utf-8")
    print(new_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
