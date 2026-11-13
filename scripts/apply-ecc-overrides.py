#!/usr/bin/env python3
"""Merge the Well-Engineering ecc override list into the Claude Code user settings.

Usage:
    scripts/apply-ecc-overrides.py [--dry-run] [--settings PATH] [--overrides PATH]

It adds the listed hook ids to env.ECC_DISABLED_HOOKS and one permissions.deny rule per
listed skill, keeps every other key untouched, and writes atomically.
Running it twice changes nothing the second time.
Python 3.11 or newer, standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OVERRIDES = REPO / "home" / "dot_config" / "welleng" / "ecc-overrides.json"
DEFAULT_SETTINGS = Path.home() / ".claude" / "settings.json"


def merge(settings: dict, overrides: dict) -> list[str]:
    """Apply the overrides to `settings` in place and return a list of human-readable changes."""
    changes: list[str] = []

    wanted_hooks = [entry["id"] for entry in overrides["hooks"]]
    env = settings.get("env", {})
    existing = [h for h in env.get("ECC_DISABLED_HOOKS", "").split(",") if h]
    missing = [h for h in wanted_hooks if h not in existing]
    if missing:
        settings.setdefault("env", {})["ECC_DISABLED_HOOKS"] = ",".join(existing + missing)
        changes.append(f"env.ECC_DISABLED_HOOKS: add {len(missing)} hook id(s)")

    wanted_rules = [f"Skill(skill:ecc:{entry['name']})" for entry in overrides["skills"]]
    deny = settings.get("permissions", {}).get("deny", [])
    new_rules = [rule for rule in wanted_rules if rule not in deny]
    if new_rules:
        settings.setdefault("permissions", {}).setdefault("deny", []).extend(new_rules)
        changes.append(f"permissions.deny: add {len(new_rules)} skill rule(s)")

    return changes


def atomic_write(path: Path, data: dict) -> None:
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    args = parser.parse_args()

    overrides = json.loads(args.overrides.read_text(encoding="utf-8"))
    settings = json.loads(args.settings.read_text(encoding="utf-8")) if args.settings.exists() else {}

    changes = merge(settings, overrides)
    if not changes:
        print("no changes needed, overrides are already applied")
        return 0

    for change in changes:
        print(("would apply: " if args.dry_run else "applied: ") + change)
    if args.dry_run:
        return 0

    args.settings.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(args.settings, settings)
    print(f"wrote {args.settings}")
    print("Restart Claude Code sessions for the hook changes to take effect.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
