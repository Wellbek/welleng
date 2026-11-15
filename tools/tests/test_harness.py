import json
from pathlib import Path

import pytest

from welleng import cli, harness

SPEC = {
    "intents": [
        {"kind": "claude_md", "name": "conventions", "text": "Use plain dashes."},
        {"kind": "deny", "rules": ["Read(**/.env)"]},
        {"kind": "ask", "rules": ["Bash(git push:*)"]},
        {"kind": "hook", "event": "PostToolUse", "matcher": "Edit|Write", "command": "git diff --quiet"},
        {"kind": "mcp", "name": "db", "config": {"command": "db-mcp", "env": {"URL": "${DB_URL}"}}},
        {"kind": "local_setting", "key": "model", "value": "sonnet"},
        {"kind": "rule_file", "name": "tests", "paths": ["tests/**"], "text": "Keep tests fast."},
    ]
}


def write_spec(tmp_path: Path, spec: dict) -> Path:
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(spec))
    return p


def test_plan_writes_nothing(tmp_path):
    changes = harness.plan(SPEC, tmp_path)
    assert {c.path.name for c in changes} >= {"CLAUDE.md", "settings.json", ".mcp.json", "settings.local.json", "tests.md"}
    assert list(tmp_path.iterdir()) == []


def test_apply_then_replan_is_a_no_op(tmp_path):
    harness.apply(harness.plan(SPEC, tmp_path))
    assert harness.plan(SPEC, tmp_path) == []
    settings = json.loads((tmp_path / ".claude" / "settings.json").read_text())
    assert settings["permissions"]["deny"] == ["Read(**/.env)"]
    assert settings["hooks"]["PostToolUse"][0]["matcher"] == "Edit|Write"
    assert harness.check(tmp_path) == []


def test_existing_content_is_preserved(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# Mine\n\nKeep me.\n")
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"deny": ["Read(x)"]}, "model": "opus"}))
    harness.apply(harness.plan(SPEC, tmp_path))
    assert (tmp_path / "CLAUDE.md").read_text().startswith("# Mine\n\nKeep me.\n")
    s = json.loads((tmp_path / ".claude" / "settings.json").read_text())
    assert s["permissions"]["deny"] == ["Read(x)", "Read(**/.env)"] and s["model"] == "opus"


def test_block_update_replaces_only_its_own_text():
    first = harness.upsert_block("# T\n", "a", "one")
    both = harness.upsert_block(first, "b", "two")
    updated = harness.upsert_block(both, "a", "ONE")
    assert "ONE" in updated and "one\n" not in updated and "two" in updated and updated.startswith("# T\n")


def test_secrets_are_refused():
    bad = {"intents": [{"kind": "claude_md", "name": "x", "text": "key sk-ant-" + "a" * 30}]}
    with pytest.raises(harness.SpecError):
        harness.plan(bad, Path("."))


def test_mcp_literal_env_is_refused():
    bad = {"intents": [{"kind": "mcp", "name": "db", "config": {"env": {"URL": "postgres://u:p@h/db"}}}]}
    with pytest.raises(harness.SpecError):
        harness.plan(bad, Path("."))


def test_invalid_existing_json_is_not_overwritten(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text("{broken")
    with pytest.raises(harness.SpecError):
        harness.plan(SPEC, tmp_path)
    assert (tmp_path / ".claude" / "settings.json").read_text() == "{broken"


def test_check_finds_problems(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "no-such-tool-xyz"}]}]}}))
    (tmp_path / "CLAUDE.md").write_text("<!-- welleng:begin a -->\nx\n")
    (tmp_path / ".mcp.json").write_text(json.dumps({"mcpServers": {"d": {"env": {"K": "literal"}}}}))
    out = "\n".join(harness.check(tmp_path))
    assert "no-such-tool-xyz" in out and "do not pair up" in out and "literal" in out


def test_cli_apply_requires_yes(tmp_path, capsys):
    spec = write_spec(tmp_path, SPEC)
    assert cli.main(["harness", "apply", str(spec), "--project", str(tmp_path)]) == 1
    assert not (tmp_path / "CLAUDE.md").exists()
    assert cli.main(["harness", "apply", str(spec), "--project", str(tmp_path), "--yes"]) == 0
    assert (tmp_path / "CLAUDE.md").exists()
    assert cli.main(["harness", "check", str(tmp_path)]) == 0
