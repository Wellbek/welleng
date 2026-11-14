"""Overview of the git repositories under a root directory."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

SKIP = {"node_modules", ".venv", "venv", "target", "__pycache__"}


@dataclass(frozen=True)
class RepoStatus:
    path: Path
    branch: str
    staged: int
    unstaged: int
    untracked: int
    ahead: int
    behind: int
    last_commit: str


def find_repos(root: Path, max_depth: int = 2) -> list[Path]:
    """Directories holding a .git entry, at most max_depth levels below root, root included."""
    found: list[Path] = []

    def walk(directory: Path, depth: int) -> None:
        if (directory / ".git").exists():
            found.append(directory)
            return
        if depth >= max_depth:
            return
        try:
            children = sorted(p for p in directory.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name not in SKIP)
        except OSError:
            return
        for child in children:
            walk(child, depth + 1)

    walk(root, 0)
    return found


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True, check=False)
    return result.stdout if result.returncode == 0 else ""


def parse_status(text: str) -> tuple[str, int, int, int, int, int]:
    """Parse `git status --porcelain=v2 --branch` into branch, staged, unstaged, untracked, ahead, behind."""
    branch, staged, unstaged, untracked, ahead, behind = "?", 0, 0, 0, 0, 0
    for line in text.splitlines():
        if line.startswith("# branch.head "):
            branch = line.split(" ", 2)[2]
        elif line.startswith("# branch.ab "):
            plus, minus = line.split()[2:4]
            ahead, behind = int(plus[1:]), int(minus[1:])
        elif line[:2] in ("1 ", "2 "):
            xy = line.split(" ", 2)[1]
            staged += xy[0] != "."
            unstaged += xy[1] != "."
        elif line.startswith("u "):
            unstaged += 1
        elif line.startswith("? "):
            untracked += 1
    return branch, staged, unstaged, untracked, ahead, behind


def status(path: Path) -> RepoStatus:
    branch, staged, unstaged, untracked, ahead, behind = parse_status(_git(path, "status", "--porcelain=v2", "--branch"))
    last = _git(path, "log", "-1", "--format=%cr").strip() or "no commits"
    return RepoStatus(path, branch, staged, unstaged, untracked, ahead, behind, last)


def render(root: Path, statuses: list[RepoStatus]) -> str:
    if not statuses:
        return f"no git repositories under {root}"
    rows = [("repository", "branch", "S", "U", "?", "ahead", "behind", "last commit")]
    for s in statuses:
        try:
            name = str(s.path.relative_to(root)) if s.path != root else s.path.name
        except ValueError:
            name = str(s.path)
        rows.append((name, s.branch, str(s.staged), str(s.unstaged), str(s.untracked), str(s.ahead), str(s.behind), s.last_commit))
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    return "\n".join("  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip() for r in rows)


def overview(root: Path) -> str:
    return render(root, [status(p) for p in find_repos(root)])
