"""Entry point of the `welleng` command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import doctor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="welleng")
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("doctor", help="report mandatory, recommended and optional components")
    d.add_argument("--packages", type=Path, default=None, help="path to packages.toml")
    args = parser.parse_args(argv)

    if args.command == "doctor":
        components = doctor.load_components(args.packages or doctor.default_packages_path())
        print(doctor.render(components))
        return doctor.exit_code(components)
    return 2


if __name__ == "__main__":
    sys.exit(main())
