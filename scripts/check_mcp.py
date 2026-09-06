"""Check that all required MCP servers and runtimes are installed and configured.

Usage: python scripts/check_mcp.py [cwd]
Exits 0 if all 4 MCP servers (arxiv, ddg-search, gutenberg, openalex) and their runtimes
(uvx, npx) are available. Exits 1 if any are missing, printing user installation guidance.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import List, Set

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED_SERVERS = ("arxiv", "ddg-search", "gutenberg", "openalex")


def find_configured_servers(cwd: Path) -> Set[str]:
    """Scan potential MCP configuration locations for declared servers."""
    found: Set[str] = set()
    candidate_paths = [
        cwd / ".omp" / "mcp.json",
        cwd / ".mcp.json",
        cwd / "mcp.json",
        cwd / ".codex-mcp.json",
        cwd / "integrations" / "opencode.json",
        cwd / "integrations" / "cursor-mcp.json",
        Path.home() / ".omp" / "agent" / "config.yml",
        Path.home() / ".claude.json",
    ]

    for p in candidate_paths:
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8")
            if p.suffix == ".json":
                data = json.loads(text)
                # Standard mcpServers structure
                servers = data.get("mcpServers") or data.get("mcp", {}).get("servers") or {}
                for s in REQUIRED_SERVERS:
                    if s in servers:
                        found.add(s)
            elif p.suffix in (".yml", ".yaml"):
                for s in REQUIRED_SERVERS:
                    if s in text:
                        found.add(s)
        except Exception:
            continue
    return found


def check_mcp(cwd: Path | str = ".") -> tuple[bool, str]:
    """Check runtimes and server declarations. Return (success, message)."""
    cwd_path = Path(cwd).resolve()
    missing: List[str] = []

    configured = find_configured_servers(cwd_path)
    if not configured and cwd_path != ROOT:
        configured = find_configured_servers(ROOT)
    if not configured:
        configured = find_configured_servers(Path.home())
    # Check CLI runtimes
    has_uvx = shutil.which("uvx") is not None
    has_npx = shutil.which("npx") is not None

    if not has_uvx:
        missing.append("uvx (required for 'arxiv' and 'ddg-search' MCP servers — install uv from https://astral.sh/uv)")
    if not has_npx:
        missing.append("npx (required for 'gutenberg' and 'openalex' MCP servers — install Node.js from https://nodejs.org)")

    configured = find_configured_servers(cwd_path)
    # Also check plugin directory itself if running from repo
    if cwd_path != ROOT:
        configured.update(find_configured_servers(ROOT))

    missing_servers = [s for s in REQUIRED_SERVERS if s not in configured]
    if missing_servers:
        missing.append(f"MCP server configurations for: {', '.join(missing_servers)}")

    if missing:
        msg = (
            "deep-research: Missing required MCP setup:\n  - "
            + "\n  - ".join(missing)
            + "\n\nFirst install this, only then will deep-research work."
        )
        return False, msg

    return True, f"deep-research: all 4 MCP servers verified ({', '.join(REQUIRED_SERVERS)})."


def main() -> int:
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    ok, msg = check_mcp(target_dir)
    if ok:
        print(msg)
        return 0
    print(msg, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
