"""Generate a keybinding cheatsheet from a tmux configuration file.

The configuration file is read as plain text, so the cheatsheet always matches what is deployed.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Binding:
    table: str
    key: str
    command: str


def parse_tmux(text: str) -> list[Binding]:
    """Return the bindings declared with bind or bind-key, in file order."""
    bindings = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            words = shlex.split(line, comments=True)
        except ValueError:
            continue
        if not words or words[0] not in ("bind", "bind-key"):
            continue
        table = "prefix"
        rest = words[1:]
        i = 0
        while i < len(rest) and rest[i].startswith("-"):
            flag = rest[i]
            if flag == "-n":
                table = "root"
            elif flag == "-T" and i + 1 < len(rest):
                table = rest[i + 1]
                i += 1
            elif flag == "-N" and i + 1 < len(rest):
                i += 1
            i += 1
        if i < len(rest):
            bindings.append(Binding(table, rest[i], " ".join(rest[i + 1 :])))
    return bindings


def render(bindings: list[Binding], pattern: str | None = None) -> str:
    needle = pattern.lower() if pattern else None
    rows = [b for b in bindings if not needle or needle in f"{b.table} {b.key} {b.command}".lower()]
    if not rows:
        return "no matching keybinding"
    width = max(len(b.key) for b in rows)
    out = []
    for table in dict.fromkeys(b.table for b in rows):
        out.append(f"[{table}]")
        for b in rows:
            if b.table == table:
                out.append(f"  {b.key:<{width}}  {b.command}")
    return "\n".join(out)


def load(path: Path) -> list[Binding]:
    return parse_tmux(path.read_text(encoding="utf-8"))
