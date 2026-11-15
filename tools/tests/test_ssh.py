import stat

import pytest

from welleng import cli, ssh


def test_add_list_remove_roundtrip(tmp_path):
    d = tmp_path / "config.d"
    target = ssh.add(d, "box1", "box1.example.invalid", user="dev", port=2222, jump="gate", description="test box")
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    hosts = ssh.list_hosts(d)
    assert [(h.name, h.hostname, h.user, h.port, h.managed) for h in hosts] == [("box1", "box1.example.invalid", "dev", "2222", True)]
    ssh.remove(d, "box1")
    assert ssh.list_hosts(d) == []


def test_hand_written_entries_are_listed_but_never_removed(tmp_path):
    main = tmp_path / "config"
    main.write_text("Host manual1\n  HostName m.example.invalid\n  User me\nHost *\n  ForwardAgent no\n")
    d = tmp_path / "config.d"
    hosts = ssh.list_hosts(d, main)
    assert [(h.name, h.managed) for h in hosts] == [("manual1", False)]
    with pytest.raises(ssh.SshError):
        ssh.remove(d, "manual1")
    d.mkdir()
    (d / "hand.conf").write_text("Host hand\n  HostName h.example.invalid\n")
    with pytest.raises(ssh.SshError):
        ssh.remove(d, "hand")
    assert (d / "hand.conf").exists()


@pytest.mark.parametrize("kwargs", [
    {"name": "bad name", "hostname": "h"},
    {"name": "ok", "hostname": "h\nProxyCommand evil"},
    {"name": "ok", "hostname": "h", "user": "a b"},
    {"name": "ok", "hostname": "h", "identity": "~/k #x"},
    {"name": "ok", "hostname": "h", "port": 70000},
    {"name": "ok", "hostname": "h", "description": "x\nHost evil"},
    {"name": "../escape", "hostname": "h"},
])
def test_injection_and_bad_values_are_rejected(tmp_path, kwargs):
    with pytest.raises(ssh.SshError):
        ssh.add(tmp_path / "d", **kwargs)
    assert not (tmp_path / "d").exists() or list((tmp_path / "d").iterdir()) == []


def test_duplicate_name_is_rejected(tmp_path):
    ssh.add(tmp_path, "a", "h")
    with pytest.raises(ssh.SshError):
        ssh.add(tmp_path, "a", "h2")


def test_cli(tmp_path, capsys):
    d = str(tmp_path / "cd")
    assert cli.main(["ssh", "--dir", d, "add", "web", "web.example.invalid", "--user", "u"]) == 0
    assert cli.main(["ssh", "--dir", d, "ls"]) == 0
    assert "web.example.invalid" in capsys.readouterr().out
    assert cli.main(["ssh", "--dir", d, "add", "web", "x"]) == 1
    assert cli.main(["ssh", "--dir", d, "rm", "web"]) == 0
