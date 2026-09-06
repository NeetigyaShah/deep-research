# Pull request checklist

- [ ] CI is green (`validate`, `extension`, `mcp`)
- [ ] Versions bumped together in `package.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` (`python scripts/bump_version.py --part minor|patch`; CI checks this)
- [ ] Skill/agent/command behavior described in plain words below (what changes for the user?)
- [ ] If MCP servers changed: tested with `/mcp list` in at least one harness

## What this changes
