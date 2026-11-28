"""Control and review effort hints. The hook itself lives in claude-plugin-hooks/hooks/effort_hint.py.

Both sides share two files in $XDG_STATE_HOME/welleng: hints.json (switches) and hints.log (events).
"""

from __future__ import annotations

import json
import os
import time
from collections import Counter
from pathlib import Path


def state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "welleng"


def _load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save(directory: Path, state: dict) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    tmp = directory / "hints.json.tmp"
    tmp.write_text(json.dumps(state), encoding="utf-8")
    tmp.replace(directory / "hints.json")


def snooze(directory: Path, hours: float = 4, now: float | None = None) -> None:
    state = _load(directory / "hints.json")
    state["snooze_until"] = (now if now is not None else time.time()) + hours * 3600
    _save(directory, state)


def set_off(directory: Path, off: bool) -> None:
    state = _load(directory / "hints.json")
    state["off"] = off
    state.pop("snooze_until", None) if not off else None
    _save(directory, state)


def report(directory: Path) -> str:
    state = _load(directory / "hints.json")
    status = "off" if state.get("off") else ("snoozed" if float(state.get("snooze_until", 0)) > time.time() else "on")
    events = []
    try:
        for line in (directory / "hints.log").read_text(encoding="utf-8").splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        pass
    lines = [f"hints: {status}", f"recommendations logged: {len(events)}", f"prompts that carried no effort level: {int(state.get('no_effort', 0))}"]
    for pair, n in Counter(f"{e.get('current')} -> {e.get('recommended')}" for e in events).most_common():
        lines.append(f"  {pair}: {n}")
    return "\n".join(lines)
