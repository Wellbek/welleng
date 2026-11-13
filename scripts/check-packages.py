#!/usr/bin/env python3
"""Check packages/packages.toml against a real package manager.

Usage:
    scripts/check-packages.py MANAGER [--tier mandatory|recommended|optional]

MANAGER is pacman, apt or dnf.
For every package that names an id for that manager, the id is looked up in the manager's
repositories, and a missing id is an error.
A mandatory package that has neither an id for the manager nor a fallback is also an error,
because the installer would have no way to provide it.
brew, winget and scoop are reported as not checked.
Python 3.11 or newer, standard library only.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

PACKAGES = Path(__file__).resolve().parent.parent / "packages" / "packages.toml"
UNCHECKED = {"brew", "winget", "scoop"}


def lookup(manager: str, package_id: str) -> bool:
    """Return True when the repositories of `manager` know `package_id`."""
    if manager == "pacman":
        cmd = ["pacman", "-Si", package_id]
    elif manager == "apt":
        cmd = ["apt-cache", "show", package_id]
    elif manager == "dnf":
        cmd = ["dnf", "-q", "repoquery", "--available", package_id]
    else:
        raise ValueError(manager)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if manager == "dnf":
        return result.returncode == 0 and bool(result.stdout.strip())
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manager", choices=sorted({"pacman", "apt", "dnf"} | UNCHECKED))
    parser.add_argument("--tier", choices=["mandatory", "recommended", "optional"])
    args = parser.parse_args()

    if args.manager in UNCHECKED:
        print(f"{args.manager}: ids are not checked yet, see CHECKLIST.md")
        return 0

    data = tomllib.loads(PACKAGES.read_text(encoding="utf-8"))
    errors = 0
    checked = 0
    for entry in data["package"]:
        if args.tier and entry["tier"] != args.tier:
            continue
        name = entry["name"]
        package_id = entry.get(args.manager)
        if package_id is None:
            if entry["tier"] == "mandatory" and "fallback" not in entry:
                print(f"ERROR  {name}: mandatory, no {args.manager} id and no fallback")
                errors += 1
            else:
                reason = "fallback" if "fallback" in entry else "not available"
                print(f"skip   {name}: no {args.manager} id ({reason})")
            continue
        checked += 1
        if lookup(args.manager, package_id):
            print(f"ok     {name}: {package_id}")
        else:
            print(f"ERROR  {name}: {package_id} not found by {args.manager}")
            errors += 1

    print(f"\n{args.manager}: {checked} ids checked, {errors} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
