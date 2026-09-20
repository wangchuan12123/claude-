#!/usr/bin/env python3
"""Auto-sync the ~/.claude git repo (whitelisted files) with its remote.

Usage:
  git-auto-sync.py push   # git add -A; commit if changed; push origin main
  git-auto-sync.py pull   # fetch + fast-forward-only pull (never overwrites local work)

Always exits 0 so it never blocks the Claude Code session.
"""
import datetime
import os
import subprocess
import sys

REPO = os.path.expanduser("~/.claude")


def run(*args, timeout=60):
    try:
        return subprocess.run(
            ["git", "-C", REPO, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception:
        return None


def push():
    # Stage whitelisted changes (settings.json / .mcp.json / node_modules are
    # excluded by .gitignore, so this only ever stages skills/hooks/rules/etc).
    run("add", "-A")
    r = run("diff", "--cached", "--quiet")
    if r is None or r.returncode == 0:
        return  # nothing staged, or git error -> skip
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if run("commit", "-q", "-m", f"auto-sync: {ts}", timeout=120) is None:
        return
    run("push", "-q", "origin", "main", timeout=60)


def pull():
    run("fetch", "-q", "origin", "main", timeout=60)
    run("pull", "--ff-only", "-q", "origin", "main", timeout=60)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "push"
    (pull if mode == "pull" else push)()
    sys.exit(0)
