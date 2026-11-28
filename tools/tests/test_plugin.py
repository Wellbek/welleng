import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "claude-plugin"
HOOKS_PLUGIN = ROOT / "claude-plugin-hooks"
HOOK = HOOKS_PLUGIN / "hooks" / "suggest_harness.py"


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
    assert "/welleng:harness" in out["hookSpecificOutput"]["additionalContext"]


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
    assert json.loads((HOOKS_PLUGIN / ".claude-plugin" / "plugin.json").read_text())["name"] == "welleng-hooks"
    hooks = json.loads((HOOKS_PLUGIN / "hooks" / "hooks.json").read_text())
    assert "SessionStart" in hooks["hooks"]
    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert {p["name"]: p["source"] for p in marketplace["plugins"]} == {
        "welleng": "./claude-plugin",
        "welleng-hooks": "./claude-plugin-hooks",
    }
    skill = (PLUGIN / "skills" / "harness" / "SKILL.md").read_text()
    assert skill.startswith("---\nname: harness\n")


def test_every_adapted_file_is_listed_and_every_listed_file_exists():
    upstream = json.loads((PLUGIN / "pstack-upstream.json").read_text())
    assert len(upstream["commit"]) == 40
    listed = {PLUGIN.parent / local for local in upstream["files"].values()}
    assert all(path.exists() for path in listed), [str(p) for p in listed if not p.exists()]
    own = {"harness"}
    for skill in sorted((PLUGIN / "skills").iterdir()):
        if skill.name not in own:
            assert skill / "SKILL.md" in listed, f"{skill.name} is not in pstack-upstream.json"
    for agent in sorted((PLUGIN / "agents").glob("*.md")):
        assert agent in listed, f"{agent.name} is not in pstack-upstream.json"
    assert "MIT License" in (PLUGIN / "THIRD_PARTY_NOTICES.md").read_text()


def test_the_mode_skill_lists_every_playbook():
    mode = PLUGIN / "skills" / "mode"
    text = (mode / "SKILL.md").read_text()
    for playbook in sorted((mode / "playbooks").glob("*.md")):
        assert f"`playbooks/{playbook.name}`" in text, playbook.name
    for principle in sorted((mode / "principles").glob("*.md")):
        assert f"`principles/{principle.name}`" in text, principle.name


def test_the_skills_plugin_runs_nothing_on_its_own():
    """The welleng plugin installs alone with nothing running automatically, see ADR 0022."""
    assert not (PLUGIN / "hooks").exists()
    manifest = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
    assert not {"hooks", "mcpServers", "lspServers"} & manifest.keys()
