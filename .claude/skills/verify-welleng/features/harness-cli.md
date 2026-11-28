# Harness CLI

`welleng harness` plans and applies a project's Claude Code configuration from intents, and checks it afterwards.

## Sub-features

- `harness-plan` prints a diff and writes nothing.
- `harness-apply` writes the files only with `--yes`, and a second plan is empty.
- `harness-check` reports problems with a failing exit code and notes without one.

## How to get to it (user POV)

- Run `/welleng:harness` in a session, which calls these commands, or run them directly.

## Driving it with the shell

Preconditions:

- `welleng` is on `PATH`, or run it as `uv run --directory tools welleng` from the repository root.
- `P` is a fresh throwaway git project.

- **Plan.**
  Write `{"intents": [{"kind": "deny", "rules": ["Read(**/.env)"]}, {"kind": "plugin", "id": "welleng@welleng-local", "shared": false}]}` to `"$EV/spec.json"`.
  Run `welleng harness plan "$EV/spec.json" --project "$P"`.
  Exit code 0, a diff for `.claude/settings.json` and `.claude/settings.local.json`, and `ls -A "$P"` shows only `.git`.
- **Apply.**
  Run `welleng harness apply "$EV/spec.json" --project "$P" --yes`.
  It prints `wrote` lines, and running the plan again prints `nothing to change`.
- **Check.**
  Run `welleng harness check "$P"`.
  Exit code 0, a `note:` line about the missing verification skill, and `harness check: ok`.

## Gotchas

- `apply` without `--yes` prints the plan and exits 1 by design.
