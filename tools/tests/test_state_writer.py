import json
import os
import stat
import subprocess
import sys
from pathlib import Path

from welleng import agents

HOOKS = Path(__file__).resolve().parents[2] / "claude-plugin-hooks" / "hooks"
SID = "abc-123"


def run(script: str, payload, state: Path) -> subprocess.CompletedProcess:
    data = payload if isinstance(payload, str) else json.dumps(payload)
    env = {**os.environ, "XDG_STATE_HOME": str(state)}
    return subprocess.run([sys.executable, "-I", str(HOOKS / script)], input=data, capture_output=True, text=True, env=env, check=False)


def session_file(state: Path, sid: str = SID) -> Path:
    return state / "welleng" / "sessions" / f"{sid}.json"


def event(name: str, **extra) -> dict:
    return {"session_id": SID, "hook_event_name": name, "cwd": "/work/proj", **extra}


def test_session_start_records_model_effort_and_prints_nothing(tmp_path):
    r = run("state_writer.py", event("SessionStart", model="claude-x", effort={"level": "high"}), tmp_path)
    assert (r.returncode, r.stdout, r.stderr) == (0, "", "")
    data = json.loads(session_file(tmp_path).read_text())
    assert (data["model"], data["effort"], data["cwd"]) == ("claude-x", "high", "/work/proj")
    assert stat.S_IMODE(session_file(tmp_path).stat().st_mode) == 0o600


def test_prompt_text_and_transcript_path_are_never_written(tmp_path):
    run("state_writer.py", event("UserPromptSubmit", prompt="SECRET-PROMPT", transcript_path="/home/u/.claude/t.jsonl"), tmp_path)
    text = session_file(tmp_path).read_text()
    assert "SECRET-PROMPT" not in text and "transcript" not in text


def test_subagents_are_tracked_by_id_and_cleared_on_stop(tmp_path):
    run("state_writer.py", event("SubagentStart", agent_id="a1"), tmp_path)
    run("state_writer.py", event("SubagentStart", agent_id="a2"), tmp_path)
    run("state_writer.py", event("SubagentStart", agent_id="a2"), tmp_path)
    assert json.loads(session_file(tmp_path).read_text())["subagents"] == ["a1", "a2"]
    run("state_writer.py", event("SubagentStop", agent_id="a1"), tmp_path)
    assert json.loads(session_file(tmp_path).read_text())["subagents"] == ["a2"]
    run("state_writer.py", event("Stop"), tmp_path)
    assert json.loads(session_file(tmp_path).read_text())["subagents"] == []


def test_session_end_removes_the_file(tmp_path):
    run("state_writer.py", event("SessionStart"), tmp_path)
    assert session_file(tmp_path).exists()
    run("state_writer.py", event("SessionEnd", reason="other"), tmp_path)
    assert not session_file(tmp_path).exists()


def test_hostile_session_ids_and_garbage_are_ignored(tmp_path):
    for sid in ("../evil", "a/b", "", ".hidden", 5):
        r = run("state_writer.py", {"session_id": sid, "hook_event_name": "SessionStart"}, tmp_path)
        assert r.returncode == 0
    for junk in ("not json", "[]", "{}", ""):
        assert run("state_writer.py", junk, tmp_path).returncode == 0
    assert not list(tmp_path.rglob("*.json")) and not (tmp_path / "evil.json").exists()


def test_old_state_files_are_pruned_on_session_start(tmp_path):
    run("state_writer.py", event("SessionStart"), tmp_path)
    old = session_file(tmp_path, "old-one")
    old.write_text("{}")
    os.utime(old, (1, 1))
    run("state_writer.py", event("SessionStart"), tmp_path)
    assert not old.exists() and session_file(tmp_path).exists()


def test_statusline_prints_a_line_and_merges_into_the_same_file(tmp_path):
    run("state_writer.py", event("SessionStart", model="m0"), tmp_path)
    payload = {"session_id": SID, "model": {"id": "claude-x"}, "effort": {"level": "xhigh"},
               "context_window": {"used_percentage": 42.4}, "cost": {"total_cost_usd": 1.234}}
    r = run("statusline.py", payload, tmp_path)
    assert r.stdout.strip() == "claude-x | xhigh | ctx 42% | $1.23"
    data = json.loads(session_file(tmp_path).read_text())
    assert (data["model"], data["effort"], data["context_pct"], data["cost_usd"], data["cwd"]) == ("claude-x", "xhigh", 42.4, 1.234, "/work/proj")
    assert run("statusline.py", "garbage", tmp_path).returncode == 0


def test_agents_enrich_reads_the_state_and_renders_extra_columns(tmp_path):
    run("state_writer.py", event("SessionStart", model="claude-x", effort={"level": "high"}), tmp_path)
    run("statusline.py", {"session_id": SID, "context_window": {"used_percentage": 10}, "cost": {"total_cost_usd": 0.5}}, tmp_path)
    run("state_writer.py", event("SubagentStart", agent_id="a1"), tmp_path)
    sample = json.dumps([{"sessionId": SID, "cwd": "/work/proj", "status": "busy", "kind": "interactive"},
                         {"sessionId": "other", "cwd": "/work/two", "status": "idle", "kind": "interactive"}])
    found = agents.enrich(agents.parse(sample), tmp_path / "welleng" / "sessions")
    mine = next(a for a in found if a.session_id == SID)
    assert (mine.model, mine.effort, mine.context_pct, mine.cost_usd, mine.subagents) == ("claude-x", "high", 10.0, 0.5, 1)
    text = agents.render(found, now=0)
    assert "model" in text.splitlines()[0] and "claude-x" in text and "$0.50" in text
    # A session without state still renders, with dashes.
    assert next(l for l in text.splitlines() if "two" in l).count("-") >= 5


def test_enrich_ignores_corrupt_state(tmp_path):
    d = tmp_path / "s"
    d.mkdir()
    (d / f"{SID}.json").write_text("{broken")
    sample = json.dumps([{"sessionId": SID, "cwd": "/w/p", "status": "idle", "kind": "x"}])
    assert agents.enrich(agents.parse(sample), d) == agents.parse(sample)


def test_every_hook_command_in_hooks_json_exists():
    cfg = json.loads((HOOKS / "hooks.json").read_text())
    scripts = {h["command"].split("/hooks/")[1].rstrip('"') for groups in cfg["hooks"].values() for g in groups for h in g["hooks"]}
    assert {"state_writer.py", "suggest_harness.py", "effort_hint.py"} <= scripts
    assert all((HOOKS / s).is_file() for s in scripts)
