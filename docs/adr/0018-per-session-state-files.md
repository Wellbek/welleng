# 0018 - Per-session state files written by hooks and the status line

Status: Accepted
Date: 2026-11-15

## Context

`claude agents --json` gives the session id, state, project and age, and nothing else.
The dashboard also needs the model, the effort level, context use, cost and the number of running subagents.
Those values are only available in hook events and in the status line payload, see ADR 0012.
ADR 0005 forbids reading files under `~/.claude/`, so the data has to be captured when it is delivered.

## Options considered

- Parse the session transcripts: forbidden by ADR 0005 and fragile.
- One shared state file: concurrent sessions would overwrite each other and need locking.
- One small JSON file per session, written atomically by the hook that receives the event.

## Decision

A hook script, `claude-plugin/hooks/state_writer.py`, handles `SessionStart`, `UserPromptSubmit`, `Stop`, `SubagentStart`, `SubagentStop` and `SessionEnd`.
A second script, `claude-plugin/hooks/statusline.py`, merges the status line fields into the same file and prints a compact line.
Files live in `$XDG_STATE_HOME/welleng/sessions/<session_id>.json` with mode 600, in a directory with mode 700.
`welleng agents` reads them and joins them to the `claude agents --json` rows by session id.

The files hold the session id, working directory, last event name, permission mode, model, effort level, context percentage, cost and the set of active subagent ids.
They never hold prompt text, assistant messages or the transcript path.
`SessionEnd` deletes the file, and `SessionStart` removes files older than seven days, so crashed sessions do not accumulate.
Session ids are matched against a strict pattern before they become a file name, so a hostile id cannot write outside the directory.

The plugin does not set the status line.
That setting belongs to the user, and replacing an existing status line would break behaviour they already rely on, see ADR 0016.
Using `statusline.py` is an explicit opt-in documented in the script.
Without it the dashboard still shows the hook-derived values: model from `SessionStart`, effort level, and subagents.
Context and cost need the status line.

## Consequences

- The writers print nothing and never raise, so they cannot add text to the model context or break a session.
- A session that never ran the hooks simply shows dashes, and a corrupt state file is ignored.
- Waiting-for-input is still taken from `claude agents --json`, because notification hooks fire late, see ADR 0012.
- Verified so far with subprocess tests on Arch `[verified: Arch]`.
  No live interactive session has produced these files yet, see `docs/verification/interactive.md`.
