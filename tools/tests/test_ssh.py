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


def test_migrate_is_a_dry_run_by_default(tmp_path):
    main = tmp_path / "config"
    main.write_text("Host a\n  HostName a.example.invalid\n")
    assert "would add" in ssh.migrate(main, apply=False)
    assert main.read_text() == "Host a\n  HostName a.example.invalid\n"


def test_migrate_puts_the_include_first_keeps_a_backup_and_is_idempotent(tmp_path):
    main = tmp_path / "config"
    original = "Host a\n  HostName a.example.invalid\n"
    main.write_text(original)
    main.chmod(0o640)
    ssh.migrate(main, apply=True)
    text = main.read_text()
    assert text.splitlines()[:2] == [ssh.MARKER, ssh.INCLUDE_LINE]
    assert text.endswith(original)
    assert (tmp_path / "config.welleng-backup").read_text() == original
    assert stat.S_IMODE(main.stat().st_mode) == 0o600
    assert "nothing to do" in ssh.migrate(main, apply=True)
    assert main.read_text() == text


def test_migrate_recognises_an_existing_include_and_a_missing_file(tmp_path):
    main = tmp_path / "config"
    main.write_text("Include ~/.ssh/config.d/*\nHost a\n")
    assert "already" in ssh.migrate(main, apply=True)
    assert main.read_text() == "Include ~/.ssh/config.d/*\nHost a\n"
    fresh = tmp_path / "sub" / "config"
    ssh.migrate(fresh, apply=True)
    assert ssh.INCLUDE_LINE in fresh.read_text()


def test_unmigrate_restores_the_original_exactly(tmp_path):
    main = tmp_path / "config"
    original = "Host a\n  HostName a.example.invalid\n"
    main.write_text(original)
    ssh.migrate(main, apply=True)
    ssh.unmigrate(main, apply=True)
    assert main.read_text() == original
    assert "nothing to do" in ssh.unmigrate(main, apply=True)


def test_migrate_through_a_symlinked_config_writes_the_target(tmp_path):
    real = tmp_path / "real_config"
    real.write_text("Host a\n")
    link = tmp_path / "config"
    link.symlink_to(real)
    ssh.migrate(link, apply=True)
    assert link.is_symlink()
    assert real.read_text().startswith(ssh.MARKER)


def test_migrated_config_resolves_hosts_identically_with_real_ssh(tmp_path):
    import shutil
    import subprocess

    if shutil.which("ssh") is None:
        pytest.skip("ssh not installed")
    dot_ssh = tmp_path / ".ssh"
    dot_ssh.mkdir()
    main = dot_ssh / "config"
    main.write_text("Host manual1\n  HostName m.example.invalid\n  User me\n  Port 2200\n")

    def resolve(name):
        out = subprocess.run(["ssh", "-F", str(main), "-G", name], capture_output=True, text=True, check=True).stdout
        return {k: v for k, _, v in (l.partition(" ") for l in out.splitlines()) if k in ("hostname", "user", "port")}

    before = resolve("manual1")
    ssh.add(dot_ssh / "config.d", "box2", "b2.example.invalid", user="dev", port=2222)
    ssh.migrate(main, apply=True)
    # ssh resolves a relative Include against the real ~/.ssh, which a test cannot redirect, so
    # point the line at the temporary directory. The ordering semantics are what is under test.
    main.write_text(main.read_text().replace("Include config.d/", f"Include {dot_ssh}/config.d/"))
    assert resolve("manual1") == before
    assert resolve("box2") == {"hostname": "b2.example.invalid", "user": "dev", "port": "2222"}
