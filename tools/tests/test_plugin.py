import json
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2] / "claude-plugin"
HOOK = PLUGIN / "hooks" / "suggest_harness.py"


def run(event: dict | str) -> str:
    payload = event if isinstance(event, str) else json.dumps(event)
    result = subprocess.run([sys.executable, "-I", str(HOOK)], input=payload, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    return result.stdout


def event(cwd: Path, source="startup"):
    return {"hook_event_name": "SessionStart", "source": source, "cwd": str(cwd)}


def test_suggests_in_a_bare_git_project(tmp_path):
    (tmp_path / ".git").mkdir()
    out = json.loads(run(event(tmp_path)))
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "/harness" in out["hookSpecificOutput"]["additionalContext"]


def test_silent_when_configured_or_not_a_repo_or_not_startup(tmp_path):
    assert run(event(tmp_path)) == ""
    (tmp_path / ".git").mkdir()
    assert run(event(tmp_path, source="resume")) == ""
    (tmp_path / "CLAUDE.md").write_text("x")
    assert run(event(tmp_path)) == ""


def test_never_fails_on_garbage_input():
    assert run("not json") == ""
    assert run("{}") == ""


def test_manifests_are_valid():
    manifest = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "welleng"
    hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())
    assert "SessionStart" in hooks["hooks"]
    skill = (PLUGIN / "skills" / "harness" / "SKILL.md").read_text()
    assert skill.startswith("---\nname: harness\n")
