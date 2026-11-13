# 0012 - Hook event data contract

Status: Accepted
Date: 2026-11-13

## Context

Agent monitoring, the project harness and model recommendations all depend on Claude Code hook events and the status line payload.
Their schemas are not a frozen API, so the project needs one written record of exactly which events and fields it relies on, and where each guarantee comes from.

This record was written from the official hooks reference, read on 2026-11-13 `[docs]`.
The installed version is Claude Code 2.1.323 `[verified: Arch]`.
No hook was run in a live session for this record, so everything below is documented behaviour and not yet observed behaviour.
The Phase 5 contract test, which runs against the real installed `claude`, is what turns it into verified behaviour.

## Decision

The project relies only on the events and fields in this table.

| Event | Fields and behaviour used | Notes |
|---|---|---|
| All events | `session_id`, `prompt_id`, `cwd`, `permission_mode`, `effort.level`, `hook_event_name`, `transcript_path` | The transcript path is recorded but never read, see ADR 0005 |
| `SessionStart` | `source` (`startup`, `resume`, `clear`, `compact`, `fork`), optional `model`, optional `session_title` | `model` can be absent, so check before reading |
| `SessionStart` on resume or fork | `seconds_since_last_response`, `context_tokens`, `prompt_cache_likely_expired`, `estimated_cache_write_usd` | Could drive a later "cache expired, resuming is costly" hint |
| `UserPromptSubmit` | `prompt` | Has no `model` field. Pasted content can arrive collapsed to a placeholder |
| `Notification` | `message`, optional `title`, `notification_type` | Cannot block or modify. Its `systemMessage` is discarded |
| `Stop` | `stop_hook_active`, `last_assistant_message`, `background_tasks[]`, `session_crons[]` | Lets a dashboard tell "done" from "paused on background work" |
| `SubagentStart`, `SubagentStop` | `agent_id`, `agent_type` | The only source of subagent counts |
| `PostModelSwitch` | the model switched to, `requested_model`, `source` including `auto` and `resume` | Cannot block. Fires for switches requested from another client, such as a phone |
| `SessionEnd` | `reason` | Default time budget is 1.5 seconds |
| Status line | `model.id`, `effort.level`, `context_window.used_percentage`, `cost.total_cost_usd`, `rate_limits.five_hour` and `seven_day` | Fields confirmed present in the status line reference |

Output the project uses:

| Output field | Effect | Used for |
|---|---|---|
| `hookSpecificOutput.additionalContext` | Added to the model context as a system reminder, capped at 10,000 characters | The `/harness` suggestion at `SessionStart` |
| `systemMessage` | A warning shown to the user | An optional one-off model hint, see the consequences |
| Plain stdout on `UserPromptSubmit`, `SessionStart` and `PostModelSwitch` | Also added to the model context | Hooks must print nothing except the JSON object |

## Consequences

Findings that shape the design:

- **The prompt hook cannot see the model.**
  Only `SessionStart`, and the model switch events, carry a model, and there is no `$CLAUDE_MODEL` variable.
  The hint scorer therefore reads the current model from the session state file that the status line script and the `PostModelSwitch` hook keep up to date.
- **A hint can be user-only.**
  `systemMessage` is documented as shown to the user, while only `additionalContext` and plain stdout enter the model context.
  The status line segment stays the primary delivery, and `systemMessage` is an optional second channel.
- **Waiting is detected from notifications.**
  `permission_prompt` fires only after a prompt has waited about six seconds, and `idle_prompt` about 60 seconds after a turn ends.
  The dashboard state "waiting" is therefore delayed by design, and `claude agents --json` stays the primary liveness source.
  `agent_needs_input` and `agent_completed` fire only while the agent view is open, so they are not relied on.
- **Remote Control is visible.**
  `CLAUDE_CODE_BRIDGE_SESSION_ID` is set in hook environments while a Remote Control connection is active, so the dashboard can show which sessions are connected.
- **Hook commands must not print profile noise.**
  Any extra text on stdout stops Claude Code from reading the JSON object, and it would otherwise enter the model context.
  Hooks run as a direct interpreter call, such as `python3 script.py`, and never through an interactive shell that sources a profile.
- **Time budgets.**
  Prompt and model switch hooks default to 30 seconds, but the project keeps them far below that.
  `SessionEnd` has only 1.5 seconds by default, so it does a single atomic file operation, and stale state is cleaned up by comparing against `claude agents --json`.
- **Typed slash commands bypass `PreToolUse`.**
  A separate `UserPromptExpansion` event fires for them, matched on `command_name`.
  This matters for ADR 0011.

Not yet verified `[spike]`:

- That `TMUX_PANE` reaches hook processes.
  Hooks inherit the parent environment, so it should, but it is an inference and the dashboard jump depends on it.
- How `systemMessage` renders when returned from `UserPromptSubmit`.
- That the status line payload in practice matches the reference, which the contract test checks.
