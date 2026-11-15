"""OpenSSH config as the machine registry (ADR 0007).

Hosts added here become one fragment per host in ~/.ssh/config.d/, so `ssh NAME` works without this
project. Hand-written entries are listed but never modified or removed.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

MARKER = "# managed by welleng"
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
VALUE_RE = re.compile(r"^[^\s#\"'\\]+$")


class SshError(ValueError):
    """Invalid input or a refused change."""


@dataclass(frozen=True)
class Host:
    name: str
    hostname: str
    user: str
    port: str
    managed: bool
    source: Path


def default_dir() -> Path:
    return Path.home() / ".ssh" / "config.d"


def parse(text: str, source: Path) -> list[Host]:
    managed = MARKER in text.splitlines()[:2]
    hosts: list[Host] = []
    current: dict[str, str] | None = None

    def flush() -> None:
        if current and "*" not in current["name"] and "?" not in current["name"]:
            hosts.append(Host(current["name"], current.get("hostname", ""), current.get("user", ""), current.get("port", ""), managed, source))

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition(" ")
        key, value = key.lower(), value.strip()
        if key == "host":
            flush()
            current = {"name": value.split()[0] if value else ""}
        elif current is not None and key in ("hostname", "user", "port"):
            current[key] = value
    flush()
    return hosts


def list_hosts(config_dir: Path, main_config: Path | None = None) -> list[Host]:
    hosts: list[Host] = []
    for path in ([main_config] if main_config and main_config.is_file() else []) + sorted(config_dir.glob("*.conf")):
        hosts += parse(path.read_text(encoding="utf-8"), path)
    return hosts


def add(config_dir: Path, name: str, hostname: str, user: str | None = None, port: int | None = None,
        identity: str | None = None, jump: str | None = None, description: str | None = None,
        main_config: Path | None = None) -> Path:
    if not NAME_RE.match(name):
        raise SshError("name may contain letters, digits, dot, dash and underscore only")
    for label, value in (("host", hostname), ("user", user), ("identity file", identity), ("jump host", jump)):
        if value is not None and not VALUE_RE.match(value):
            raise SshError(f"invalid {label}: no whitespace, quotes, backslashes or comments allowed")
    if port is not None and not 1 <= port <= 65535:
        raise SshError("port must be between 1 and 65535")
    if description is not None and ("\n" in description or "\r" in description):
        raise SshError("description must be one line")
    if any(h.name == name for h in list_hosts(config_dir, main_config)):
        raise SshError(f"a host named {name} already exists")
    lines = [MARKER]
    if description:
        lines.append(f"# {description}")
    lines += [f"Host {name}", f"    HostName {hostname}"]
    if user:
        lines.append(f"    User {user}")
    if port:
        lines.append(f"    Port {port}")
    if identity:
        lines.append(f"    IdentityFile {identity}")
    if jump:
        lines.append(f"    ProxyJump {jump}")
    config_dir.mkdir(parents=True, exist_ok=True)
    target = config_dir / f"{name}.conf"
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return target


def remove(config_dir: Path, name: str) -> Path:
    if not NAME_RE.match(name):
        raise SshError("invalid name")
    target = config_dir / f"{name}.conf"
    if not target.is_file():
        raise SshError(f"no fragment for {name}, hand-written entries are never removed by welleng")
    if MARKER not in target.read_text(encoding="utf-8").splitlines()[:2]:
        raise SshError(f"{target.name} was not created by welleng, refusing to remove it")
    target.unlink()
    return target


INCLUDE_LINE = "Include config.d/*.conf"
INCLUDE_RE = re.compile(r"^\s*include\s+(?:.*\s)?(?:~/\.ssh/|\.ssh/)?config\.d/\*(?:\.conf)?\s*$", re.IGNORECASE)


def _migrated_text(text: str) -> str:
    return f"{MARKER}\n{INCLUDE_LINE}\n\n{text}"


def migrate(main_config: Path, apply: bool) -> str:
    """Add `Include config.d/*.conf` at the very top of the main config, once.

    The line must come first: an Include inside a Host or Match block would only apply to that
    block. Without --yes nothing is written. The previous file is kept next to it as a backup.
    """
    text = main_config.read_text(encoding="utf-8") if main_config.is_file() else ""
    if any(INCLUDE_RE.match(line) for line in text.splitlines()):
        return "already includes config.d, nothing to do"
    if not apply:
        return f"would add this at the top of {main_config}:\n  {INCLUDE_LINE}\nrun again with --yes to apply, a backup is kept"
    main_config.parent.mkdir(parents=True, exist_ok=True)
    target = main_config.resolve()
    if main_config.is_file():
        backup = target.with_name(target.name + ".welleng-backup")
        if not backup.exists():
            backup.write_text(text, encoding="utf-8")
            backup.chmod(0o600)
    tmp = target.with_name(target.name + ".welleng-tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(_migrated_text(text))
    os.replace(tmp, target)
    return f"added the Include line to {main_config}, previous file kept as {target.name}.welleng-backup"


def unmigrate(main_config: Path, apply: bool) -> str:
    """Remove exactly the block that `migrate` added, and nothing else."""
    block = f"{MARKER}\n{INCLUDE_LINE}\n\n"
    text = main_config.read_text(encoding="utf-8") if main_config.is_file() else ""
    if not text.startswith(block):
        return "no welleng Include block at the top, nothing to do"
    if not apply:
        return "would remove the welleng Include block, run again with --yes"
    target = main_config.resolve()
    target.write_text(text[len(block):], encoding="utf-8")
    return "removed the welleng Include block"


def render(hosts: list[Host]) -> str:
    if not hosts:
        return "no hosts"
    rows = [("name", "host", "user", "port", "source")]
    rows += [(h.name, h.hostname or "-", h.user or "-", h.port or "-", "welleng" if h.managed else "manual") for h in hosts]
    widths = [max(len(r[i]) for r in rows) for i in range(5)]
    return "\n".join("  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip() for r in rows)
