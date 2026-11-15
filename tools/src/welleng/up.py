"""Open or attach to the project tmux session with the default four-window layout."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

WINDOWS = ("edit", "git", "agents", "shell")


def session_name(path: Path) -> str:
    """tmux-safe session name from the project directory name."""
    name = re.sub(r"[^A-Za-z0-9_-]+", "-", path.name).strip("-")
    return name or "project"


def window_commands(have: callable = shutil.which) -> dict[str, str | None]:
    """Command per window, None meaning a plain shell. Missing tools degrade to a shell."""
    return {
        "edit": "NVIM_APPNAME=${NVIM_APPNAME:-nvim} nvim" if have("nvim") else None,
        "git": "lazygit" if have("lazygit") else None,
        "agents": "watch -t -n 5 welleng agents" if have("watch") and have("welleng") else None,
        "shell": None,
    }


def tmux(socket: str | None, *args: str) -> subprocess.CompletedProcess:
    base = ["tmux"] + (["-L", socket] if socket else [])
    return subprocess.run([*base, *args], capture_output=True, text=True, check=False)


def has_session(socket: str | None, name: str) -> bool:
    return tmux(socket, "has-session", "-t", f"={name}").returncode == 0


def create(socket: str | None, name: str, path: Path, commands: dict[str, str | None]) -> None:
    first = True
    for window in WINDOWS:
        cmd = commands.get(window)
        args = ["-c", str(path), "-n", window]
        if first:
            result = tmux(socket, "new-session", "-d", "-s", name, *args)
            first = False
        else:
            result = tmux(socket, "new-window", "-t", f"={name}:", *args)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "tmux failed")
        if cmd:
            tmux(socket, "send-keys", "-t", f"={name}:{window}", cmd, "Enter")
    tmux(socket, "select-window", "-t", f"={name}:{WINDOWS[0]}")


def up(path: Path, socket: str | None = None, attach: bool = True) -> int:
    if shutil.which("tmux") is None:
        print("up: tmux is not installed")
        return 1
    if not path.is_dir():
        print(f"up: not a directory: {path}")
        return 1
    name = session_name(path.resolve())
    if not has_session(socket, name):
        try:
            create(socket, name, path.resolve(), window_commands())
        except RuntimeError as e:
            print(f"up: {e}")
            return 1
    if not attach:
        print(name)
        return 0
    base = ["tmux"] + (["-L", socket] if socket else [])
    verb = "switch-client" if os.environ.get("TMUX") else "attach-session"
    os.execvp("tmux", [*base, verb, "-t", f"={name}"])
    return 0  # pragma: no cover - execvp does not return
