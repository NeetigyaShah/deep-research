import pluginMain from "../src/main.ts";

const calls: string[] = [];
const factory = pluginMain as unknown as (pi: {
	on: (event: string, handler: unknown) => void;
	registerCommand: (name: string, def: unknown) => void;
}) => void;

factory({
	on: (event: string) => {
		calls.push(`on:${event}`);
	},
	registerCommand: (name: string) => {
		calls.push(`command:${name}`);
	},
});

const expected = ["on:session_start", "on:session_start", "command:deep-research-status"];
for (const want of expected) {
	if (!calls.includes(want)) throw new Error(`missing registration: ${want} (got ${JSON.stringify(calls)})`);
}
console.log(`EXT_OK ${JSON.stringify(calls)}`);
