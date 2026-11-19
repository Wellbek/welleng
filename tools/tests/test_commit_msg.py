"""scripts/check-commit-msg.sh, the commit-msg hook's checker."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-commit-msg.sh"


def check(tmp_path: Path, message: str) -> subprocess.CompletedProcess:
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_text(message)
    return subprocess.run(["bash", str(SCRIPT), str(path)], capture_output=True, text=True, check=False)


@pytest.mark.parametrize(
    "message",
    [
        "feat(plugin): add a Claude Code hook for Anthropic models\n",
        "fix: handle an empty file\n\nThe body may mention claude, cursor or gemini freely.\n",
        "docs(adr)!: drop the old layout\n",
        "# a comment git strips\nchore(ci): pin the runner\n",
        'Revert "feat: add x"\n',
        "Merge branch 'main' into topic\n",
        "fixup! feat: add x\n",
        "feat: credit a person\n\nCo-Authored-By: A Person <person@example.com>\n",
    ],
)
def test_valid_messages_pass(tmp_path, message):
    result = check(tmp_path, message)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "message, needle",
    [
        ("Add a thing\n", "type(scope): subject"),
        ("feature: add a thing\n", "type(scope): subject"),
        ("feat(Plugin): add a thing\n", "type(scope): subject"),
        ("feat: add x\n\nCo-Authored-By: Claude Opus <noreply@anthropic.com>\n", "AI attribution"),
        ("feat: add x\n\nco-authored-by: GitHub Copilot <copilot@github.com>\n", "AI attribution"),
        ("feat: add x\n\nClaude-Session: https://example.invalid/session\n", "AI attribution"),
        ("feat: add x\n\nGenerated with [Claude Code](https://claude.com/claude-code)\n", "AI attribution"),
    ],
)
def test_invalid_messages_fail_with_the_reason(tmp_path, message, needle):
    result = check(tmp_path, message)
    assert result.returncode == 1 and needle in result.stderr


def test_the_hook_calls_the_checker():
    hook = (ROOT / ".githooks" / "commit-msg").read_text()
    assert "scripts/check-commit-msg.sh" in hook
    assert (ROOT / ".githooks" / "commit-msg").stat().st_mode & 0o111
