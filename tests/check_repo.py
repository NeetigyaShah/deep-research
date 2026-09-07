"""Repo checks: manifests parse, versions agree, skill/agent/command frontmatter valid."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list = []


def check(condition, message):
    print(("ok  " if condition else "FAIL") + " " + message)
    if not condition:
        FAILURES.append(message)


def load_json(path):
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except Exception as exc:
        check(False, f"{path} parses as JSON ({exc})")
        return None


def frontmatter(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


manifests = [
    "package.json",
    ".mcp.json",
    "mcp.json",
    ".codex-mcp.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
    "integrations/opencode.json",
    "integrations/cursor-mcp.json",
    "integrations/antigravity-mcp.json",
]
parsed = {}
for name in manifests:
    data = load_json(name)
    if data is not None:
        check(True, f"{name} parses as JSON")
        parsed[name] = data

for name in ("package.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
    data = parsed.get(name, {})
    check(bool(data.get("name")), f"{name} has a name")
    check(bool(data.get("description")), f"{name} has a description")

versions = {
    parsed.get("package.json", {}).get("version"),
    parsed.get(".claude-plugin/plugin.json", {}).get("version"),
    parsed.get(".codex-plugin/plugin.json", {}).get("version"),
}
check(len(versions) == 1 and None not in versions, f"versions agree across manifests ({versions})")

for server in ("arxiv", "ddg-search", "gutenberg", "openalex"):
    for name in (".mcp.json", "mcp.json"):
        entry = parsed.get(name, {}).get("mcpServers", {}).get(server, {})
        check(bool(entry.get("command")) and bool(entry.get("args")), f"{name} defines {server} server")
    flat = parsed.get(".codex-mcp.json", {}).get(server, {})
    check(bool(flat.get("command")) and bool(flat.get("args")), f".codex-mcp.json defines {server} server")
    oco = parsed.get("integrations/opencode.json", {}).get("mcp", {}).get("servers", {}).get(server, {})
    check(oco.get("type") == "local" and bool(oco.get("command")), f"integrations/opencode.json defines {server} server")
    cur = parsed.get("integrations/cursor-mcp.json", {}).get("mcpServers", {}).get(server, {})
    check(bool(cur.get("command")) and bool(cur.get("args")), f"integrations/cursor-mcp.json defines {server} server")
    ag = parsed.get("integrations/antigravity-mcp.json", {}).get("mcpServers", {}).get(server, {})
    check(bool(ag.get("command")) and bool(ag.get("args")), f"integrations/antigravity-mcp.json defines {server} server")

for sk in ("deep-research", "followup"):
    fm = frontmatter(f"skills/{sk}/SKILL.md")
    check(bool(fm and fm.get("name") and fm.get("description")), f"skill {sk} has name + description frontmatter")

for agent in ("research-planner", "web-diver", "literature-diver", "books-diver", "citation-checker"):
    fm = frontmatter(f"agents/{agent}.md")
    check(bool(fm and fm.get("name") and fm.get("description")), f"agent {agent} has name + description frontmatter")

for cmd_file in sorted((ROOT / "commands").glob("*.md")):
    cmd = frontmatter(f"commands/{cmd_file.name}")
    check(bool(cmd and cmd.get("description")), f"command {cmd_file.name} has description frontmatter")

for asset in (
    "scripts/progress.py",
    "scripts/stats.py",
    "scripts/check_update.py",
    "scripts/check_mcp.py",
    "scripts/core/__init__.py",
    "scripts/core/models.py",
    "scripts/core/protocols.py",
    "scripts/core/operations.py",
    "scripts/core/document.py",
    "scripts/ingest_doc.py",
    "tests/test_core.py",
    "tests/test_document.py",
    "commands/followup.md",
    "skills/followup/SKILL.md",
):
    check((ROOT / asset).exists(), f"{asset} exists")

skill_text = (ROOT / "skills/deep-research/SKILL.md").read_text(encoding="utf-8")
check("MCP Gate Check" in skill_text, "skill defines Phase 0 MCP gate check")
check("built-in `web_search`" in skill_text or "internet search tool" in skill_text, "skill defines internet search fallback")
check("stats.json" in skill_text, "skill defines the stats.json end log")
check("Phase 7" in skill_text, "skill defines the Phase 7 follow-up loop")
check("plan-attack" in skill_text, "skill defines the observer plan review")
checker_text = (ROOT / "agents/citation-checker.md").read_text(encoding="utf-8")
check("Plan-attack mode" in checker_text and "plan-review.md" in checker_text, "checker defines plan-attack mode")
check("peer verifier" in checker_text and "Textual Grounding" in checker_text, "checker defines cross-diver peer verification")
check("Cross-Diver Peer Validation" in skill_text, "skill defines Phase 4 cross-diver peer validation")
check("ledger ID" in skill_text and "backstop" in skill_text, "skill defines provenance-first synthesis with gate backstop")
check("Split-debug" in skill_text, "skill defines the split-debug rule")
check("decisions.md" in skill_text, "skill defines auto-captured decisions")
planner_text = (ROOT / "agents/research-planner.md").read_text(encoding="utf-8")
check("self_score" in planner_text, "planner self-scores its packs")
readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
check("token audit" in readme_text, "readme carries the MCP checklist")
check("turns_this_round" in skill_text, "skill tracks turns per round")
check("sequential_only" in (ROOT / "agents/research-planner.md").read_text(encoding="utf-8"), "planner marks sequential queries")
check((ROOT / "evals/README.md").exists() and (ROOT / "evals/seed-questions.md").exists(), "evals loop and seed set exist")
check("[thin]" in skill_text and "never round thin up" in skill_text, "skill defines confidence tags")
check("Exhaustive Technical Report" in skill_text, "skill defines exhaustive technical report contract")
check("Multi-Turn Section Assembly" in skill_text, "skill defines multi-turn section assembly contract")
check("Publication-Grade HTML Whitepaper" in skill_text, "skill defines publication-grade HTML whitepaper")
check("Document Ingestion Mode" in skill_text, "skill defines Document Ingestion mode")

print(f"\n{len(FAILURES)} failures")
sys.exit(1 if FAILURES else 0)
