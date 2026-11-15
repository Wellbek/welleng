"""Central view of Claude Code sessions, from the official `claude agents --json` output.

The JSON schema is not a frozen API (ADR 0005), so every field is read defensively and unknown
values are shown as "unknown" instead of failing.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, replace
from pathlib import Path

# Raw state strings seen from the CLI, mapped to the states shown to the user.
STATE_MAP = {
    "busy": "working",
    "working": "working",
    "running": "working",
    "idle": "idle",
    "waiting": "waiting",
    "blocked": "waiting",
    "needs_input": "waiting",
    "done": "done",
    "completed": "done",
}
ORDER = {"waiting": 0, "working": 1, "idle": 2, "done": 3, "unknown": 4}


@dataclass(frozen=True)
class Agent:
    session_id: str
    project: str
    name: str
    kind: str
    state: str
    started_ms: int | None
    pid: int | None
    # Filled from the hook state writer when it has run for this session, see enrich().
    model: str | None = None
    effort: str | None = None
    context_pct: float | None = None
    cost_usd: float | None = None
    subagents: int | None = None


class AgentsError(RuntimeError):
    """`claude agents --json` could not be run or understood."""


def parse(text: str) -> list[Agent]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise AgentsError(f"unreadable output from claude agents ({e})") from e
    if not isinstance(data, list):
        raise AgentsError("claude agents did not return a list")
    agents = []
    for item in data:
        if not isinstance(item, dict):
            continue
        raw = str(item.get("status") or item.get("state") or "").lower()
        cwd = str(item.get("cwd") or "")
        started = item.get("startedAt")
        pid = item.get("pid")
        agents.append(
            Agent(
                session_id=str(item.get("sessionId") or item.get("id") or "?"),
                project=Path(cwd).name or "?",
                name=str(item.get("name") or ""),
                kind=str(item.get("kind") or "?"),
                state=STATE_MAP.get(raw, "unknown"),
                started_ms=started if isinstance(started, int) else None,
                pid=pid if isinstance(pid, int) else None,
            )
        )
    return sorted(agents, key=lambda a: (ORDER[a.state], a.project))


def fetch(timeout: float = 20.0) -> list[Agent]:
    try:
        result = subprocess.run(["claude", "agents", "--json"], capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError as e:
        raise AgentsError("the claude command was not found") from e
    except subprocess.TimeoutExpired as e:
        raise AgentsError("claude agents timed out") from e
    if result.returncode != 0:
        raise AgentsError(f"claude agents failed with exit code {result.returncode}")
    return parse(result.stdout)


def state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "welleng" / "sessions"


def enrich(agents: list[Agent], directory: Path | None = None) -> list[Agent]:
    """Add model, effort, context, cost and subagent count from the hook state files, where present."""
    directory = directory or state_dir()
    out = []
    for a in agents:
        path = directory / f"{a.session_id}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            data = None
        if not isinstance(data, dict):
            out.append(a)
            continue

        def text(key: str) -> str | None:
            v = data.get(key)
            return v if isinstance(v, str) else None

        def number(key: str) -> float | None:
            v = data.get(key)
            return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None

        subs = data.get("subagents")
        out.append(replace(a, model=text("model"), effort=text("effort"), context_pct=number("context_pct"),
                           cost_usd=number("cost_usd"), subagents=len(subs) if isinstance(subs, list) else None))
    return out


def age(started_ms: int | None, now: float | None = None) -> str:
    if started_ms is None:
        return "?"
    seconds = max(0, int((now if now is not None else time.time()) - started_ms / 1000))
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60)):
        if seconds >= size:
            return f"{seconds // size}{unit}"
    return f"{seconds}s"


def waiting_count(agents: list[Agent]) -> int:
    return sum(a.state == "waiting" for a in agents)


def render(agents: list[Agent], now: float | None = None) -> str:
    if not agents:
        return "no Claude Code sessions"
    extras = any(a.model or a.effort or a.context_pct is not None or a.cost_usd is not None for a in agents)
    header = ("state", "project", "name", "kind", "age") + (("model", "effort", "ctx", "cost", "sub") if extras else ())
    rows = [header]
    for a in agents:
        row = (a.state, a.project, a.name or "-", a.kind, age(a.started_ms, now))
        if extras:
            row += (
                a.model or "-",
                a.effort or "-",
                f"{a.context_pct:.0f}%" if a.context_pct is not None else "-",
                f"${a.cost_usd:.2f}" if a.cost_usd is not None else "-",
                str(a.subagents) if a.subagents is not None else "-",
            )
        rows.append(row)
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    return "\n".join("  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip() for r in rows)
