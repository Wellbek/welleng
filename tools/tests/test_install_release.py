import hashlib
import importlib.util
import io
import tarfile
import zipfile
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "install_release", Path(__file__).resolve().parents[2] / "bootstrap" / "install_release.py"
)
ir = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ir)


def tar_bytes(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            t.addfile(info, io.BytesIO(content))
    return buf.getvalue()


def entry(data: bytes, url="https://example.invalid/tool.tar.gz", members=("tool",), sha=None):
    return {
        "name": "tool",
        "version": "1.0",
        "members": list(members),
        "assets": {"linux-x86_64": {"url": url, "sha256": sha or hashlib.sha256(data).hexdigest()}},
    }


def test_installs_verified_archive(tmp_path):
    data = tar_bytes({"dir/tool": b"#!/bin/sh\n", "dir/README": b"x"})
    rc = ir.install(entry(data), "linux-x86_64", tmp_path, fetch=lambda u: data)
    assert rc == 0
    assert (tmp_path / "tool").read_bytes() == b"#!/bin/sh\n"
    assert (tmp_path / "tool").stat().st_mode & 0o111
    assert not (tmp_path / "README").exists()


def test_checksum_mismatch_installs_nothing(tmp_path):
    data = tar_bytes({"tool": b"real"})
    tampered = tar_bytes({"tool": b"evil"})
    rc = ir.install(entry(data), "linux-x86_64", tmp_path, fetch=lambda u: tampered)
    assert rc == 1
    assert list(tmp_path.iterdir()) == []


def test_non_https_is_refused(tmp_path):
    data = tar_bytes({"tool": b"x"})
    rc = ir.install(entry(data, url="http://example.invalid/t.tar.gz"), "linux-x86_64", tmp_path, fetch=lambda u: data)
    assert rc == 1


def test_path_traversal_member_is_written_by_base_name_only(tmp_path):
    data = tar_bytes({"../../escape/tool": b"x"})
    dest = tmp_path / "bin"
    assert ir.install(entry(data), "linux-x86_64", dest, fetch=lambda u: data) == 0
    assert (dest / "tool").exists()
    assert not (tmp_path / "escape").exists()


def test_missing_member_installs_nothing(tmp_path):
    data = tar_bytes({"other": b"x"})
    assert ir.install(entry(data), "linux-x86_64", tmp_path, fetch=lambda u: data) == 1
    assert list(tmp_path.iterdir()) == []


def test_unknown_platform_reports_no_release(tmp_path):
    data = tar_bytes({"tool": b"x"})
    assert ir.install(entry(data), "plan9-mips", tmp_path, fetch=lambda u: data) == ir.NO_RELEASE


def test_zip_archives_work(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("yazi-x/yazi", b"bin")
    data = buf.getvalue()
    e = entry(data, url="https://example.invalid/y.zip", members=("yazi",))
    assert ir.install(e, "linux-x86_64", tmp_path, fetch=lambda u: data) == 0
    assert (tmp_path / "yazi").read_bytes() == b"bin"


def test_dry_run_writes_nothing(tmp_path, capsys):
    data = tar_bytes({"tool": b"x"})
    assert ir.install(entry(data), "linux-x86_64", tmp_path, dry_run=True) == 0
    assert list(tmp_path.iterdir()) == []
    assert "would install" in capsys.readouterr().out
