#!/usr/bin/env python3
"""Hook state writer: one small JSON file per live session, read by `welleng agents` (ADR 0012).

Handles SessionStart, UserPromptSubmit, Stop, SubagentStart, SubagentStop and SessionEnd.
It records ids and levels only: never the prompt, never the assistant message, never the
transcript path. Files live in $XDG_STATE_HOME/welleng/sessions (default ~/.local/state), mode 600.
It prints nothing, so it can never add text to the model context, and it never raises.
Standard library only.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
KEEP_SECONDS = 7 * 24 * 3600


def sessions_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "welleng" / "sessions"


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp, path)


def prune(directory: Path, now: float) -> None:
    for old in directory.glob("*.json"):
        try:
            if now - old.stat().st_mtime > KEEP_SECONDS:
                old.unlink()
        except OSError:
            pass


def update(directory: Path, event: dict, now: float) -> None:
    session_id = event.get("session_id")
    name = event.get("hook_event_name")
    if not isinstance(session_id, str) or not SESSION_ID_RE.match(session_id) or not isinstance(name, str):
        return
    path = directory / f"{session_id}.json"
    if name == "SessionEnd":
        path.unlink(missing_ok=True)
        return
    state = load(path)
    state.update({"session_id": session_id, "event": name, "updated": now})
    if isinstance(event.get("cwd"), str):
        state["cwd"] = event["cwd"]
    if isinstance(event.get("permission_mode"), str):
        state["permission_mode"] = event["permission_mode"]
    effort = event.get("effort")
    if isinstance(effort, dict) and isinstance(effort.get("level"), str):
        state["effort"] = effort["level"]
    if name == "SessionStart":
        if isinstance(event.get("model"), str):
            state["model"] = event["model"]
        state["subagents"] = []
        prune(directory, now)
    elif name in ("SubagentStart", "SubagentStop"):
        agent_id = event.get("agent_id")
        if isinstance(agent_id, str):
            active = {a for a in state.get("subagents", []) if isinstance(a, str)}
            (active.add if name == "SubagentStart" else active.discard)(agent_id)
            state["subagents"] = sorted(active)
    elif name == "Stop":
        state["subagents"] = []
    save(path, state)


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if isinstance(event, dict):
            update(sessions_dir(), event, time.time())
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
