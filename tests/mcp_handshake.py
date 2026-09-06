"""Live MCP handshake: all bundled servers initialize and list tools over stdio."""

import json
import queue
import shutil
import subprocess
import sys
import threading
import time

SERVERS = {
    "arxiv": ("uvx", ["arxiv-mcp-server"]),
    "ddg-search": ("uvx", ["--with", "duckduckgo-mcp-server[browser]", "duckduckgo-mcp-server"]),
    "gutenberg": ("npx", ["-y", "@cyanheads/gutenberg-mcp-server"]),
}
MIN_TOOLS = {"arxiv": 10, "ddg-search": 3, "gutenberg": 3}
TIMEOUT = 180


def start(cmd):
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    out_q: queue.Queue = queue.Queue()

    def reader():
        for line in proc.stdout:
            line = line.strip()
            if line:
                out_q.put(line)

    threading.Thread(target=reader, daemon=True).start()
    return proc, out_q


def call(proc, out_q, method, params, call_id, timeout=120):
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": call_id, "method": method, "params": params}) + "\n")
    proc.stdin.flush()
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            message = json.loads(out_q.get(timeout=1))
        except queue.Empty:
            continue
        except json.JSONDecodeError:
            continue
        if message.get("id") == call_id:
            return message
    raise TimeoutError(f"no response to {method}")


def notify(proc, method):
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n")
    proc.stdin.flush()


def main():
    runners = {}
    for runner in {runner for runner, _ in SERVERS.values()}:
        found = shutil.which(runner)
        assert found, f"{runner} not on PATH"
        runners[runner] = found
    failures = []
    for name, (runner, args) in SERVERS.items():
        try:
            proc, out_q = start([runners[runner], *args])
            init = call(
                proc,
                out_q,
                "initialize",
                {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "ci", "version": "1"}},
                1,
            )
            assert "result" in init, f"initialize failed: {init}"
            notify(proc, "notifications/initialized")
            time.sleep(1)
            tools = call(proc, out_q, "tools/list", {}, 2)["result"]["tools"]
            names = [t["name"] for t in tools]
            assert len(names) >= MIN_TOOLS[name], f"only {len(names)} tools: {names}"
            print(f"ok   {name}: {len(names)} tools ({', '.join(names[:6])}...)")
            proc.kill()
        except Exception as exc:
            failures.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")
    if failures:
        sys.exit(1)
    print("\nall MCP handshakes passed")


main()
