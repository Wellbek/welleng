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
