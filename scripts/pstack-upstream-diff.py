#!/usr/bin/env python3
"""List the upstream pstack changes since the commit the workflow layer was adapted from (ADR 0020).

    python3 -I scripts/pstack-upstream-diff.py [--to REF]

Reads claude-plugin/pstack-upstream.json for the repository, the studied commit and the map from each upstream file
to the local file adapted from it, then asks the GitHub compare API what changed under pstack/ up to REF
(default: the default branch). Each changed upstream file is printed with its local counterpart, or as "not adapted".
It reads only public data and changes nothing. It uses `gh api` when gh is installed, plain HTTPS otherwise.
After porting the changes you want, update "commit" in pstack-upstream.json.
Exit code 0 with no changes, 1 with changes, 2 on an error.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "claude-plugin" / "pstack-upstream.json"


def fetch(path: str) -> dict:
    if shutil.which("gh"):
        out = subprocess.run(["gh", "api", path], capture_output=True, text=True, check=False)
        if out.returncode == 0:
            return json.loads(out.stdout)
    request = urllib.request.Request(f"https://api.github.com/{path}", headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def changes(upstream: dict, compare: dict) -> list[str]:
    lines = []
    for item in compare.get("files", []):
        name = item["filename"]
        if not name.startswith("pstack/"):
            continue
        local = upstream["files"].get(name) or upstream["files"].get(item.get("previous_filename", ""))
        target = local if local else "not adapted"
        lines.append(f"{item['status']:<9} {name} -> {target}")
    return lines


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--to", default=None, help="upstream ref to compare against, default: the default branch")
    args = parser.parse_args(argv)
    upstream = json.loads(MAP.read_text(encoding="utf-8"))
    repo, base = upstream["repository"], upstream["commit"]
    try:
        head = args.to or fetch(f"repos/{repo}")["default_branch"]
        compare = fetch(f"repos/{repo}/compare/{base}...{head}")
    except (OSError, ValueError, KeyError) as e:
        print(f"pstack-upstream-diff: {e}", file=sys.stderr)
        return 2
    lines = changes(upstream, compare)
    print(f"{repo} {base[:12]}...{head}: {compare.get('ahead_by', 0)} commit(s) ahead, {len(lines)} pstack file(s) changed")
    for line in lines:
        print(line)
    if len(compare.get("files", [])) >= 300:
        print("note: GitHub lists at most 300 files per comparison, compare a nearer ref with --to", file=sys.stderr)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
