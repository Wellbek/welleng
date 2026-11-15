"""Pull the Well-Engineering repository, show what changed, then apply a limited chezmoi scope.

Nothing changes without --yes. The apply step only covers the directories this project owns under
~/.config, never the whole source state, so a pull cannot overwrite an existing tmux or git config.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

APPLY_TARGETS = (".config/welleng", ".config/welleng-nvim")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)


def incoming(repo: Path) -> tuple[list[str], str]:
    """Fetch, then return (commit subjects not yet applied, diffstat)."""
    fetched = git(repo, "fetch", "--quiet")
    if fetched.returncode != 0:
        raise RuntimeError("git fetch failed: " + fetched.stderr.strip())
    log = git(repo, "log", "--format=%h %s", "HEAD..@{u}")
    if log.returncode != 0:
        raise RuntimeError("the current branch has no upstream")
    stat = git(repo, "diff", "--stat", "HEAD..@{u}").stdout.strip()
    return [line for line in log.stdout.splitlines() if line], stat


def chezmoi_args(repo: Path, home: Path) -> list[str]:
    return [str(home / target) for target in APPLY_TARGETS]


def run(repo: Path, home: Path, yes: bool) -> int:
    if git(repo, "status", "--porcelain").stdout.strip():
        print("update: the repository has uncommitted changes, commit or stash them first")
        return 1
    try:
        commits, stat = incoming(repo)
    except RuntimeError as e:
        print(f"update: {e}")
        return 1
    if commits:
        print(f"{len(commits)} new commit(s):")
        print("\n".join(f"  {c}" for c in commits))
        print(stat)
    else:
        print("repository is up to date")
    have_chezmoi = shutil.which("chezmoi") is not None
    base = ["chezmoi", "--source", str(repo), "--destination", str(home)]
    if have_chezmoi:
        drift = subprocess.run([*base, "diff", "--exclude=externals", *chezmoi_args(repo, home)], capture_output=True, text=True, check=False)
        print("deployed files differ from the repository:" if drift.stdout.strip() else "deployed files match the repository")
        if drift.stdout.strip():
            print(drift.stdout)
    else:
        print("chezmoi is not installed, only the repository will be updated")
    if not yes:
        print("dry run: nothing was changed, rerun with --yes")
        return 0
    if commits:
        pulled = git(repo, "pull", "--ff-only", "--quiet")
        if pulled.returncode != 0:
            print("update: git pull --ff-only failed: " + pulled.stderr.strip())
            return 1
    if have_chezmoi:
        applied = subprocess.run([*base, "apply", "--exclude=externals", *chezmoi_args(repo, home)], check=False)
        return applied.returncode
    return 0
