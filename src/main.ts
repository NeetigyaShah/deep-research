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
}
