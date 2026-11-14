"""Entry point of the `welleng` command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import doctor, keys, repos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="welleng")
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("doctor", help="report mandatory, recommended and optional components")
    d.add_argument("--packages", type=Path, default=None, help="path to packages.toml")
    k = sub.add_parser("keys", help="searchable tmux keybinding cheatsheet")
    k.add_argument("pattern", nargs="?", help="only bindings containing this text")
    k.add_argument("--tmux-conf", type=Path, default=Path.home() / ".tmux.conf")
    r = sub.add_parser("repos", help="branch and change overview of the git repositories under a root")
    r.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    if args.command == "doctor":
        components = doctor.load_components(args.packages or doctor.default_packages_path())
        print(doctor.render(components))
        return doctor.exit_code(components)
    if args.command == "keys":
        if not args.tmux_conf.is_file():
            print(f"no tmux configuration at {args.tmux_conf}", file=sys.stderr)
            return 1
        print(keys.render(keys.load(args.tmux_conf), args.pattern))
        return 0
    if args.command == "repos":
        if not args.root.is_dir():
            print(f"not a directory: {args.root}", file=sys.stderr)
            return 1
        print(repos.overview(args.root.resolve()))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
