import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

from welleng import cli, hints

HOOK = Path(__file__).resolve().parents[2] / "claude-plugin" / "hooks" / "effort_hint.py"
SPEC = importlib.util.spec_from_file_location("effort_hint", HOOK)
eh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(eh)

HEAVY = "Please refactor the authentication module across the codebase and migrate the session handling " + "x " * 150
LIGHT = "rename foo to bar"


def test_estimates():
    assert eh.estimate(LIGHT)[0] == "light"
    assert eh.estimate(HEAVY)[0] == "heavy"
    assert eh.estimate("add a retry to the upload function and update the test")[0] == "standard"


def test_light_task_at_high_effort_gets_a_hint():
    assert eh.decide(LIGHT, "high", {}, 1e6)[0] == "low"


def test_heavy_task_at_low_effort_gets_a_hint():
    assert eh.decide(HEAVY, "low", {}, 1e6)[0] == "high"


def test_silent_cases():
    assert eh.decide(LIGHT, "medium", {}, 1e6)[0] is None  # gap of one level
    assert eh.decide(LIGHT, "high", {"off": True}, 1e6)[0] is None
    assert eh.decide(LIGHT, "high", {"snooze_until": 2e6}, 1e6)[0] is None
    assert eh.decide(LIGHT, "high", {"last_hint": 1e6 - 100}, 1e6)[0] is None  # cooldown
    assert eh.decide(LIGHT + " ultrathink", "high", {}, 1e6)[0] is None
    assert eh.decide(LIGHT, None, {}, 1e6)[0] is None  # no effort in the input
    assert eh.decide("do the thing", "low", {}, 1e6)[0] is None  # not confident
    assert eh.decide(HEAVY, "xhigh", {}, 1e6)[0] is None  # never recommends below the gap


def run_hook(tmp_path, prompt, level):
    event = {"hook_event_name": "UserPromptSubmit", "prompt": prompt, "effort": {"level": level}}
    env = {"XDG_STATE_HOME": str(tmp_path), "PATH": "/usr/bin:/bin"}
    r = subprocess.run([sys.executable, "-I", str(HOOK)], input=json.dumps(event), capture_output=True, text=True, env=env, check=False)
    assert r.returncode == 0
    return r.stdout


def test_hook_prints_only_one_json_object_then_respects_cooldown(tmp_path):
    out = run_hook(tmp_path, LIGHT, "high")
    assert list(json.loads(out)) == ["systemMessage"] and "/effort low" in out
    assert run_hook(tmp_path, LIGHT, "high") == ""
    log = (tmp_path / "welleng" / "hints.log").read_text()
    assert "rename" not in log and json.loads(log.splitlines()[0])["recommended"] == "low"


def test_hook_never_fails_on_garbage(tmp_path):
    for bad in ("", "nope", "{}"):
        r = subprocess.run([sys.executable, "-I", str(HOOK)], input=bad, capture_output=True, text=True, check=False)
        assert r.returncode == 0 and r.stdout == ""


def test_snooze_off_on_and_report(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    d = hints.state_dir()
    hints.snooze(d, 1, now=time.time())
    assert eh.decide(LIGHT, "high", json.loads((d / "hints.json").read_text()), time.time())[0] is None
    assert cli.main(["hints", "off"]) == 0
    assert "hints: off" in hints.report(d)
    assert cli.main(["hints", "on"]) == 0
    assert hints.report(d).startswith("hints: on")
    assert cli.main(["hints", "report"]) == 0
