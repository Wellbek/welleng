import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

from welleng import up

needs_tmux = pytest.mark.skipif(shutil.which("tmux") is None, reason="tmux is not installed")


def test_session_name():
    assert up.session_name(Path("/x/My Project.v2")) == "My-Project-v2"
    assert up.session_name(Path("/")) == "project"


def test_missing_tools_degrade_to_a_shell():
    cmds = up.window_commands(have=lambda name: None)
    assert all(v is None for v in cmds.values())
    cmds = up.window_commands(have=lambda name: "/bin/x")
    assert cmds["git"] == "lazygit" and "welleng agents" in cmds["agents"]


@needs_tmux
def test_creates_four_windows_and_reuses_the_session(tmp_path):
    socket = f"welleng-test-{uuid.uuid4().hex[:8]}"
    proj = tmp_path / "demo"
    proj.mkdir()
    try:
        assert up.up(proj, socket=socket, attach=False) == 0
        out = subprocess.run(["tmux", "-L", socket, "list-windows", "-t", "=demo", "-F", "#{window_name}"], capture_output=True, text=True, check=True).stdout.split()
        assert out == list(up.WINDOWS)
        assert up.up(proj, socket=socket, attach=False) == 0  # second call must not duplicate windows
        again = subprocess.run(["tmux", "-L", socket, "list-windows", "-t", "=demo"], capture_output=True, text=True, check=True).stdout.splitlines()
        assert len(again) == 4
        pane = subprocess.run(["tmux", "-L", socket, "display", "-p", "-t", "=demo:shell", "#{pane_current_path}"], capture_output=True, text=True, check=True).stdout.strip()
        assert Path(pane).resolve() == proj.resolve()
    finally:
        subprocess.run(["tmux", "-L", socket, "kill-server"], capture_output=True, check=False)


def test_not_a_directory(tmp_path, capsys):
    assert up.up(tmp_path / "nope", socket="x", attach=False) == 1
