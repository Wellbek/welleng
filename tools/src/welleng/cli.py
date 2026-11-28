"""Entry point of the `welleng` command."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from . import agents, doctor, harness, hints, keys, rc, repos, ssh, up, update


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="welleng")
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("doctor", help="report mandatory, recommended and optional components")
    d.add_argument("--packages", type=Path, default=None, help="path to packages.toml")
    d.add_argument("--claude", action="store_true", help="also report Claude Code plugins, versions and context cost")
    k = sub.add_parser("keys", help="searchable tmux keybinding cheatsheet")
    k.add_argument("pattern", nargs="?", help="only bindings containing this text")
    k.add_argument("--tmux-conf", type=Path, default=Path.home() / ".tmux.conf")
    r = sub.add_parser("repos", help="branch and change overview of the git repositories under a root")
    r.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    a = sub.add_parser("agents", help="central view of Claude Code sessions")
    a.add_argument("--count", action="store_true", help="print only the number of sessions waiting for you")
    s = sub.add_parser("ssh", help="machine registry on top of the OpenSSH config")
    s.add_argument("--dir", type=Path, default=None, help="fragment directory, default ~/.ssh/config.d")
    ss = s.add_subparsers(dest="action", required=True)
    ss.add_parser("ls")
    sa = ss.add_parser("add")
    sa.add_argument("name")
    sa.add_argument("hostname")
    sa.add_argument("--user")
    sa.add_argument("--port", type=int)
    sa.add_argument("--identity", help="path to a private key, only the path is stored")
    sa.add_argument("--jump")
    sa.add_argument("--description")
    sr = ss.add_parser("rm")
    sr.add_argument("name")
    sm = ss.add_parser("migrate", help="add the Include line for config.d to ~/.ssh/config, dry run unless --yes")
    sm.add_argument("--yes", action="store_true")
    sm.add_argument("--undo", action="store_true", help="remove the block added by an earlier migrate")
    sm.add_argument("--config", type=Path, default=None, help="main config file, default ~/.ssh/config")
    up2 = sub.add_parser("update", help="pull the repository, show the changes, then apply the owned config directories")
    up2.add_argument("--repo", type=Path, default=None, help="repository path, default $WELLENG_REPO or the chezmoi source")
    up2.add_argument("--yes", action="store_true", help="apply, without it nothing changes")
    u = sub.add_parser("up", help="open or attach to the project tmux session")
    u.add_argument("path", nargs="?", type=Path, default=Path.cwd())
    u.add_argument("--no-attach", action="store_true", help="create the session and print its name")
    u.add_argument("--socket", help="tmux socket name, for tests")
    r2 = sub.add_parser("rc", help="start Remote Control in a tmux window, or check the listening ports")
    r2.add_argument("--name")
    r2.add_argument("--ports", choices=["snapshot", "diff"], help="snapshot listeners before starting, diff afterwards")
    hi = sub.add_parser("hints", help="control and review effort recommendations")
    hi.add_argument("action", choices=["snooze", "off", "on", "report"])
    hi.add_argument("--hours", type=float, default=4)
    h = sub.add_parser("harness", help="plan, apply and check a project's Claude Code configuration")
    hs = h.add_subparsers(dest="action", required=True)
    for action in ("plan", "apply"):
        sp = hs.add_parser(action)
        sp.add_argument("spec", type=Path)
        sp.add_argument("--project", type=Path, default=Path.cwd())
        if action == "apply":
            sp.add_argument("--yes", action="store_true", help="required, the plan must have been approved")
    hc = hs.add_parser("check")
    hc.add_argument("project", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    if args.command == "doctor":
        components = doctor.load_components(args.packages or doctor.default_packages_path())
        print(doctor.render(components))
        if args.claude:
            print(doctor.render_plugins(doctor.load_plugins(), doctor.plugin_version_in_repo()))
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
    if args.command == "agents":
        try:
            found = agents.fetch()
        except agents.AgentsError as e:
            if args.count:
                print("?")
                return 0
            print(f"agents: {e}", file=sys.stderr)
            return 1
        print(agents.waiting_count(found) if args.count else agents.render(agents.enrich(found)))
        return 0
    if args.command == "update":
        repo = args.repo or (Path(os.environ["WELLENG_REPO"]) if os.environ.get("WELLENG_REPO") else _chezmoi_repo())
        if repo is None or not (repo / ".git").exists():
            print("update: give the repository with --repo or WELLENG_REPO", file=sys.stderr)
            return 1
        return update.run(repo.resolve(), Path.home(), args.yes)
    if args.command == "up":
        return up.up(args.path, socket=args.socket, attach=not args.no_attach)
    if args.command == "rc":
        if args.ports:
            directory = hints.state_dir()
            try:
                current = rc.listeners()
            except RuntimeError as e:
                print(f"rc: {e}", file=sys.stderr)
                return 1
            if args.ports == "snapshot":
                rc.save_snapshot(directory, current)
                print(f"recorded {len(current)} listening sockets")
                return 0
            if not rc.snapshot_path(directory).is_file():
                print("rc: no snapshot, run `welleng rc --ports snapshot` first", file=sys.stderr)
                return 1
            loopback, tailnet, exposed = rc.diff(directory, current)
            for a in loopback:
                print(f"new loopback listener: {a}")
            for a in tailnet:
                print(f"new tailnet-only listener: {a}")
            for a in exposed:
                print(f"NEW EXPOSED LISTENER: {a}")
            print("ports check: ok" if not exposed else "ports check: FAILED, something is listening on a non-loopback address")
            return 1 if exposed else 0
        return rc.start(args.name)
    if args.command == "hints":
        directory = hints.state_dir()
        if args.action == "snooze":
            hints.snooze(directory, args.hours)
            print(f"hints snoozed for {args.hours:g} hours")
        elif args.action in ("off", "on"):
            hints.set_off(directory, args.action == "off")
            print(f"hints {args.action}")
        else:
            print(hints.report(directory))
        return 0
    if args.command == "ssh":
        directory = args.dir or ssh.default_dir()
        try:
            if args.action == "ls":
                main_config = Path.home() / ".ssh" / "config" if args.dir is None else None
                print(ssh.render(ssh.list_hosts(directory, main_config)))
            elif args.action == "migrate":
                config = args.config or Path.home() / ".ssh" / "config"
                print((ssh.unmigrate if args.undo else ssh.migrate)(config, args.yes))
            elif args.action == "add":
                path = ssh.add(directory, args.name, args.hostname, args.user, args.port, args.identity, args.jump, args.description,
                               Path.home() / ".ssh" / "config" if args.dir is None else None)
                print(f"wrote {path}")
            else:
                print(f"removed {ssh.remove(directory, args.name)}")
        except ssh.SshError as e:
            print(f"ssh: {e}", file=sys.stderr)
            return 1
        return 0
    if args.command == "harness":
        return _harness(args)
    return 2


def _chezmoi_repo() -> Path | None:
    """The repository root behind chezmoi's source directory (.chezmoiroot points at home/)."""
    try:
        out = subprocess.run(["chezmoi", "source-path"], capture_output=True, text=True, check=False).stdout.strip()
    except FileNotFoundError:
        return None
    if not out:
        return None
    path = Path(out)
    return path.parent if path.name == "home" else path


def _harness(args) -> int:
    if args.action == "check":
        problems = harness.check(args.project.resolve())
        for p in problems:
            print(p)
        for note in harness.notes(args.project.resolve()):
            print(f"note: {note}")
        print("harness check: ok" if not problems else f"harness check: {len(problems)} problem(s)")
        return 1 if problems else 0
    root = args.project.resolve()
    try:
        changes = harness.plan(json.loads(args.spec.read_text(encoding="utf-8")), root)
    except (harness.SpecError, json.JSONDecodeError, OSError) as e:
        print(f"harness: {e}", file=sys.stderr)
        return 1
    if not changes:
        print("nothing to change")
        return 0
    if args.action == "plan" or not args.yes:
        for c in changes:
            print(c.diff(root))
        if args.action == "apply":
            print("not applied: pass --yes after reviewing the plan", file=sys.stderr)
            return 1
        return 0
    harness.apply(changes)
    for c in changes:
        print(f"wrote {c.path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
