"""scripts/check-skills.py: the shipped skills pass, and each rule catches the mistake it exists for."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-skills.py"

GOOD_SKILL = """---
name: {name}
description: Does one thing. Use for /welleng:{name}.
disable-model-invocation: true
---

# {name}

Read `playbooks/bug-fix.md`, `principles/prove-it-works.md` and `../mode/SKILL.md` first.
Then spawn `welleng:worker`.
"""


def check(root: Path) -> tuple[int, str]:
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), str(root)], capture_output=True, text=True, check=False)
    return result.returncode, result.stderr


def tree(tmp_path: Path) -> Path:
    plugin = tmp_path / "claude-plugin"
    mode = plugin / "skills" / "mode"
    (mode / "playbooks").mkdir(parents=True)
    (mode / "principles").mkdir()
    (mode / "playbooks" / "bug-fix.md").write_text("# Bug fix\n\nReproduce it first.\n")
    (mode / "principles" / "prove-it-works.md").write_text("# Prove it works\n\nRun the real thing.\n")
    (mode / "SKILL.md").write_text(GOOD_SKILL.format(name="mode"))
    (plugin / "agents").mkdir()
    (plugin / "agents" / "worker.md").write_text("---\nname: worker\ndescription: A delegate.\n---\n\nFollow the rules.\n")
    return tmp_path


def write_skill(root: Path, name: str, text: str) -> None:
    folder = root / "claude-plugin" / "skills" / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(text)


def test_the_shipped_skills_pass():
    code, err = check(ROOT)
    assert code == 0, err


def test_a_clean_tree_passes(tmp_path):
    code, err = check(tree(tmp_path))
    assert code == 0, err


def test_name_must_match_the_directory(tmp_path):
    root = tree(tmp_path)
    write_skill(root, "why", GOOD_SKILL.format(name="how"))
    code, err = check(root)
    assert code == 1 and "frontmatter name must be 'why'" in err


def test_plugin_skills_must_be_user_invoked(tmp_path):
    root = tree(tmp_path)
    write_skill(root, "why", GOOD_SKILL.format(name="why").replace("disable-model-invocation: true\n", ""))
    code, err = check(root)
    assert code == 1 and "disable-model-invocation" in err


def test_missing_references_are_reported(tmp_path):
    root = tree(tmp_path)
    body = GOOD_SKILL.format(name="why") + "\nSee `playbooks/nope.md`, /welleng:ghost, `welleng:phantom`, `../gone/SKILL.md` and `../mode/nope.md`.\n"
    write_skill(root, "why", body)
    code, err = check(root)
    assert code == 1
    for needle in ("playbooks/nope.md", "/welleng:ghost", "welleng:phantom", "../gone/SKILL.md", "../mode/nope.md"):
        assert needle in err, needle


def test_cursor_names_and_transcript_paths_are_rejected(tmp_path):
    root = tree(tmp_path)
    write_skill(root, "why", GOOD_SKILL.format(name="why") + "\nSpawn a generalPurpose agent.\nRead ~/.claude/projects first.\n")
    code, err = check(root)
    assert code == 1 and "Cursor-only name" in err and "ADR 0005" in err


def test_two_sentences_on_one_line_are_rejected_but_lists_and_code_are_not(tmp_path):
    root = tree(tmp_path)
    fine = GOOD_SKILL.format(name="why") + "\n1. Do this.\n- Use `a. B` and e.g. Foo.\n\n```\nOne. Two. [example](missing.md)\n```\n| A. B | C |\n"
    write_skill(root, "why", fine)
    assert check(root)[0] == 0
    write_skill(root, "why", fine + "\nFirst sentence. Second sentence.\n")
    code, err = check(root)
    assert code == 1 and "more than one sentence" in err


def test_an_unquoted_colon_in_a_description_is_rejected(tmp_path):
    root = tree(tmp_path)
    write_skill(root, "why", GOOD_SKILL.format(name="why").replace("Does one thing.", "Does one thing: well."))
    code, err = check(root)
    assert code == 1 and "quote the description" in err
    write_skill(root, "why", GOOD_SKILL.format(name="why").replace("Does one thing. Use for /welleng:why.", '"Does one thing: well."'))
    assert check(root)[0] == 0
