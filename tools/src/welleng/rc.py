"""Remote Control helpers: start the server in its own tmux window, and a listening-port check.

Remote Control is outbound-only according to the documentation `[docs]`, so the security check
here proves it on this machine: no new non-loopback listener may appear while it runs.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path

LOOPBACK = ("127.", "[::1]", "::1")


def window_command(name: str | None, permission_mode: str = "default") -> list[str]:
    """tmux command that starts Remote Control in a detached window called rc."""
    if permission_mode == "bypassPermissions":
        raise ValueError("Remote Control is never started with bypassPermissions by this tool")
    inner = ["claude", "remote-control", "--permission-mode", permission_mode]
    if name:
        inner += ["--name", name]
    return ["tmux", "new-window", "-d", "-n", "rc", shlex.join(inner)]


def start(name: str | None) -> int:
    if not os.environ.get("TMUX"):
        print("rc: run this inside tmux, it starts Remote Control in a window named rc")
        return 1
    return subprocess.run(window_command(name), check=False).returncode


def parse_listeners(ss_output: str) -> set[str]:
    """Local addresses from `ss -ltnH` output, as host:port strings."""
    found = set()
    for line in ss_output.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            found.add(parts[3])
    return found


def listeners() -> set[str]:
    result = subprocess.run(["ss", "-ltnH"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError("ss failed, this check needs Linux with iproute2")
    return parse_listeners(result.stdout)


def is_loopback(address: str) -> bool:
    return address.startswith(LOOPBACK)


def snapshot_path(directory: Path) -> Path:
    return directory / "ports-before.json"


def save_snapshot(directory: Path, current: set[str]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    snapshot_path(directory).write_text(json.dumps(sorted(current)), encoding="utf-8")


def diff(directory: Path, current: set[str]) -> tuple[list[str], list[str]]:
    """Return (new loopback listeners, new exposed listeners) since the snapshot."""
    before = set(json.loads(snapshot_path(directory).read_text(encoding="utf-8")))
    new = sorted(current - before)
    return [a for a in new if is_loopback(a)], [a for a in new if not is_loopback(a)]
