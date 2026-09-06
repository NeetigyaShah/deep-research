"""Bump the plugin version across all manifests in lockstep.

Usage: python scripts/bump_version.py [--part minor|patch] [--root DIR]
Defaults to minor (0.x.0 -> 0.x+1.0); patch does 0.0.x -> 0.0.x+1.
Prints the new version. check_repo.py enforces the lockstep in CI.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.core import SemVer, bump_manifest_versions
from scripts.core.protocols import FileManifestStore

MANIFESTS = list(FileManifestStore.DEFAULT_MANIFESTS)


def bump(version: str, part: str) -> str:
    """Retained for backwards compatibility with tests and callers."""
    ver = SemVer.parse(version)
    return str(ver.bump_patch() if part == "patch" else ver.bump_minor())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", default="minor", choices=("minor", "patch"))
    parser.add_argument("--root", default=".")
    opts = parser.parse_args()

    store = FileManifestStore()
    try:
        _, new_ver = bump_manifest_versions(store=store, root=Path(opts.root), part=opts.part)
    except ValueError as err:
        print(str(err), file=sys.stderr)
        return 1

    print(str(new_ver))
    return 0


if __name__ == "__main__":
    sys.exit(main())
