# 0021 - The effort level for hints comes from the status line state

Status: Accepted
Date: 2026-11-19
Refines: [0013](0013-effort-only-hints.md)

## Context

ADR 0013 assumed that the `UserPromptSubmit` hook input carries the session's effort level.
A live interactive session on Claude Code 2.1.328, started with `--effort high`, sent this hook input with the keys `cwd`, `hook_event_name`, `permission_mode`, `prompt`, `prompt_id`, `scratchpad_dir`, `session_id` and `transcript_path`, and no effort level `[verified: Arch]`.
The hint hook therefore counted every prompt as "no effort level" and never recommended anything.
The status line payload of the same session did carry `effort.level`, and the status line script recorded it in the per-session state file of ADR 0018 `[verified: Arch]`.

## Options considered

- Keep reading only the hook input: hints never fire on this version.
- Read Claude Code's own session files: forbidden by ADR 0005.
- Fall back to the effort level the welleng status line recorded for the same session id: uses welleng's own state, written from an official interface.

## Decision

The hint hook uses the effort level from the hook input when it is present.
Otherwise it reads the level from `$XDG_STATE_HOME/welleng/sessions/<session_id>.json`, which the status line script writes.
The session id is matched against the same pattern the state writer uses before it becomes part of a path.

## Consequences

- Hints work in interactive sessions when the opt-in status line script is installed `[verified: Arch]`.
- Without the status line script, hints stay silent, as before, and `welleng hints report` shows the prompts that arrived without a level.
- The level can lag one prompt behind an `/effort` change if the status line has not refreshed yet.
- If a later Claude Code version adds the level to the hook input again, the hook prefers it automatically.
