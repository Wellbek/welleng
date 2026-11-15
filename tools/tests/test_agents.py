import json
import shutil

import pytest

from welleng import agents, cli

SAMPLE = json.dumps(
    [
        {"pid": 1, "cwd": "/w/alpha", "kind": "interactive", "startedAt": 1_000_000, "sessionId": "s1", "name": "a", "status": "busy"},
        {"id": "b2", "cwd": "/w/beta", "kind": "background", "startedAt": 2_000_000, "sessionId": "s2", "state": "blocked"},
        {"cwd": "/w/gamma", "status": "something-new"},
        "junk",
    ]
)


def test_parse_maps_states_and_sorts_waiting_first():
    out = agents.parse(SAMPLE)
    assert [(a.project, a.state) for a in out] == [("beta", "waiting"), ("alpha", "working"), ("gamma", "unknown")]


def test_waiting_count():
    assert agents.waiting_count(agents.parse(SAMPLE)) == 1


def test_age_formatting():
    assert agents.age(0, now=45) == "45s"
    assert agents.age(0, now=3 * 3600 + 5) == "3h"
    assert agents.age(None) == "?"


def test_render_has_header_and_rows():
    text = agents.render(agents.parse(SAMPLE), now=3000)
    assert text.splitlines()[0].startswith("state")
    assert "beta" in text and "alpha" in text


@pytest.mark.parametrize("bad", ["not json", "{}", ""])
def test_bad_output_raises(bad):
    with pytest.raises(agents.AgentsError):
        agents.parse(bad)


def test_cli_count_and_error(monkeypatch, capsys):
    monkeypatch.setattr(agents, "fetch", lambda: agents.parse(SAMPLE))
    assert cli.main(["agents", "--count"]) == 0
    assert capsys.readouterr().out.strip() == "1"

    def boom():
        raise agents.AgentsError("nope")

    monkeypatch.setattr(agents, "fetch", boom)
    assert cli.main(["agents", "--count"]) == 0
    assert capsys.readouterr().out.strip() == "?"
    assert cli.main(["agents"]) == 1


@pytest.mark.skipif(shutil.which("claude") is None, reason="claude is not installed")
def test_contract_against_the_installed_claude():
    """ADR 0005: the schema is not frozen, so check the real output still parses with known states."""
    found = agents.fetch()
    assert all(a.state in agents.ORDER for a in found)
    assert all(a.session_id != "" for a in found)
