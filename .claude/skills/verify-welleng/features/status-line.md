# Status line

The status line shows the model, the effort level, the context use and the cost of the session, and records them in the session's state file.

## Sub-features

- `status-render` shows `model | effort | ctx N% | $cost`.
- `status-state` writes the same values to `state/welleng/sessions/<session id>.json`.

## How to get to it (user POV)

- Start any session with the status line script configured.

## Driving it with drive.sh

Preconditions:

- The session is launched per the skill's `SKILL.md`.

- **Render.**
  After launch, run `$D wait '\| high \|' 30`.
  The pane shows a line such as `claude-sonnet-5-5 | high | $0.00`.
- **Context and cost.**
  Send any prompt and wait for the answer.
  The line gains `ctx N%` and a non-zero cost.
- **State.**
  Read the one file in `$EV/state/welleng/sessions/`.
  It holds `"effort": "high"`, the model id, `context_pct` and `cost_usd`.

## Gotchas

- The status line is opt-in, ADR 0016, so a machine without it shows Claude Code's default line.
