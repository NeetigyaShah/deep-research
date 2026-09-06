# Deep Research

A research assistant that lives inside your AI coding tool. You give it a
topic. It asks you what you actually want, searches hundreds of web pages
and academic papers, checks every fact against its source, and hands you a
report with citations. Like the Deep Research features in ChatGPT and
Gemini, but running in your own setup.

## How it works

1. **You ask.** Type `/deep-research` followed by your topic.
2. **It interviews you.** Before searching anything, it repeats back what
   it thinks you want and asks a few pointed questions: who is this for,
   how deep should it go, which time period, what format you want the
   answer in. It never states facts at this stage. If it doesn't know
   something, it asks instead of guessing.
3. **It plans.** It turns your answers into a research plan: a list of web
   searches, academic paper searches, and the exact questions the final
   report must answer.
4. **It searches in parallel.** Several sub-agents fan out at once. Web
   searches go through DuckDuckGo. Academic papers go through arXiv, where
   it reads the actual sections of the most relevant papers (not just
   abstracts) and follows their citations. If your topic has no academic
   literature, it skips that part and tells you.
5. **It checks every fact.** A separate pass keeps a claim only if there
   is a direct quote from a trustworthy source behind it — an official
   document, specification, or paper section. Anything unverified is
   dropped. Numbers, dates, and cause-and-effect claims without a source
   never reach the report.
6. **It keeps going until done.** It compares what it found against the
   questions from step 2 and sends agents back out for the gaps, following
   up on promising leads. It stops when a full round of searching adds
   almost nothing new, or when you tell it to stop. Whatever is still
   unknown is listed under Gaps instead of being made up.
7. **You get a report.** A Markdown file with a summary, findings (every
   paragraph cited), a papers section, gaps, a source list, and
   ready-to-use citations.

Everything runs on your main AI model, for as many rounds as the topic
needs. A hard question takes roughly half an hour to an hour and a half.
You can walk away mid-run: progress is saved in plain Markdown files, so
an interrupted run picks up where it left off.

## What you need

Only one thing: **uv** (a Python tool installer). It provides the `uvx`
command, which downloads and runs the two search servers automatically on
first use. Install it from
https://docs.astral.sh/uv/getting-started/installation/

The two servers it fetches:

- **arxiv** — searches and reads academic papers from arXiv.
- **ddg-search** — searches the web through DuckDuckGo and reads pages.

## Installation

Pick your tool. In every case, make sure `uvx` works first by running
`uvx --version` in your terminal.

### OMP (Oh My Pi)

```bash
git clone https://github.com/NeetigyaShah/deep-research.git
# add to your project's .omp/config.yml:
#   extensions:
#     - ../deep-research
```

Then inside OMP, run `/reload-plugins` and check `/mcp list` shows
`arxiv` and `ddg-search`.

(On machines where symlinks work, `omp plugin link <path-to-this-folder>`
also installs it for all projects.)

### Claude Code

```bash
claude plugin marketplace add NeetigyaShah/deep-research
claude plugin install deep-research@deep-research
```

Then restart Claude Code, or run `/reload-plugins`, and check the `arxiv`
and `ddg-search` servers connected.

### Codex

```bash
codex plugin marketplace add NeetigyaShah/deep-research
codex plugin add deep-research@deep-research
```

This repo already contains the Codex plugin file (`.codex-plugin/`)
with both search servers and the skill wired in.

### OpenCode

OpenCode reads its setup from `opencode.json` and the `.opencode/`
folder. Merge and copy three things:

```bash
# 1. add the two servers from integrations/opencode.json
#    into your opencode.json under "mcp" -> "servers"
# 2. copy the skill, command, and agents:
cp -r skills/deep-research .opencode/skills/
cp commands/deep-research.md .opencode/commands/
cp agents/*.md .opencode/agents/
```

Tool names will look like `arxiv_search_papers` and
`ddg-search_search` — that is normal for OpenCode.

### Cursor

Cursor understands the open Agent Skills standard and Claude-style MCP
files:

```bash
# 1. servers: merge integrations/cursor-mcp.json into
#    .cursor/mcp.json (this project) or ~/.cursor/mcp.json (all projects)
# 2. skill:
cp -r skills/deep-research .cursor/skills/
```

Restart Cursor and confirm both servers show as connected in
Settings → MCP.

## Use

```text
/deep-research <your topic>
```

Example: `/deep-research carbon credit trading scheme India compliance`

Answer its questions, approve the plan, come back later for the report.
You can also invoke the skill directly where your tool supports it
(`/skill:deep-research <topic>` in OMP).

When it asks for output format: `md` (default) always works. `pdf` and
`doc` need extra conversion software installed — it will tell you.
While it works, every round ends with a progress line like
`[Research 62% | round 4 | 41/54 claims | 4/6 questions | frontier 12 |
183 pages] ████████████░░░░░░░░`. Percent = mostly facts-found versus
target, partly leads worked through — capped at 99% until the report is
done. Check anytime without disturbing it: `python scripts/progress.py
research/<topic>` in any terminal, or `/deep-research-status` in OMP.

## When it finishes (the end log)

Every run ends with a log like this — same numbers in every tool,
only the place you see it changes:

```text
[Research done] carbon-credits — 6/6 questions, 58 kept claims
  Time: 1h 2m 3s (… → … UTC) | Rounds: 6 | Pages: 240
  Papers cited: 7 | Web sources: 31 | Dropped: 12
  Report: research/carbon-credits/report.md
```

That's papers cited, web sources, checked facts kept and dropped, and
total time from start to finish. In OMP it prints in chat and
`/deep-research-status` shows it on demand. Everywhere else it prints
in chat and `python scripts/stats.py research/<topic>` reprints it in
any terminal.

## Asking follow-up questions

```text
/followup what penalty applies to cement plants that miss targets?
/followup carbon-credits how is biomass treated?
```

It answers from the facts it already checked, reusing the report's
citations — no new searching, no new interview. If the answer isn't in
there, it says exactly what is missing and what it would search next.
Reply `research more` and it digs deeper with the same tools, checks
the new facts, updates the report, and prints a fresh end log. The
original brief is never rewritten; every follow-up is appended to
`followups.md` so you can see what was asked and what changed.

## The loop (why it doesn't quit early)

Each run keeps score in `research/<topic>/state.md`: how many questions
are covered, how many checked facts exist versus the target (3 per
question), and how many leads are still queued. A round that leaves any
question with zero facts behind is not allowed to be the last one —
unless two full rounds in a row find nothing new anywhere, which means
the topic is dry and the rest goes under Gaps. If the search keeps
repeating itself, the agents are forced to rephrase before trying again.
You can stop it anytime; it reports from what it has.

## What's inside

```text
.mcp.json / mcp.json        both search servers (Claude/OMP style)
.codex-mcp.json             both search servers (Codex style)
integrations/opencode.json  both search servers (OpenCode style)
integrations/cursor-mcp.json both search servers (Cursor style)
skills/deep-research/       the 6-step workflow (works everywhere)
agents/                     planner, web diver, paper diver, fact checker
commands/deep-research.md   the /deep-research command
.claude-plugin/             Claude Code plugin + marketplace files
.codex-plugin/              Codex plugin file
.agents/                    agent-plugins marketplace file
src/main.ts                 OMP extension (commands + startup check)
scripts/progress.py         live progress bar from any state.md
```

## Honest notes

- Fully tested on **OMP** (skill, command, and both servers verified
  working in a live session). The Claude, Codex, OpenCode, and Cursor
  paths follow each tool's documented plugin format but have not been
  run here yet — if one misbehaves, the fix is almost always "the MCP
  servers didn't connect," and the README's troubleshooting section in
  each integration file covers it.
- DuckDuckGo allows roughly 30 searches and 20 page reads per minute,
  shared across agents. Hundreds of pages per run is realistic;
  thousands means multiple rounds, not one burst.
- Web content and papers are treated as untrusted input: the agents
  quote them but never obey instructions hidden inside them.
