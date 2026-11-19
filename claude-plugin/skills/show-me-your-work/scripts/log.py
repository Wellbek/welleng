#!/usr/bin/env python3
"""Append one row to a decision log in TSV form.

    python3 -I log.py LOGFILE PHASE DECISION WHY EVIDENCE RESULT

Stamps the time in UTC, writes the header on first use, turns tabs and newlines inside a cell into spaces,
and prefixes a cell that starts with =, +, - or @ with a quote so a spreadsheet never runs it as a formula.
Standard library only.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

HEADER = ["ts", "phase", "decision", "why", "evidence", "result"]


def cell(value: str) -> str:
    value = " ".join(value.replace("\t", " ").splitlines()).strip()
    return "'" + value if value[:1] in ("=", "+", "-", "@") else value


def main(argv: list[str]) -> int:
    if len(argv) != 7:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    log = Path(argv[1])
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = [stamp, *(cell(v) for v in argv[2:])]
    new = not log.exists() or log.stat().st_size == 0
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        if new:
            fh.write("\t".join(HEADER) + "\n")
        fh.write("\t".join(row) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
