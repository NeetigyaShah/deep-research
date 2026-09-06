"""Update checker: behind, current, and unreachable repos behave correctly."""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_update.py"
GIT_ENV = {"GIT_CONFIG_NOSYSTEM": "1", "HOME": tempfile.gettempdir()}


def git(*args, cwd):
    env = {
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
        **GIT_ENV,
    }
    out = subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "init.defaultBranch=main", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=60,
        env={**dict(__import__("os").environ), **env},
    )
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


def make_origin(tmp):
    origin = Path(tmp) / "origin.git"
    git("init", "--bare", str(origin), cwd=tmp)
    seed = Path(tmp) / "seed"
    git("clone", str(origin), str(seed), cwd=tmp)
    (seed / "file.txt").write_text("v1", encoding="utf-8")
    git("add", "file.txt", cwd=seed)
    git("commit", "-m", "v1", cwd=seed)
    git("push", "origin", "main", cwd=seed)
    return origin


def check(path):
    out = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True, timeout=90)
    return out


with tempfile.TemporaryDirectory() as tmp:
    origin = make_origin(tmp)
    clone = Path(tmp) / "clone"
    git("clone", str(origin), str(clone), cwd=tmp)

    out = check(clone)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "up to date" in out.stdout, out.stdout
    print("ok   current checkout reports up to date")

    worker = Path(tmp) / "worker"
    git("clone", str(origin), str(worker), cwd=tmp)
    (worker / "file.txt").write_text("v2", encoding="utf-8")
    git("add", "file.txt", cwd=worker)
    git("commit", "-m", "v2", cwd=worker)
    git("push", "origin", "main", cwd=worker)

    out = check(clone)
    assert out.returncode == 1, out.stdout + out.stderr
    assert "update available" in out.stdout and "git pull" in out.stdout, out.stdout
    print("ok   behind checkout reports update with pull guidance")

    # 3. Ahead checkout (worker pulls, commits v3, but has not pushed)
    git("pull", "origin", "main", cwd=worker)
    (worker / "file.txt").write_text("v3-local", encoding="utf-8")
    git("add", "file.txt", cwd=worker)
    git("commit", "-m", "v3", cwd=worker)
    out = check(worker)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "up to date" in out.stdout, out.stdout
    print("ok   ahead checkout reports up to date without false nag")

with tempfile.TemporaryDirectory() as tmp:
    out = check(Path(tmp))
    assert out.returncode == 2, out.stdout + out.stderr
    assert "not a git checkout" in out.stdout, out.stdout
    print("ok   non-repo path exits 2 with guidance")

print("\nall update tests passed")
