import pytest

from welleng import cli, rc

SS = """LISTEN 0 4096 127.0.0.1:8080 0.0.0.0:*
LISTEN 0 4096 0.0.0.0:22 0.0.0.0:*
LISTEN 0 4096 [::1]:631 [::]:*
"""


def test_window_command_is_a_detached_tmux_window_with_safe_mode():
    cmd = rc.window_command("my box")
    assert cmd[:5] == ["tmux", "new-window", "-d", "-n", "rc"]
    assert "--permission-mode default" in cmd[5] and "'my box'" in cmd[5]


def test_bypass_is_refused():
    with pytest.raises(ValueError):
        rc.window_command(None, "bypassPermissions")


def test_parse_and_loopback():
    assert rc.parse_listeners(SS) == {"127.0.0.1:8080", "0.0.0.0:22", "[::1]:631"}
    assert rc.is_loopback("127.0.0.1:1") and rc.is_loopback("[::1]:1") and not rc.is_loopback("0.0.0.0:22")


def test_diff_separates_exposed_listeners(tmp_path):
    before = rc.parse_listeners(SS)
    rc.save_snapshot(tmp_path, before)
    after = before | {"127.0.0.1:9000", "0.0.0.0:7777"}
    assert rc.diff(tmp_path, after) == (["127.0.0.1:9000"], ["0.0.0.0:7777"])
    assert rc.diff(tmp_path, before) == ([], [])


def test_cli_rc_outside_tmux_fails_cleanly(monkeypatch, capsys):
    monkeypatch.delenv("TMUX", raising=False)
    assert cli.main(["rc"]) == 1
    assert "inside tmux" in capsys.readouterr().out
