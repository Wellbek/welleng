"""Keep the documentation honest: links resolve, and every command is documented."""

import re
from pathlib import Path

import pytest

from welleng import cli

ROOT = Path(__file__).resolve().parents[2]
# docs/research and docs/architecture.md are gitignored local notes, so only tracked documents are checked.
LOCAL_NOTES = (ROOT / "docs" / "research", ROOT / "docs" / "architecture.md")
DOCS = [
    ROOT / "README.md",
    ROOT / "CHECKLIST.md",
    ROOT / "CLAUDE.md",
    *(p for p in sorted((ROOT / "docs").rglob("*.md")) if not any(p == n or n in p.parents for n in LOCAL_NOTES)),
]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")


def slug(heading: str) -> str:
    """GitHub's anchor for a heading."""
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    found = set()
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        elif not in_code and (m := re.match(r"#{1,6}\s+(.*)", line)):
            found.add(slug(m.group(1)))
    return found


def links(path: Path):
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        elif not in_code:
            yield from LINK.findall(line)


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_and_anchors_resolve(doc):
    problems = []
    for target in links(doc):
        if re.match(r"[a-z]+:", target):
            continue
        name, _, fragment = target.partition("#")
        dest = (doc.parent / name).resolve() if name else doc
        if not dest.exists():
            problems.append(f"{target}: no such file")
        elif fragment and dest.suffix == ".md" and fragment not in anchors(dest):
            problems.append(f"{target}: no such heading")
    assert not problems, problems


def test_every_command_is_in_the_command_reference():
    parser_commands = re.search(r"\{([a-z,]+)\}", cli_usage())
    assert parser_commands
    text = (ROOT / "docs" / "guides" / "commands.md").read_text(encoding="utf-8")
    missing = [c for c in parser_commands.group(1).split(",") if f"## `welleng {c}`" not in text]
    assert not missing, missing


def test_the_guide_index_lists_every_guide():
    index = (ROOT / "docs" / "guides" / "README.md").read_text(encoding="utf-8")
    for guide in (ROOT / "docs" / "guides").glob("*.md"):
        if guide.name != "README.md":
            assert f"]({guide.name})" in index, guide.name


def cli_usage() -> str:
    import contextlib
    import io

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf), pytest.raises(SystemExit):
        cli.main([])
    return buf.getvalue()
