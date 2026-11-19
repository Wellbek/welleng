#!/usr/bin/env python3
"""Check the Claude Code skills, agents and playbooks shipped in this repository (ADR 0020).

    python3 -I scripts/check-skills.py [ROOT]

Checked files: every Markdown file under claude-plugin/skills/, claude-plugin/agents/ and .claude/skills/.

- A SKILL.md has frontmatter whose `name` matches its directory and a `description` of at most 1024 characters,
  quoted when it contains ': ', because an unquoted one is invalid YAML.
- A plugin skill is user-invoked only (`disable-model-invocation: true`) unless it is listed in MODEL_INVOCABLE,
  so its description costs no context until it is typed.
- An agent has frontmatter whose `name` matches its file name, and a `description`.
- No Cursor-only names survive the port, and nothing points at Claude Code transcripts (ADR 0005).
- Every reference resolves: `playbooks/<x>.md`, `principles/<x>.md`, `/welleng:<skill>`, `welleng:<agent>`,
  `../<skill>/SKILL.md`, any other backticked `../` path, which is relative to the skill folder, and relative Markdown
  links outside code blocks.
- Prose keeps one sentence per line.

Standard library only. Exit code 0 when clean, 1 with one `path:line: problem` line per finding.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MODEL_INVOCABLE = {"harness"}
MAX_DESCRIPTION = 1024

FORBIDDEN = [
    (re.compile(r"\.cursor/|cursor-team-kit|\bAskQuestion\b|\bgeneralPurpose\b|\bBugbot\b|pstack-models|\bpoteto\b", re.I),
     "Cursor-only name, use the Claude Code equivalent"),
    (re.compile(r"~/\.claude/projects|agent-transcripts|\.jsonl\b"),
     "points at Claude Code transcripts, which ADR 0005 forbids"),
]

PLAYBOOK_REF = re.compile(r"\b(playbooks|principles)/([a-z0-9-]+)\.md")
SKILL_REF = re.compile(r"/welleng:([a-z0-9-]+)")
AGENT_REF = re.compile(r"(?<![/\w])welleng:([a-z0-9-]+)")
SIBLING_REF = re.compile(r"\.\./([a-z0-9-]+)/SKILL\.md")
RELATIVE_REF = re.compile(r"`(\.\./[A-Za-z0-9_./-]+\.[a-z]+)`")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
INLINE_CODE = re.compile(r"`[^`]*`")
LIST_MARKER = re.compile(r"^(\d+\.|[-*+])\s+")
ABBREVIATIONS = re.compile(r"\b(e\.g|i\.e|vs|etc|cf)\.", re.I)
SENTENCE_BREAK = re.compile(r"[a-z0-9)\]\"'*][.!?][\"'*)]*\s+[A-Z]")


def frontmatter(text: str) -> tuple[dict[str, str], int] | None:
    """Return the top-level `key: value` pairs and the number of lines the block takes, or None."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None
    for end in range(1, len(lines)):
        if lines[end] == "---":
            break
    else:
        return None
    fields: dict[str, str] = {}
    key = None
    for line in lines[1:end]:
        m = re.match(r"([A-Za-z][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields, end + 1


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


class Checker:
    def __init__(self, root: Path):
        self.root = root
        self.plugin = root / "claude-plugin"
        self.mode = self.plugin / "skills" / "mode"
        self.problems: list[str] = []

    def report(self, path: Path, line: int, message: str) -> None:
        self.problems.append(f"{path.relative_to(self.root)}:{line}: {message}")

    def files(self) -> list[Path]:
        found: list[Path] = []
        for base in (self.plugin / "skills", self.plugin / "agents", self.root / ".claude" / "skills"):
            if base.is_dir():
                found += sorted(base.rglob("*.md"))
        return found

    def skill_exists(self, name: str) -> bool:
        return (self.plugin / "skills" / name / "SKILL.md").is_file()

    def agent_exists(self, name: str) -> bool:
        return (self.plugin / "agents" / f"{name}.md").is_file()

    def skill_root(self, path: Path) -> Path | None:
        """The folder of the skill that owns `path`, which `../` references are relative to."""
        for base in (self.plugin / "skills", self.root / ".claude" / "skills"):
            if base in path.parents:
                return base / path.relative_to(base).parts[0]
        return None

    def check_frontmatter(self, path: Path, text: str) -> int:
        """Validate frontmatter where it is required and return the number of lines it takes."""
        parsed = frontmatter(text)
        is_skill = path.name == "SKILL.md"
        is_agent = path.parent == self.plugin / "agents"
        if not (is_skill or is_agent):
            return parsed[1] if parsed else 0
        if parsed is None:
            self.report(path, 1, "missing frontmatter")
            return 0
        fields, size = parsed
        expected = path.parent.name if is_skill else path.stem
        if unquote(fields.get("name", "")) != expected:
            self.report(path, 2, f"frontmatter name must be {expected!r}")
        raw = fields.get("description", "")
        description = unquote(raw)
        if ": " in raw and raw == description and not raw.startswith((">", "|")):
            self.report(path, 2, "quote the description, an unquoted ': ' is invalid YAML")
        if not description:
            self.report(path, 2, "frontmatter description is missing")
        elif len(description) > MAX_DESCRIPTION:
            self.report(path, 2, f"description is longer than {MAX_DESCRIPTION} characters")
        in_plugin = self.plugin in path.parents
        if is_skill and in_plugin and expected not in MODEL_INVOCABLE:
            if unquote(fields.get("disable-model-invocation", "")) != "true":
                self.report(path, 2, "plugin skills are user-invoked: set disable-model-invocation: true")
        return size

    def check_references(self, path: Path, number: int, line: str, in_code: bool) -> None:
        for kind, slug in PLAYBOOK_REF.findall(line):
            if not (self.mode / kind / f"{slug}.md").is_file():
                self.report(path, number, f"{kind}/{slug}.md does not exist under skills/mode/")
        for name in SKILL_REF.findall(line):
            if not self.skill_exists(name):
                self.report(path, number, f"/welleng:{name} is not a skill in claude-plugin/skills/")
        for name in AGENT_REF.findall(line):
            if not (self.skill_exists(name) or self.agent_exists(name)):
                self.report(path, number, f"welleng:{name} is neither a plugin skill nor a plugin agent")
        for name in SIBLING_REF.findall(line):
            if not self.skill_exists(name):
                self.report(path, number, f"../{name}/SKILL.md does not exist")
        root = self.skill_root(path)
        for target in RELATIVE_REF.findall(line):
            if root and not (root / target).exists():
                self.report(path, number, f"{target} does not exist relative to the skill folder")
        for target in [] if in_code else LINK.findall(line):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            if not (path.parent / target.partition("#")[0]).exists():
                self.report(path, number, f"link target {target} does not exist")

    def check_sentences(self, path: Path, number: int, line: str) -> None:
        stripped = line.strip()
        if not stripped or stripped.startswith(("|", "#", ">")):
            return
        prose = LIST_MARKER.sub("", stripped)
        prose = ABBREVIATIONS.sub("abbr", INLINE_CODE.sub("code", LINK.sub("link", prose)))
        if SENTENCE_BREAK.search(prose):
            self.report(path, number, "more than one sentence on this line, put each sentence on its own line")

    def check_file(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        skip = self.check_frontmatter(path, text)
        in_code = False
        for number, line in enumerate(text.splitlines(), start=1):
            for pattern, message in FORBIDDEN:
                if pattern.search(line):
                    self.report(path, number, message)
            if number <= skip:
                continue
            if line.lstrip().startswith("```"):
                in_code = not in_code
                continue
            self.check_references(path, number, line, in_code)
            if not in_code:
                self.check_sentences(path, number, line)

    def run(self) -> list[str]:
        for path in self.files():
            self.check_file(path)
        return self.problems


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parents[1]
    problems = Checker(root).run()
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
