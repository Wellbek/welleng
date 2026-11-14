#!/usr/bin/env python3
"""Install a pinned, checksum-verified release archive without root.

Usage:
    bootstrap/install_release.py NAME [--dest DIR] [--manifest FILE] [--dry-run]

NAME is looked up in packages/releases.toml, which scripts/pin-releases.py generates.
The download is refused unless it is https and its SHA-256 equals the pinned value.
Only the executables named in `members` are written, by base name, into DEST
(default ~/.local/bin), so a hostile archive cannot write anywhere else.
Exit codes: 0 installed or already current, 1 failure, 4 no pinned release for this platform.
Standard library only, Python 3.11 or newer.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import platform
import sys
import tarfile
import tomllib
import urllib.request
import zipfile
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "packages" / "releases.toml"
NO_RELEASE = 4


def platform_key() -> str:
    system = platform.system().lower()
    machine = {"amd64": "x86_64", "arm64": "aarch64"}.get(platform.machine().lower(), platform.machine().lower())
    return f"{system}-{machine}"


def extract(archive: bytes, url: str, members: list[str]) -> dict[str, bytes]:
    """Return {base name: bytes} for each wanted member, found anywhere in the archive."""
    found: dict[str, bytes] = {}
    if url.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            for info in z.infolist():
                base = Path(info.filename).name
                if not info.is_dir() and base in members and base not in found:
                    found[base] = z.read(info)
    else:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:*") as t:
            for info in t:
                base = Path(info.name).name
                if info.isfile() and base in members and base not in found:
                    handle = t.extractfile(info)
                    if handle is not None:
                        found[base] = handle.read()
    return found


def install(entry: dict, key: str, dest: Path, fetch=None, dry_run: bool = False) -> int:
    asset = entry.get("assets", {}).get(key)
    if asset is None:
        print(f"{entry['name']}: no pinned release for {key}", file=sys.stderr)
        return NO_RELEASE
    url, digest = asset["url"], asset["sha256"]
    if not url.startswith("https://"):
        print(f"{entry['name']}: refusing a non-https url", file=sys.stderr)
        return 1
    if dry_run:
        print(f"would install {entry['name']} {entry['version']} from {url} into {dest}")
        return 0
    fetch = fetch or _fetch
    data = fetch(url)
    actual = hashlib.sha256(data).hexdigest()
    if actual != digest:
        print(f"{entry['name']}: checksum mismatch, nothing installed (expected {digest}, got {actual})", file=sys.stderr)
        return 1
    files = extract(data, url, entry["members"])
    missing = set(entry["members"]) - set(files)
    if missing:
        print(f"{entry['name']}: archive lacks {sorted(missing)}, nothing installed", file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    for base, content in files.items():
        target = dest / base
        tmp = dest / f".{base}.tmp"
        tmp.write_bytes(content)
        os.chmod(tmp, 0o755)
        os.replace(tmp, target)
        print(f"installed: {target}")
    return 0


def _fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as response:  # noqa: S310 - https checked by caller
        return response.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("name")
    parser.add_argument("--dest", type=Path, default=Path.home() / ".local" / "bin")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    data = tomllib.loads(args.manifest.read_text(encoding="utf-8"))
    entry = next((r for r in data.get("release", []) if r["name"] == args.name), None)
    if entry is None:
        print(f"{args.name}: not in the release manifest", file=sys.stderr)
        return NO_RELEASE
    return install(entry, platform_key(), args.dest, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
