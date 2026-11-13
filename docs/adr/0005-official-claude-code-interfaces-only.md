# 0005 - Official Claude Code interfaces only

Status: Accepted
Date: 2026-11-13

## Context

The project monitors sessions, shows model and usage data, and recommends models.
Claude Code already exposes machine-readable interfaces for most of this `[docs]`.

## Options considered

- Parse `~/.claude/projects/*.jsonl`, `history.jsonl` or the `sessions/` directory: undocumented formats that can change without notice.
- Parse terminal output with a PTY wrapper: fragile, as used by some third-party session managers `[search]`.
- Use the official CLI JSON output, hooks, the status line payload, settings and plugins.

## Decision

Use only official interfaces: `claude agents --json`, hooks, the status line, settings and plugins.
Never read Claude Code's internal files.

## Consequences

The glue code stays small, because the CLI already provides listing, attach, logs, stop and Remote Control `[docs]`.
The JSON schema is not a frozen API, so adapters validate fields defensively and map unknown values to "unknown".
A contract test runs against the real installed `claude`, and `welleng doctor` reports drift.
Model and usage data exist only for sessions that ran the hooks and status line, so older sessions show partial data.
