import os
import stat
import subprocess
from pathlib import Path

from welleng import cli, update

ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}


def git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True, env={**os.environ, **ENV})


def git_only_path(tmp_path: Path) -> str:
    """A PATH holding git and nothing else, so no real chezmoi is found whatever the machine has installed."""
    import shutil

    directory = tmp_path / "git-only-bin"
    directory.mkdir(exist_ok=True)
    link = directory / "git"
    if not link.exists():
        link.symlink_to(shutil.which("git"))
    return str(directory)


def make_pair(tmp_path: Path):
    origin = tmp_path / "origin"
    origin.mkdir()
    git(origin, "init", "-q", "-b", "main")
    (origin / "a").write_text("1")
    git(origin, "add", "a")
    git(origin, "commit", "-q", "-m", "first")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, capture_output=True)
    return origin, clone


def test_up_to_date_and_dry_run(tmp_path, capsys, monkeypatch):
    _, clone = make_pair(tmp_path)
    monkeypatch.setenv("PATH", git_only_path(tmp_path))
    assert update.run(clone, tmp_path / "home", yes=False) == 0
    out = capsys.readouterr().out
    assert "up to date" in out and "dry run" in out


def test_new_commits_are_shown_then_pulled_only_with_yes(tmp_path, capsys, monkeypatch):
    origin, clone = make_pair(tmp_path)
    (origin / "b").write_text("2")
    git(origin, "add", "b")
    git(origin, "commit", "-q", "-m", "second change")
    monkeypatch.setenv("PATH", git_only_path(tmp_path))
    assert update.run(clone, tmp_path / "home", yes=False) == 0
    assert "second change" in capsys.readouterr().out
    assert not (clone / "b").exists()
    assert update.run(clone, tmp_path / "home", yes=True) == 0
    assert (clone / "b").exists()


def test_dirty_repository_is_refused(tmp_path, capsys):
    _, clone = make_pair(tmp_path)
    (clone / "a").write_text("changed")
    assert update.run(clone, tmp_path / "home", yes=True) == 1
    assert "uncommitted" in capsys.readouterr().out


def test_chezmoi_scope_is_limited_to_owned_directories(tmp_path, monkeypatch):
    origin, clone = make_pair(tmp_path)
    fake = tmp_path / "bin"
    fake.mkdir()
    log = tmp_path / "calls.txt"
    script = fake / "chezmoi"
    script.write_text(f'#!/bin/sh\necho "$@" >> {log}\n')
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{fake}:/usr/bin:/bin")
    home = tmp_path / "home"
    assert update.run(clone, home, yes=True) == 0
    calls = log.read_text()
    assert str(home / ".config" / "welleng") in calls and "apply" in calls
    assert ".tmux.conf" not in calls and ".gitconfig" not in calls


def test_cli_update_reports_error_without_upstream(tmp_path, capsys):
    solo = tmp_path / "solo"
    solo.mkdir()
    git(solo, "init", "-q", "-b", "main")
    (solo / "a").write_text("x")
    git(solo, "add", "a")
    git(solo, "commit", "-q", "-m", "x")
    assert cli.main(["update", "--repo", str(solo)]) == 1


def test_dry_run_reports_drift_inside_deployed_directories_with_real_chezmoi(tmp_path, capsys):
    # `chezmoi diff` does not recurse into a directory target unless asked, unlike `apply` and `status`.
    import shutil

    import pytest

    if shutil.which("chezmoi") is None:
        pytest.skip("chezmoi not installed")
    origin, clone = make_pair(tmp_path)
    (clone / ".chezmoiroot").write_text("home\n")
    source = clone / "home" / "dot_config" / "welleng" / "claude"
    source.mkdir(parents=True)
    (source / "CLAUDE.md").write_text("old\n")
    (clone / "home" / "dot_config" / "welleng-nvim").mkdir()
    (clone / "home" / "dot_config" / "welleng-nvim" / "init.lua").write_text("-- nvim\n")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "add source")
    home = tmp_path / "home"
    deployed = home / ".config" / "welleng" / "claude" / "CLAUDE.md"
    deployed.parent.mkdir(parents=True)
    deployed.write_text("old\n")
    (home / ".config" / "welleng-nvim").mkdir()
    (home / ".config" / "welleng-nvim" / "init.lua").write_text("-- nvim\n")
    assert update.run(clone, home, yes=False) == 0
    assert "deployed files match the repository" in capsys.readouterr().out
    (source / "CLAUDE.md").write_text("new\n")
    git(clone, "commit", "-q", "-am", "change source")
    assert update.run(clone, home, yes=False) == 0
    assert "deployed files differ from the repository" in capsys.readouterr().out
    assert deployed.read_text() == "old\n"
