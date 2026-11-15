"""Validate the shipped terminal configs with the real tools where they are installed."""

import shutil
import subprocess
from pathlib import Path

import pytest

CONFIG = Path(__file__).resolve().parents[2] / "home" / "dot_config" / "welleng"


@pytest.mark.skipif(shutil.which("kitty") is None, reason="kitty not installed")
def test_kitty_config_loads_and_applies_values(tmp_path):
    code = (
        f"from kitty.config import load_config; o = load_config('{CONFIG / 'kitty' / 'welleng.conf'}'); "
        "print(o.scrollback_lines, o.copy_on_select, o.macos_option_as_alt)"
    )
    env = {"HOME": str(tmp_path), "XDG_CONFIG_HOME": str(tmp_path), "PATH": "/usr/bin:/bin"}
    out = subprocess.run([shutil.which("kitty"), "+runpy", code], capture_output=True, text=True, env=env, check=False, timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.split()[:2] == ["20000", "clipboard"]


@pytest.mark.skipif(shutil.which("yazi") is None, reason="yazi not installed")
def test_yazi_config_parses_without_errors(tmp_path):
    env = {"HOME": str(tmp_path), "YAZI_CONFIG_HOME": str(CONFIG / "yazi"), "PATH": "/usr/bin:/bin"}
    out = subprocess.run([shutil.which("yazi"), "--debug"], capture_output=True, text=True, env=env, check=False, timeout=60)
    text = out.stdout + out.stderr
    assert "invalid type" not in text and "unknown field" not in text and "expected" not in text, text


@pytest.mark.skipif(shutil.which("zsh") is None, reason="zsh not installed")
def test_init_zsh_parses():
    assert subprocess.run(["zsh", "-n", str(CONFIG / "shell" / "init.zsh")], check=False).returncode == 0


def test_global_claude_instructions_follow_the_rules():
    text = (CONFIG / "claude" / "CLAUDE.md").read_text(encoding="utf-8")
    assert chr(0x2014) not in text
    assert "@~/.config/welleng/claude/CLAUDE.md" in text
    assert "~/.claude/CLAUDE.md" in text
