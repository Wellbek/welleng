"""Plan, apply and check a project's Claude Code configuration from a list of intents.

The `/harness` skill collects answers and writes them as a JSON spec.
This module turns the spec into exact file changes, shows them as diffs, and writes nothing until
`apply` is called.
Generated Markdown lives in delimited blocks so a rerun replaces only its own text.
JSON files are merged without removing anything the user already has.

Spec format:
    {"intents": [
      {"kind": "claude_md", "name": "conventions", "text": "Use ..."},
      {"kind": "rule_file", "name": "tests", "paths": ["tests/**"], "text": "..."},
      {"kind": "deny", "rules": ["Read(**/.env)"]},
      {"kind": "ask", "rules": ["Bash(git push:*)"]},
      {"kind": "hook", "event": "PostToolUse", "matcher": "Edit|Write", "command": "ruff format ."},
      {"kind": "mcp", "name": "db", "config": {"command": "...", "env": {"URL": "${DB_URL}"}}},
      {"kind": "local_setting", "key": "model", "value": "sonnet"},
      {"kind": "plugin", "id": "welleng@welleng-local", "shared": false},
      {"kind": "plugin", "id": "welleng@welleng-local", "shared": true,
       "marketplace": {"name": "welleng-local", "source": {"source": "github", "repo": "OWNER/REPO"}}}
    ]}

A `plugin` intent enables a plugin for the project.
With `shared` false it goes into the personal `.claude/settings.local.json`.
With `shared` true it goes into `.claude/settings.json` for every collaborator, together with the marketplace
they need to install it from, because a local marketplace path means nothing on their machine.
"""

from __future__ import annotations

import difflib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

BEGIN = "<!-- welleng:begin {name} -->"
END = "<!-- welleng:end {name} -->"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SECRET_RE = re.compile(
    r"(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)
ENV_REF_RE = re.compile(r"^\$\{[A-Z_][A-Z0-9_]*\}$")
PLUGIN_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*@[a-z0-9][a-z0-9-]*$")
MARKETPLACE_SOURCES = {"github": "repo", "git": "url", "url": "url", "directory": "path"}
HOOK_EVENTS = {"PreToolUse", "PostToolUse", "Stop", "SessionStart", "UserPromptSubmit", "SubagentStop"}


class SpecError(ValueError):
    """The spec is invalid or unsafe, nothing is written."""


@dataclass(frozen=True)
class Change:
    path: Path
    old: str | None
    new: str

    def diff(self, root: Path) -> str:
        rel = str(self.path.relative_to(root))
        a = (self.old or "").splitlines(keepends=True)
        b = self.new.splitlines(keepends=True)
        header = "new file" if self.old is None else "modified"
        body = "".join(difflib.unified_diff(a, b, f"a/{rel}", f"b/{rel}"))
        return f"# {rel} ({header})\n{body}"


def _block(name: str, text: str) -> str:
    return f"{BEGIN.format(name=name)}\n{text.strip()}\n{END.format(name=name)}\n"


def upsert_block(existing: str | None, name: str, text: str) -> str:
    """Insert or replace the managed block `name`, leaving every other byte untouched."""
    block = _block(name, text)
    if not existing:
        return block
    start, end = BEGIN.format(name=name), END.format(name=name)
    i = existing.find(start)
    if i == -1:
        return existing.rstrip("\n") + "\n\n" + block
    j = existing.find(end, i)
    if j == -1:
        raise SpecError(f"managed block {name} has no end marker, fix the file by hand")
    return existing[:i] + block.rstrip("\n") + existing[j + len(end) :]


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SpecError(f"{path.name} is not valid JSON ({e}), fix it by hand first") from e
    if not isinstance(data, dict):
        raise SpecError(f"{path.name} must hold a JSON object")
    return data


def _dump(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _extend_unique(items: list, new: list) -> list:
    return items + [x for x in new if x not in items]


def validate(spec: dict) -> None:
    if not isinstance(spec.get("intents"), list):
        raise SpecError("spec needs an 'intents' list")
    for intent in spec["intents"]:
        if SECRET_RE.search(json.dumps(intent)):
            raise SpecError("a credential-like string was found in the spec, credentials are never written")
        kind = intent.get("kind")
        if kind in ("claude_md", "rule_file"):
            if not NAME_RE.match(intent.get("name", "")):
                raise SpecError("name must be lowercase letters, digits and dashes")
            if not intent.get("text", "").strip():
                raise SpecError(f"{kind} {intent['name']} has no text")
        elif kind in ("deny", "ask"):
            if not intent.get("rules"):
                raise SpecError(f"{kind} needs rules")
        elif kind == "hook":
            if intent.get("event") not in HOOK_EVENTS:
                raise SpecError(f"unsupported hook event: {intent.get('event')}")
            if not intent.get("command", "").strip():
                raise SpecError("hook needs a command")
        elif kind == "mcp":
            if not NAME_RE.match(intent.get("name", "")):
                raise SpecError("mcp name must be lowercase letters, digits and dashes")
            for key, value in intent.get("config", {}).get("env", {}).items():
                if not ENV_REF_RE.match(str(value)):
                    raise SpecError(f"mcp env {key} must be a ${{VAR}} reference, never a literal value")
        elif kind == "local_setting":
            if not intent.get("key"):
                raise SpecError("local_setting needs a key")
        elif kind == "plugin":
            _validate_plugin(intent)
        else:
            raise SpecError(f"unknown intent kind: {kind}")


def _validate_plugin(intent: dict) -> None:
    if not PLUGIN_ID_RE.match(intent.get("id", "")):
        raise SpecError("plugin id must look like name@marketplace")
    if not isinstance(intent.get("shared", False), bool):
        raise SpecError("plugin shared must be true or false")
    market = intent.get("marketplace")
    if market is None:
        if intent.get("shared"):
            raise SpecError("a shared plugin needs its marketplace, so collaborators can install it")
        return
    if not intent.get("shared"):
        raise SpecError("a marketplace is only written for a shared plugin")
    if market.get("name") != intent["id"].split("@", 1)[1]:
        raise SpecError("the marketplace name must match the part of the plugin id after @")
    source = market.get("source", {})
    field = MARKETPLACE_SOURCES.get(source.get("source"))
    if field is None or not str(source.get(field, "")).strip():
        raise SpecError(f"marketplace source must be one of {sorted(MARKETPLACE_SOURCES)} with its location")
    if source["source"] == "directory":
        raise SpecError("a directory marketplace only exists on one machine, it cannot be shared")


def plan(spec: dict, root: Path) -> list[Change]:
    """Compute the file changes for `spec` under `root`. Reads files, writes nothing."""
    validate(spec)
    texts: dict[Path, str | None] = {}

    def read(path: Path) -> str | None:
        if path not in texts:
            texts[path] = path.read_text(encoding="utf-8") if path.exists() else None
        return texts[path]

    originals: dict[Path, str | None] = {}
    current: dict[Path, str] = {}

    def get(path: Path) -> str | None:
        return current.get(path, read(path))

    def put(path: Path, content: str) -> None:
        originals.setdefault(path, read(path))
        current[path] = content

    settings, local, mcp = root / ".claude" / "settings.json", root / ".claude" / "settings.local.json", root / ".mcp.json"
    for intent in spec["intents"]:
        kind = intent["kind"]
        if kind == "claude_md":
            path = root / "CLAUDE.md"
            put(path, upsert_block(get(path), intent["name"], intent["text"]))
        elif kind == "rule_file":
            path = root / ".claude" / "rules" / f"{intent['name']}.md"
            front = ""
            if intent.get("paths"):
                front = "---\npaths:\n" + "".join(f'  - "{p}"\n' for p in intent["paths"]) + "---\n\n"
            put(path, front + intent["text"].strip() + "\n")
        elif kind in ("deny", "ask"):
            data = json.loads(get(settings) or "{}") if settings in current else _load_json(settings)
            perms = data.setdefault("permissions", {})
            perms[kind] = _extend_unique(perms.get(kind, []), intent["rules"])
            put(settings, _dump(data))
        elif kind == "hook":
            data = json.loads(get(settings) or "{}") if settings in current else _load_json(settings)
            groups = data.setdefault("hooks", {}).setdefault(intent["event"], [])
            matcher = intent.get("matcher")
            hook = {"type": "command", "command": intent["command"]}
            group = next((g for g in groups if g.get("matcher") == matcher), None)
            if group is None:
                group = {"hooks": []}
                if matcher is not None:
                    group["matcher"] = matcher
                groups.append(group)
            if hook not in group["hooks"]:
                group["hooks"].append(hook)
            put(settings, _dump(data))
        elif kind == "mcp":
            data = json.loads(get(mcp) or "{}") if mcp in current else _load_json(mcp)
            data.setdefault("mcpServers", {})[intent["name"]] = intent["config"]
            put(mcp, _dump(data))
        elif kind == "local_setting":
            data = json.loads(get(local) or "{}") if local in current else _load_json(local)
            data[intent["key"]] = intent["value"]
            put(local, _dump(data))
        elif kind == "plugin":
            target = settings if intent.get("shared") else local
            data = json.loads(get(target) or "{}") if target in current else _load_json(target)
            data.setdefault("enabledPlugins", {})[intent["id"]] = True
            if intent.get("marketplace"):
                market = intent["marketplace"]
                data.setdefault("extraKnownMarketplaces", {})[market["name"]] = {"source": market["source"]}
            put(target, _dump(data))

    return [Change(p, originals[p], c) for p, c in current.items() if originals[p] != c]


def apply(changes: list[Change]) -> None:
    for change in changes:
        change.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = change.path.with_name(f".{change.path.name}.welleng-tmp")
        tmp.write_text(change.new, encoding="utf-8")
        tmp.replace(change.path)


def check(root: Path) -> list[str]:
    """Problems found in the project's Claude Code configuration, empty when it is healthy."""
    problems: list[str] = []
    files = [root / "CLAUDE.md", root / ".claude" / "settings.json", root / ".claude" / "settings.local.json", root / ".mcp.json"]
    files += sorted((root / ".claude" / "rules").glob("*.md")) if (root / ".claude" / "rules").is_dir() else []
    for path in files:
        if not path.exists():
            continue
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            problems.append(f"{rel}: file is empty")
            continue
        if SECRET_RE.search(text):
            problems.append(f"{rel}: contains a credential-like string")
        if path.suffix == ".json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                problems.append(f"{rel}: invalid JSON ({e})")
                continue
            if path.name.startswith("settings"):
                for event, groups in data.get("hooks", {}).items():
                    for group in groups:
                        for hook in group.get("hooks", []):
                            problems += _check_hook(root, rel, event, hook)
            if path.name == ".mcp.json":
                for name, server in data.get("mcpServers", {}).items():
                    for key, value in server.get("env", {}).items():
                        if not ENV_REF_RE.match(str(value)):
                            problems.append(f"{rel}: server {name} env {key} is a literal, use a ${{VAR}} reference")
        elif path.suffix == ".md":
            begins = re.findall(r"<!-- welleng:begin ([a-z0-9-]+) -->", text)
            ends = re.findall(r"<!-- welleng:end ([a-z0-9-]+) -->", text)
            if sorted(begins) != sorted(ends):
                problems.append(f"{rel}: managed block markers do not pair up")
    return problems


def notes(root: Path) -> list[str]:
    """Advice for the project's agent setup. Unlike `check`, a note is never a failure."""
    found: list[str] = []
    skills = root / ".claude" / "skills"
    if not any(skills.glob("verify-*/SKILL.md")):
        found.append("no verification skill under .claude/skills/verify-*/, run /welleng:verify-setup to create one")
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        text = claude_md.read_text(encoding="utf-8")
        m = re.search(r"<!-- welleng:begin rules -->(.*?)<!-- welleng:end rules -->", text, re.S)
        if m:
            for rule, enforcer in _rule_rows(m.group(1)):
                if not enforcer or enforcer.lower().startswith(("nothing", "none", "-")):
                    found.append(f"CLAUDE.md: rule has no enforcer, consider /welleng:correct: {rule}")
    return found


def _rule_rows(block: str) -> list[tuple[str, str]]:
    """The (rule, enforced by) pairs of the Markdown table in the `rules` block, header and divider excluded."""
    rows = []
    for line in block.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.strip().startswith("|") or len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        rows.append((cells[0], cells[1]))
    return rows[1:] if rows and rows[0][0].lower() == "rule" else rows


def _check_hook(root: Path, rel: Path, event: str, hook: dict) -> list[str]:
    command = hook.get("command", "").strip()
    if not command:
        return [f"{rel}: {event} hook has no command"]
    first = command.split()[0]
    if first.startswith("$") or first in ("cd", "export", "env", "bash", "sh", "python3", "python", "node", "uv"):
        return []
    if shutil.which(first) or (root / first).exists():
        target = root / first
        if target.exists() and target.is_file() and not target.stat().st_mode & 0o111:
            return [f"{rel}: {event} hook {first} is not executable"]
        return []
    return [f"{rel}: {event} hook command not found: {first}"]
