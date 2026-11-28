#!/usr/bin/env python3
"""Point the Claude Code status line at the Well-Engineering status line script of this clone.

Usage:
    scripts/enable-statusline.py [--dry-run] [--remove] [--force] [--settings PATH]

It sets only the `statusLine` key of the user settings, keeps every other key untouched, and writes atomically.
A status line that points at an older path of the same script is updated.
Any other existing status line is kept unless --force is given, because it would be replaced.
Running it twice changes nothing the second time.
Python 3.11 or newer, standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "claude-plugin-hooks" / "hooks" / "statusline.py"
DEFAULT_SETTINGS = Path.home() / ".claude" / "settings.json"


def wanted(script: Path = SCRIPT) -> dict:
    return {"type": "command", "command": f"python3 -I {shlex.quote(str(script))}"}


def is_ours(entry: object) -> bool:
    """True for a status line that runs a welleng statusline.py, at this or an older path."""
    if not isinstance(entry, dict):
        return False
    command = str(entry.get("command", ""))
    return command.endswith("/hooks/statusline.py") and "welleng" in command


def merge(settings: dict, remove: bool, force: bool, target: dict) -> str | None:
    """Change `settings` in place and return a description, or None when nothing changes.

    Raises ValueError when a foreign status line would be replaced without --force.
    """
    current = settings.get("statusLine")
    if remove:
        if current is None:
            return None
        if not is_ours(current) and not force:
            raise ValueError("the status line is not the welleng one, pass --force to remove it anyway")
        del settings["statusLine"]
        return "statusLine: removed"
    if current == target:
        return None
    if current is not None and not is_ours(current) and not force:
        raise ValueError(
            "a different status line is already set, pass --force to replace it,"
            f" or call {SCRIPT} from your own status line script"
        )
    settings["statusLine"] = target
    return f"statusLine: {'update' if current else 'set'} to {target['command']}"


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="show the change, write nothing")
    parser.add_argument("--remove", action="store_true", help="remove the welleng status line")
    parser.add_argument("--force", action="store_true", help="replace or remove a status line that is not the welleng one")
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    args = parser.parse_args(argv)

    if not args.remove and not SCRIPT.is_file():
        print(f"enable-statusline: {SCRIPT} is missing", file=sys.stderr)
        return 1
    try:
        settings = json.loads(args.settings.read_text(encoding="utf-8")) if args.settings.exists() else {}
    except json.JSONDecodeError as exc:
        print(f"enable-statusline: {args.settings} is not valid JSON, nothing written: {exc}", file=sys.stderr)
        return 1
    try:
        change = merge(settings, args.remove, args.force, wanted())
    except ValueError as exc:
        print(f"enable-statusline: {exc}", file=sys.stderr)
        return 1
    if change is None:
        print("nothing to change")
        return 0
    print(change)
    if args.dry_run:
        print("dry run: nothing was written")
        return 0
    args.settings.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(args.settings, settings)
    print(f"wrote {args.settings}, restart Claude Code sessions to load it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
