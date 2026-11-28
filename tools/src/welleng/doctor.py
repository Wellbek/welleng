"""Report which components of the package map are present, and with --claude the Claude Code plugins.

Read-only: it looks executables up on PATH, asks `claude plugin` for JSON and text output, and never installs or
changes anything (ADR 0005: official CLI output only, no files under ~/.claude are read).
Only a missing mandatory component makes the report fail, the plugin section is advice.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

TIERS = ("mandatory", "recommended", "optional")
WELLENG_PLUGIN = "welleng@welleng-local"
HOOKS_PLUGIN = "welleng-hooks@welleng-local"
ALWAYS_ON_RE = re.compile(r"Always-on:\s*~?([\d,]+)\s*tok")
Runner = Callable[[list[str]], "str | None"]


@dataclass(frozen=True)
class Component:
    name: str
    tier: str
    bins: tuple[str, ...]
    fallback: str | None
    found: str | None


def default_packages_path() -> Path:
    """packages/packages.toml of the repository this package lives in."""
    return Path(__file__).resolve().parents[3] / "packages" / "packages.toml"


def load_components(path: Path) -> list[Component]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    components = []
    for entry in data["package"]:
        bins = tuple(entry.get("bins", [entry["name"]]))
        found = next((b for b in bins if shutil.which(b)), None)
        components.append(
            Component(entry["name"], entry["tier"], bins, entry.get("fallback"), found)
        )
    return components


def render(components: list[Component]) -> str:
    lines = []
    for tier in TIERS:
        group = [c for c in components if c.tier == tier]
        if not group:
            continue
        lines.append(f"{tier}:")
        for c in group:
            if c.found:
                lines.append(f"  ok       {c.name} ({c.found})")
            else:
                hint = f", fallback: {c.fallback}" if c.fallback else ""
                lines.append(f"  missing  {c.name}{hint}")
    return "\n".join(lines)


def exit_code(components: list[Component]) -> int:
    return 1 if any(c.tier == "mandatory" and not c.found for c in components) else 0


@dataclass(frozen=True)
class Plugin:
    id: str
    enabled: bool
    version: str
    always_on: int | None


def _run(args: list[str]) -> str | None:
    """Stdout of a command, or None when it is missing, fails or hangs."""
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout if out.returncode == 0 else None


def plugin_version_in_repo() -> str:
    manifest = Path(__file__).resolve().parents[3] / "claude-plugin" / ".claude-plugin" / "plugin.json"
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def load_plugins(run: Runner = _run) -> list[Plugin] | None:
    """Installed plugins with the version a session loads and the always-on token estimate, or None without claude."""
    raw = run(["claude", "plugin", "list", "--json"])
    if raw is None:
        return None
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError:
        return None
    plugins = []
    for entry in entries if isinstance(entries, list) else []:
        version = entry.get("folderVersion") if entry.get("readFromFolder") else entry.get("version")
        always_on = None
        if entry.get("enabled"):
            m = ALWAYS_ON_RE.search(run(["claude", "plugin", "details", entry["id"]]) or "")
            always_on = int(m.group(1).replace(",", "")) if m else None
        plugins.append(Plugin(entry["id"], bool(entry.get("enabled")), str(version or "unknown"), always_on))
    return plugins


def render_plugins(plugins: list[Plugin] | None, repo_version: str) -> str:
    if plugins is None:
        return "claude plugins:\n  skipped  the claude command is not available"
    lines = ["claude plugins:"]
    for p in plugins:
        state = "enabled " if p.enabled else "disabled"
        cost = f", ~{p.always_on:,} always-on tokens (estimate)" if p.always_on is not None else ""
        lines.append(f"  {state} {p.id} {p.version}{cost}")
    total = sum(p.always_on or 0 for p in plugins if p.enabled)
    lines.append(f"  total    ~{total:,} always-on tokens (estimate, it also counts user-invoked skills)")
    welleng = next((p for p in plugins if p.id == WELLENG_PLUGIN), None)
    if welleng is None:
        lines.append(f"  advice   {WELLENG_PLUGIN} is not installed, see docs/guides/claude-code.md")
    elif welleng.version != repo_version:
        lines.append(
            f"  advice   sessions load {WELLENG_PLUGIN} {welleng.version} but the repository has {repo_version}, run"
            f" `claude plugin marketplace update welleng-local` and `claude plugin update {WELLENG_PLUGIN}`"
        )
    if not any(p.id == HOOKS_PLUGIN for p in plugins):
        lines.append(f"  advice   {HOOKS_PLUGIN} is not installed, effort hints and session state need it")
    return "\n".join(lines)
