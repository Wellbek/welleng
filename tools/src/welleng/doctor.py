"""Report which components of the package map are present.

Read-only: it looks executables up on PATH and never installs or changes anything.
Only a missing mandatory component makes the report fail.
"""

from __future__ import annotations

import shutil
import tomllib
from dataclasses import dataclass
from pathlib import Path

TIERS = ("mandatory", "recommended", "optional")


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
