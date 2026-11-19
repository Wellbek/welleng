from pathlib import Path

from welleng import cli, doctor

TOML = """
[[package]]
name = "alpha"
tier = "mandatory"
bins = ["definitely-not-installed-a", "sh"]

[[package]]
name = "beta"
tier = "recommended"
fallback = "uv tool install beta"
bins = ["definitely-not-installed-b"]

[[package]]
name = "gamma"
tier = "mandatory"
bins = ["definitely-not-installed-c"]
"""


def write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "packages.toml"
    p.write_text(text)
    return p


def test_alternate_binary_name_is_found(tmp_path):
    comps = doctor.load_components(write(tmp_path, TOML))
    assert comps[0].found == "sh"
    assert comps[1].found is None


def test_missing_mandatory_fails(tmp_path, capsys):
    assert cli.main(["doctor", "--packages", str(write(tmp_path, TOML))]) == 1
    out = capsys.readouterr().out
    assert "missing  gamma" in out
    assert "fallback: uv tool install beta" in out


def test_missing_recommended_only_passes(tmp_path):
    only_rec = TOML.split("[[package]]")[2]
    p = write(tmp_path, "[[package]]" + only_rec)
    assert cli.main(["doctor", "--packages", str(p)]) == 0


def test_repository_package_map_loads():
    comps = doctor.load_components(doctor.default_packages_path())
    assert {c.name for c in comps} >= {"git", "neovim", "fd"}
    assert next(c for c in comps if c.name == "neovim").bins == ("nvim",)


LIST_JSON = """[
 {"id": "big@market", "version": "2.0.0", "enabled": true},
 {"id": "off@market", "version": "1.0.0", "enabled": false},
 {"id": "welleng@welleng-local", "version": "0.1.0", "enabled": true,
  "readFromFolder": "/repo/claude-plugin", "folderVersion": "0.2.0"}
]"""


def fake_claude(args):
    if args[:3] == ["claude", "plugin", "list"]:
        return LIST_JSON
    if args[-1] == "big@market":
        return "Projected token cost\n  Always-on:   ~44,834 tok   added to every session\n"
    if args[-1] == "welleng@welleng-local":
        return "  Always-on:   ~1,860 tok   added to every session\n"
    raise AssertionError(f"unexpected call {args}")


def test_plugins_report_the_loaded_version_and_the_cost():
    plugins = doctor.load_plugins(fake_claude)
    assert [p.version for p in plugins] == ["2.0.0", "1.0.0", "0.2.0"]
    text = doctor.render_plugins(plugins, "0.2.0")
    assert "enabled  big@market 2.0.0, ~44,834 always-on tokens" in text
    assert "disabled off@market 1.0.0" in text and "off@market 1.0.0," not in text
    assert "~46,694 always-on tokens" in text
    assert "advice" not in text


def test_plugins_advise_an_update_when_the_loaded_version_is_old():
    text = doctor.render_plugins(doctor.load_plugins(fake_claude), "0.3.0")
    assert "sessions load welleng@welleng-local 0.2.0 but the repository has 0.3.0" in text


def test_plugins_are_skipped_without_claude():
    assert doctor.load_plugins(lambda args: None) is None
    assert "skipped" in doctor.render_plugins(None, "0.2.0")
    assert doctor.load_plugins(lambda args: "not json") is None
