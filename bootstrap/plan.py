#!/usr/bin/env python3
"""Turn packages/packages.toml into an install plan for one package manager.

Usage:
    bootstrap/plan.py MANAGER [--tiers mandatory,recommended]

MANAGER is pacman, apt, dnf, brew, winget or scoop.
Every package whose executable is already on PATH is skipped.
Output is one tab-separated line per action:
    pkg          NAME  ID        install NAME with the package manager
    fallback     NAME  SOURCE    no package id, install from SOURCE, see the installer
    unavailable  NAME  NOTE      no package and no fallback on this platform
Pure standard library, Python 3.11 or newer, reads nothing but the package map and PATH.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tomllib
from pathlib import Path

PACKAGES = Path(__file__).resolve().parent.parent / "packages" / "packages.toml"
MANAGERS = ("pacman", "apt", "dnf", "brew", "winget", "scoop")


def plan(data: dict, manager: str, tiers: set[str]) -> list[tuple[str, str, str]]:
    actions = []
    for entry in data["package"]:
        if entry["tier"] not in tiers:
            continue
        bins = entry.get("bins", [entry["name"]])
        if any(shutil.which(b) for b in bins):
            continue
        name = entry["name"]
        if manager in entry:
            actions.append(("pkg", name, entry[manager]))
        elif "fallback" in entry:
            actions.append(("fallback", name, entry["fallback"]))
        else:
            actions.append(("unavailable", name, entry.get("note", "no package for this platform")))
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manager", choices=MANAGERS)
    parser.add_argument("--tiers", default="mandatory,recommended")
    parser.add_argument("--packages", type=Path, default=PACKAGES)
    args = parser.parse_args()
    tiers = set(args.tiers.split(","))
    if not tiers <= {"mandatory", "recommended", "optional"}:
        parser.error("tiers must be a subset of mandatory,recommended,optional")
    data = tomllib.loads(args.packages.read_text(encoding="utf-8"))
    for kind, name, value in plan(data, args.manager, tiers):
        print(f"{kind}\t{name}\t{value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
