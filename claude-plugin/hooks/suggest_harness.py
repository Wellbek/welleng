#!/usr/bin/env python3
"""SessionStart hook: suggest /welleng:harness once when a project has no agent configuration.

Reads the hook event from stdin and prints one JSON object, or nothing.
Never raises: a hook failure must not disturb a session, and nothing but the JSON object may be
printed, because any other stdout would enter the model context (see ADR 0012).
Standard library only. Reads no file under ~/.claude, only the project directory.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MESSAGE = (
    "This project has no CLAUDE.md and no .claude/settings.json yet. "
    "If the user wants agent conventions, permissions or hooks set up, mention that the /welleng:harness "
    "skill can do it with a short questionnaire. Mention it at most once and do not start it unprompted."
)


def main() -> int:
    try:
        event = json.load(sys.stdin)
        cwd = Path(event.get("cwd") or ".")
        if event.get("hook_event_name") != "SessionStart" or event.get("source") != "startup":
            return 0
        if not (cwd / ".git").exists():
            return 0
        if (cwd / "CLAUDE.md").exists() or (cwd / ".claude" / "settings.json").exists():
            return 0
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": MESSAGE}}))
    except Exception:  # noqa: BLE001 - a hook must never break the session
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
