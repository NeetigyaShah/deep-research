"""Version bumps move all manifests together and reset patch on minor."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "bump_version.py"
FILES = ["package.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"]


def run_bump(tmp, part):
    for name in FILES:
        src = ROOT / name
        dst = Path(tmp) / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--part", part, "--root", str(tmp)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert out.returncode == 0, out.stderr
    versions = set()
    for name in FILES:
        data = json.loads((Path(tmp) / name).read_text(encoding="utf-8"))
        versions.add(data["version"])
    return out.stdout.strip(), versions


with tempfile.TemporaryDirectory() as tmp:
    new_version, versions = run_bump(tmp, "minor")
    assert len(versions) == 1, versions
    assert new_version.endswith(".0"), new_version
    print(f"ok   minor bump moves together and resets patch ({new_version})")

with tempfile.TemporaryDirectory() as tmp:
    new_version, versions = run_bump(tmp, "patch")
    assert len(versions) == 1, versions
    major, minor, patch = (int(p) for p in new_version.split("."))
    assert patch > 0, new_version
    print(f"ok   patch bump moves together ({new_version})")

print("\nall version tests passed")
