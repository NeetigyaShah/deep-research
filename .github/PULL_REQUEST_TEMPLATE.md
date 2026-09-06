# Pull request checklist

- [ ] CI is green (`validate`, `extension`, `mcp`)
- [ ] Versions NOT bumped by hand (the version bot does it after merge)
- [ ] If this fixes a bug, the `bug` label is set (bot bumps patch instead of minor)
- [ ] Skill/agent/command behavior described in plain words below (what changes for the user?)
- [ ] If MCP servers changed: tested with `/mcp list` in at least one harness

## What this changes
