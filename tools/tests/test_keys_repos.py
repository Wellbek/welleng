import subprocess
from pathlib import Path

from welleng import keys, repos

TMUX = """
# comment
bind r source-file ~/.tmux.conf
bind -n M-1 select-window -t 1
bind-key -T copy-mode-vi 'C-h' select-pane -L
bind-key -N "note here" F1 display-popup -E "less x"
set -g mouse on
"""


def test_parse_tmux_tables_and_commands():
    b = keys.parse_tmux(TMUX)
    assert [(x.table, x.key) for x in b] == [
        ("prefix", "r"),
        ("root", "M-1"),
        ("copy-mode-vi", "C-h"),
        ("prefix", "F1"),
    ]
    assert b[1].command == "select-window -t 1"


def test_render_filter():
    out = keys.render(keys.parse_tmux(TMUX), "select-pane")
    assert "C-h" in out and "M-1" not in out
    assert keys.render(keys.parse_tmux(TMUX), "zzz") == "no matching keybinding"


def test_deployed_tmux_conf_parses():
    conf = Path(__file__).resolve().parents[2] / "home" / "dot_tmux.conf"
    assert len(keys.load(conf)) > 10


def git(path: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        check=True, capture_output=True,
    )


def make_repo(path: Path) -> None:
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    (path / "a.txt").write_text("a")
    git(path, "add", "a.txt")
    git(path, "commit", "-q", "-m", "init")


def test_parse_status_counts():
    text = "# branch.head main\n# branch.ab +2 -1\n1 M. N... 1 1 1 a b c f\n1 .M N... 1 1 1 a b c g\n? new\n? new2\n"
    assert repos.parse_status(text) == ("main", 1, 1, 2, 2, 1)


def test_overview_real_repos(tmp_path):
    make_repo(tmp_path / "one")
    make_repo(tmp_path / "group" / "two")
    (tmp_path / "one" / "u.txt").write_text("x")
    (tmp_path / "group" / "two" / "a.txt").write_text("changed")
    (tmp_path / "plain").mkdir()
    found = repos.find_repos(tmp_path)
    assert {p.name for p in found} == {"one", "two"}
    one = repos.status(tmp_path / "one")
    two = repos.status(tmp_path / "group" / "two")
    assert (one.branch, one.untracked, one.unstaged) == ("main", 1, 0)
    assert (two.untracked, two.unstaged) == (0, 1)
    out = repos.overview(tmp_path)
    assert "one" in out and "group/two" in out and "plain" not in out


def test_empty_root(tmp_path):
    assert "no git repositories" in repos.overview(tmp_path)
