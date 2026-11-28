#!/usr/bin/env python3
"""UserPromptSubmit hook: recommend a different /effort level when the gap is large (ADR 0013).

Local and free: a small keyword and length scorer, no model call, no network.
It never switches anything. It prints one `systemMessage` JSON object, shown to the user only,
or nothing. It prefers silence: a hint needs a gap of two levels or more and clear confidence.
State lives in $XDG_STATE_HOME/welleng (default ~/.local/state/welleng), never in ~/.claude.
The effort level comes from the prompt event when it carries one. Claude Code 2.1.328 sends interactive prompt
events without it, so the hook then reads the level the status line recorded for the session (ADR 0021).
The log records the estimate and the levels only, never prompt text.
Standard library only, and it never raises.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

# `python3 -I` leaves the script directory off sys.path, so add it for the sibling module.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from state_writer import SESSION_ID_RE  # noqa: E402

LEVELS = ["low", "medium", "high", "xhigh", "max"]
RECOMMEND = {"light": "low", "standard": "medium", "heavy": "high"}
COOLDOWN_SECONDS = 30 * 60
THRESHOLD = 0.6

LIGHT_RE = re.compile(r"\b(typo|rename|what does|what is|explain|show me|list|format|status|commit|revert|print|where is)\b", re.I)
HEAVY_RE = re.compile(
    r"\b(refactor|redesign|re-?architect|architecture|migrate|migration|root cause|investigate|"
    r"across (the )?(codebase|repo|project|modules)|end[- ]to[- ]end|from scratch|design (a|the) )\b",
    re.I,
)


def state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "welleng"


def estimate(prompt: str) -> tuple[str, float]:
    """Return (light|standard|heavy, confidence between 0 and 1)."""
    text = prompt.strip()
    length = len(text)
    heavy = len(HEAVY_RE.findall(text))
    light = len(LIGHT_RE.findall(text))
    files = len(re.findall(r"[\w./-]+\.(py|ts|tsx|js|go|rs|java|c|cpp|md|toml|json|sh|lua)\b", text))
    if heavy >= 1 and (length > 300 or heavy >= 2 or files >= 3):
        return "heavy", min(0.95, 0.6 + 0.1 * heavy + 0.05 * min(files, 3))
    if light >= 1 and heavy == 0 and length < 120 and files <= 1:
        return "light", 0.8
    return "standard", 0.3


def load_state(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(directory: Path, state: dict) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    tmp = directory / "hints.json.tmp"
    tmp.write_text(json.dumps(state), encoding="utf-8")
    tmp.replace(directory / "hints.json")


def decide(prompt: str, current: str | None, state: dict, now: float) -> tuple[str | None, str, float]:
    """Return (level to recommend or None, estimate, confidence)."""
    est, conf = estimate(prompt)
    if current not in LEVELS or state.get("off") or now < float(state.get("snooze_until", 0)):
        return None, est, conf
    if "ultrathink" in prompt.lower() or conf < THRESHOLD:
        return None, est, conf
    if now - float(state.get("last_hint", 0)) < COOLDOWN_SECONDS:
        return None, est, conf
    rec = RECOMMEND[est]
    if abs(LEVELS.index(rec) - LEVELS.index(current)) < 2:
        return None, est, conf
    return rec, est, conf


def session_effort(directory: Path, session_id: object) -> str | None:
    """The effort level the status line recorded for this session, or None."""
    if not isinstance(session_id, str) or not SESSION_ID_RE.match(session_id):
        return None
    level = load_state(directory / "sessions" / f"{session_id}.json").get("effort")
    return level if level in LEVELS else None


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if event.get("hook_event_name") != "UserPromptSubmit":
            return 0
        effort = event.get("effort")
        current = effort.get("level") if isinstance(effort, dict) else None
        directory = state_dir()
        if current not in LEVELS:
            current = session_effort(directory, event.get("session_id"))
        state_path = directory / "hints.json"
        state = load_state(state_path)
        now = time.time()
        rec, est, conf = decide(str(event.get("prompt", "")), current, state, now)
        if current not in LEVELS:
            # Count prompts that arrive without an effort level, so the report shows whether hints can fire.
            state["no_effort"] = int(state.get("no_effort", 0)) + 1
            rec = None
        if rec is None:
            if current not in LEVELS:
                save_state(directory, state)
            return 0
        state["last_hint"] = now
        save_state(directory, state)
        with (directory / "hints.log").open("a", encoding="utf-8") as log:
            log.write(json.dumps({"t": int(now), "estimate": est, "confidence": round(conf, 2), "current": current, "recommended": rec}) + "\n")
        print(json.dumps({"systemMessage": f"hint: this looks {est}, consider /effort {rec} (now {current}). Silence with: welleng hints snooze"}))
    except Exception:  # noqa: BLE001 - a hook must never break the session
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
