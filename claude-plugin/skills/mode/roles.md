# Roles

Every subagent gets an explicit model and effort level from its role.
Pass both as the `model` and `effort` parameters of the `Agent` tool.

## Defaults

| Role | Model | Effort | Used for |
|---|---|---|---|
| `code` | `opus` | `xhigh` | Delegates that write code in the feature, refactoring, bug fix, perf and hillclimb playbooks |
| `judgment` | `opus` | `high` | Prose, design calls, plans, judges and pickers |
| `verification` | `opus` | `high` | Rerunning a repro or a finding, checking a claim against the real artifact |
| `mechanical` | `sonnet` | `medium` | Trivial mechanical edits and swarm workers |
| `dispatch` | `haiku` | `low` | Agents that only dispatch, poll or pack results |
| `panel` | `fable`, `opus`, `sonnet` | `high` | One seat each in review and design panels, such as interrogate and arena |

## Overrides

If `~/.config/welleng/roles.md` exists, read it once per session.
Each line has the form `<role>: <model> <effort>`, such as `code: opus high`.
The `panel` line lists its seats separated by commas, such as `panel: fable high, opus high`.
The value `inherit` means omit `model` and `effort`, so the subagent runs on the session's model.
A role without a line keeps its default.
Lines starting with `#` are comments.

## Adjusting a level

- Start from the role's level.
  Raise it one step for the hardest or subtlest work and lower it one or two steps for routine work.
- Never go above `xhigh` unless the user asks for `max`.
- Run `fable` outside a panel only when the user named it for this task, or after two `opus` runs at `xhigh` of the same brief failed its check.
  Say which of the two applied.
- Panel seats keep their listed level, so the panel stays diverse.

## When the tool rejects a value

If the `Agent` tool rejects a model or an effort value, never pass it again in this session.
Drop the effort level first, then the model, and say what ran instead.
