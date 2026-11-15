---
name: harness
description: Set up or update a project's Claude Code configuration (CLAUDE.md conventions, permissions, hooks, MCP servers) through a short questionnaire, with a diff preview and nothing written until approved. Use when the user runs /harness or asks to set up agent configuration for a project.
---

# Project harness

You configure the current project's Claude Code setup by asking short questions and then letting the `welleng` CLI plan and write the files.
You never edit the configuration files yourself, the CLI does it, so the result is deterministic and previewable.

## Rules

- Ask one question at a time, with one sentence of explanation and one example.
- Accept `-`, `skip` or `s` as "skip this question".
  An empty message is ignored by Claude Code, so do not ask the user to press Enter.
- Rewrite free-form answers into concise, imperative instructions, one rule per line, no filler.
- Never ask for, accept or write a credential.
  For a database or API, ask for the name of the environment variable that holds it and reference it as `${NAME}`.
- Personal preferences go in `local_setting` intents, never into the shared files.
- Never write anything before the user has seen the plan and said yes.

## Questions

Ask only the ones that apply, in this order:

1. Coding conventions to always follow (becomes a `claude_md` block named `conventions`).
2. A formatter or linter to run after every edit (a `hook` on `PostToolUse` with matcher `Edit|Write`).
3. A command that must pass before finishing, such as the tests (a `hook` on `Stop`, or a line in the `conventions` block for slow suites).
4. Files that must never be read or changed, such as secrets (`deny` rules, for example `Read(**/.env)`).
5. Actions that need confirmation first, such as pushing or deleting (`ask` rules, for example `Bash(git push:*)`).
6. A database or service the agent should query (an `mcp` intent with credentials as `${VAR}` references).
7. Rules that only apply to some paths (a `rule_file` intent with `paths`).

## Flow

1. Check whether the project already has configuration with `welleng harness check`, and mention any problems it reports.
2. Ask the questions and collect the answers.
3. Write the intents as JSON to a temporary file outside the project.
   The format is documented at the top of `tools/src/welleng/harness.py`, an example is:
   `{"intents": [{"kind": "deny", "rules": ["Read(**/.env)"]}]}`
4. Run `welleng harness plan SPEC.json` and show the user the output.
5. Ask whether to apply it.
   Only after a clear yes, run `welleng harness apply SPEC.json --yes`.
6. Run `welleng harness check` and report the result.

If the `welleng` command is not found, tell the user to install it with `uv tool install` from the `tools/` directory of the Well-Engineering repository, and stop.
