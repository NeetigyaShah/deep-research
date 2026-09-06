import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";

function progressLine(vals: Record<string, string>): string {
	const num = (key: string): number => Number.parseInt(vals[key] ?? "", 10) || 0;
	const kept = num("kept_claims");
	const target = Math.max(num("target_claims"), 1);
	const done = num("frontier_done");
	const pending = num("frontier_pending");
	let pct: number;
	if (vals["status"] === "complete") {
		pct = 100;
	} else {
		const coverage = Math.min(kept / target, 1);
		const drain = done / Math.max(done + pending, 1);
		pct = Math.min(99, Math.round(100 * (0.7 * coverage + 0.3 * drain)));
	}
	const filled = Math.round(pct / 5);
	const bar = "█".repeat(filled) + "░".repeat(20 - filled);
	return `[Research ${pct}% | round ${vals["round"] ?? "?"} | ${kept}/${vals["target_claims"] ?? "?"} claims | ${vals["must_answer_covered"] ?? "?"}/${vals["must_answer_total"] ?? "?"} questions | frontier ${pending} | ${vals["visited_pages"] ?? "?"} pages] ${bar}`;
}

async function latestStateDir(cwd: string): Promise<string | null> {
	let entries;
	try {
		entries = await readdir(path.join(cwd, "research"), { withFileTypes: true });
	} catch {
		return null;
	}
	let best: { dir: string; mtime: number } | null = null;
	for (const entry of entries) {
		if (!entry.isDirectory()) continue;
		const statePath = path.join(cwd, "research", entry.name, "state.md");
		try {
			const info = await stat(statePath);
			if (!best || info.mtimeMs > best.mtime) best = { dir: path.join("research", entry.name), mtime: info.mtimeMs };
		} catch {
			// Run has no state file yet.
		}
	}
	return best?.dir ?? null;
}
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

export default function deepResearch(pi: ExtensionAPI) {
	pi.on("session_start", async (_event, ctx) => {
		try {
			const proc = Bun.spawnSync(["uvx", "--version"]);
			if (proc.exitCode !== 0) {
				ctx.ui.notify(
					"deep-research: `uvx` not found — install uv (https://docs.astral.sh/uv/getting-started/installation/) so the arxiv + ddg-search MCP servers can run.",
					"warning",
				);
			}
		} catch {
			ctx.ui.notify("deep-research: could not check for `uvx` — arxiv + ddg-search servers need it on PATH.", "warning");
		}
	});

	pi.registerCommand("deep-research", {
		description: "Start a deep-research run: grill to a brief, then parallel DuckDuckGo + arXiv research with citations.",
		handler: async (args, ctx) => {
			const topic = args.trim();
			if (!topic) {
				ctx.ui.notify("Usage: /deep-research <research topic>", "warning");
				return;
			}
			pi.sendUserMessage(`Follow the deep-research skill (skill://deep-research) for this request. Topic: ${topic}`);
		},
	});

	pi.registerCommand("deep-research-status", {
		description: "Show the live progress bar of the latest deep-research run.",
		handler: async (_args, ctx) => {
			const dir = await latestStateDir(ctx.cwd);
			if (!dir) {
				ctx.ui.notify("deep-research: no research/*/state.md found — no run in progress here.", "warning");
				return;
			}
			try {
				const vals: Record<string, string> = {};
				const text = await readFile(path.join(ctx.cwd, dir, "state.md"), "utf8");
				for (const line of text.split("\n")) {
					const sep = line.indexOf(":");
					if (sep > 0) vals[line.slice(0, sep).trim()] = line.slice(sep + 1).trim();
				}
				ctx.ui.notify(`${dir}: ${progressLine(vals)}`, "info");
			} catch {
				ctx.ui.notify(`deep-research: could not read ${dir}/state.md.`, "warning");
			}
		},
	});
}
