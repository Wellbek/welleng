import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "enable-statusline.py"
EXPECTED = f"python3 -I {ROOT / 'claude-plugin-hooks' / 'hooks' / 'statusline.py'}"


def run(settings: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(SCRIPT), "--settings", str(settings), *args],
                          capture_output=True, text=True, check=False)


def test_sets_the_status_line_keeps_other_keys_and_is_idempotent(tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({"model": "opus", "enabledPlugins": {"a@b": True}}))
    assert run(settings).returncode == 0
    data = json.loads(settings.read_text())
    assert data["statusLine"] == {"type": "command", "command": EXPECTED}
    assert data["model"] == "opus" and data["enabledPlugins"] == {"a@b": True}
    again = run(settings)
    assert again.returncode == 0 and "nothing to change" in again.stdout


def test_dry_run_writes_nothing(tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text("{}")
    assert run(settings, "--dry-run").returncode == 0
    assert settings.read_text() == "{}"


def test_an_old_welleng_path_is_updated(tmp_path):
    settings = tmp_path / "settings.json"
    old = {"type": "command", "command": "python3 -I /home/x/welleng/claude-plugin/hooks/statusline.py"}
    settings.write_text(json.dumps({"statusLine": old}))
    assert run(settings).returncode == 0
    assert json.loads(settings.read_text())["statusLine"]["command"] == EXPECTED


def test_a_foreign_status_line_needs_force(tmp_path):
    settings = tmp_path / "settings.json"
    mine = {"type": "command", "command": "~/bin/my-line"}
    settings.write_text(json.dumps({"statusLine": mine}))
    refused = run(settings)
    assert refused.returncode == 1 and "--force" in refused.stderr
    assert json.loads(settings.read_text())["statusLine"] == mine
    assert run(settings, "--force").returncode == 0
    assert json.loads(settings.read_text())["statusLine"]["command"] == EXPECTED


def test_remove_and_invalid_json(tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text("{}")
    run(settings)
    assert run(settings, "--remove").returncode == 0
    assert "statusLine" not in json.loads(settings.read_text())
    settings.write_text("{not json")
    assert run(settings).returncode == 1
    assert settings.read_text() == "{not json"
