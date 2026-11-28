#!/usr/bin/env python3
"""Status line command: record model, effort, context use and cost, and print a compact line.

The plugin does not set the status line, because that would replace one you already have (ADR 0016), so this is opt-in: put it in your own settings as
  "statusLine": {"type": "command", "command": "python3 -I /path/to/claude-plugin-hooks/hooks/statusline.py"}
It merges into the same per-session file as state_writer.py. Standard library only, never raises.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# `python3 -I` leaves the script directory off sys.path, so add it for the sibling module.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from state_writer import SESSION_ID_RE, load, save, sessions_dir


def fields(payload: dict) -> dict:
    out: dict = {}
    model = payload.get("model")
    if isinstance(model, dict) and isinstance(model.get("id"), str):
        out["model"] = model["id"]
    effort = payload.get("effort")
    if isinstance(effort, dict) and isinstance(effort.get("level"), str):
        out["effort"] = effort["level"]
    ctx = payload.get("context_window")
    if isinstance(ctx, dict) and isinstance(ctx.get("used_percentage"), (int, float)):
        out["context_pct"] = round(float(ctx["used_percentage"]), 1)
    cost = payload.get("cost")
    if isinstance(cost, dict) and isinstance(cost.get("total_cost_usd"), (int, float)):
        out["cost_usd"] = round(float(cost["total_cost_usd"]), 4)
    return out


def line(values: dict) -> str:
    parts = [str(values["model"])] if "model" in values else []
    if "effort" in values:
        parts.append(str(values["effort"]))
    if "context_pct" in values:
        parts.append(f"ctx {values['context_pct']:.0f}%")
    if "cost_usd" in values:
        parts.append(f"${values['cost_usd']:.2f}")
    return " | ".join(parts)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            return 0
        values = fields(payload)
        session_id = payload.get("session_id")
        if isinstance(session_id, str) and SESSION_ID_RE.match(session_id) and values:
            path = sessions_dir() / f"{session_id}.json"
            state = load(path)
            state.update(values)
            state.update({"session_id": session_id, "updated": time.time()})
            save(path, state)
        print(line(values))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
