import { mkdtempSync, mkdirSync, writeFileSync, utimesSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { resolveFollowupRun } from "../src/main.ts";

function fixture(): string {
	const root = mkdtempSync(path.join(tmpdir(), "dr-followup-"));
	for (const [name, mtime] of [["alpha", 1000], ["beta", 2000]] as const) {
		const dir = path.join(root, "research", name);
		mkdirSync(dir, { recursive: true });
		const file = path.join(dir, "state.md");
		writeFileSync(file, `round: 1\nstatus: running\n`);
		const date = new Date(mtime);
		utimesSync(file, date, date);
	}
	return root;
}

function assertEqual(actual: unknown, want: unknown, label: string): void {
	if (actual !== want) throw new Error(`${label}: got ${JSON.stringify(actual)}, want ${JSON.stringify(want)}`);
}

const root = fixture();

let got = await resolveFollowupRun(root, "alpha what is the penalty?");
assertEqual(got.dir, path.join("research", "alpha"), "explicit slug dir");
assertEqual(got.question, "what is the penalty?", "explicit slug question");

got = await resolveFollowupRun(root, "what is the penalty?");
assertEqual(got.dir, path.join("research", "beta"), "latest run fallback");
assertEqual(got.question, "what is the penalty?", "full text kept as question");

got = await resolveFollowupRun(root, "beta");
assertEqual(got.dir, path.join("research", "beta"), "slug-only dir");
assertEqual(got.question, "", "slug-only leaves empty question");

got = await resolveFollowupRun(path.join(root, "missing"), "anything?");
assertEqual(got.dir, null, "no runs yields null dir");
assertEqual(got.question, "anything?", "question preserved without runs");

console.log("FOLLOWUP_OK");
