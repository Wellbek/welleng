"""Helper scripts that ship inside plugin skills."""

import subprocess
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2] / "claude-plugin" / "skills"
LOG = SKILLS / "show-me-your-work" / "scripts" / "log.py"


def log(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(LOG), *args], capture_output=True, text=True, check=False)


def test_decision_log_writes_the_header_once_and_one_clean_row_per_call(tmp_path):
    path = tmp_path / "nested" / "decisions.tsv"
    assert log(str(path), "frame", "picked a", "smaller", "commit abc", "tests green").returncode == 0
    assert log(str(path), "build", "two\tcells\nand lines", "why", "=HYPERLINK(1)", "-1").returncode == 0
    rows = [line.split("\t") for line in path.read_text().splitlines()]
    assert rows[0] == ["ts", "phase", "decision", "why", "evidence", "result"]
    assert len(rows) == 3 and all(len(r) == 6 for r in rows)
    assert rows[2][2] == "two cells and lines"
    assert rows[2][4] == "'=HYPERLINK(1)" and rows[2][5] == "'-1"
    assert rows[1][0].endswith("Z")


def test_decision_log_rejects_a_wrong_argument_count(tmp_path):
    result = log(str(tmp_path / "d.tsv"), "only-a-phase")
    assert result.returncode == 2 and "LOGFILE" in result.stderr
    assert not (tmp_path / "d.tsv").exists()
