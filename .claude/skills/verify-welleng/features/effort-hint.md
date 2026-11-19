# Effort hint

After a prompt whose effort estimate is two or more levels away from the session's level, the user sees one hint line under the prompt.

## Sub-features

- `hint-light-at-high` recommends `/effort low` for a light prompt at `high`.
- `hint-cooldown` stays silent for a second hint within 30 minutes.
- `hint-log` records the estimate and the levels, never the prompt text.

## How to get to it (user POV)

- Type a short, light prompt, such as a rename, in a session at `high` effort.

## Driving it with drive.sh

Preconditions:

- The session started with `--effort high` and the status line shows `| high |`.

- **Light prompt.**
  Run `$D send "rename foo to bar"`, then `$D wait 'hint: this looks' 60`.
  The pane shows `UserPromptSubmit says: hint: this looks light, consider /effort low (now high).`
- **Cooldown.**
  Run `$D send "rename bar to baz"` and wait for the answer.
  No second hint line appears.
- **Log.**
  Read `$EV/state/welleng/hints.log`.
  It holds one JSON line with `"current": "high"` and `"recommended": "low"`, and no prompt text.
- **Proof.**
  Run `$D capture "$EV/01-hint.txt"`.

## Gotchas

- Claude Code 2.1.328 sends the prompt event without an effort level, so the hint depends on the status line state, see ADR 0021.
  Without the status line script the hint stays silent.
- The level in the state lags one prompt behind an `/effort` change until the status line refreshes.
