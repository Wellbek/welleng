# 0013 - Effort-only hints

Status: Accepted
Date: 2026-11-13
Supersedes: [0008](0008-recommend-only-model-hints.md)

## Context

ADR 0008 recommended both a model and an effort level.
The prompt hook does not receive the model, only the prompt text and the effort level, see ADR 0012.
Recommending a model would therefore need extra state from the status line and the model switch hook.

Effort is also the lever that fits the goal.
Claude Code's effort levels control how much adaptive reasoning the model spends, so a lower level is faster and cheaper for straightforward work `[docs]`.
The maintainer decided that effort alone is enough.

The effort scale is `low`, `medium`, `high`, `xhigh` and `max`, and Opus 4.6 and Sonnet 4.6 have no `xhigh` `[docs]`.
The default for the current model families is `medium` `[docs]`.
The level can be changed from the terminal with `/effort` and from a connected phone, where it applies to that session only `[docs]`.

## Options considered

- Recommend model and effort, as in ADR 0008: needs model state, and changes the model more disruptively than the level.
- Recommend effort only: uses data that is already in the hook input.
- Recommend nothing: no protection against wasting usage on trivial tasks.

## Decision

Hints recommend an effort level only, never a model.
They never switch anything automatically, and the user runs `/effort <level>` themselves.

The scorer stays local and free by default, combining intent verbs, scope hints, session context, attachments and the previous turn.
A model-based classification stage exists but is off by default.

Levels are mapped onto a scale of 0 to 4 for `low`, `medium`, `high`, `xhigh` and `max`.
A task estimate maps to a recommended level:

| Estimate | Recommended level |
|---|---|
| light | `low` |
| standard | `medium` |
| heavy | `high` |

`xhigh` and `max` are never recommended, they remain a deliberate choice by the user.

A hint fires only when all of these hold:

1. The recommended level differs from the current level by at least two steps, in either direction.
2. Confidence is above the threshold.
3. It is the first prompt after a completed turn.
4. No cooldown, snooze or global switch is active.
5. The hook input carries an effort level, so a model without effort support stays silent.
6. The prompt does not contain `ultrathink`, and no skill set the level for that turn, because a deliberate one-turn raise is not a mismatch.

## Consequences

The scorer needs only the hook input and its own cooldown state, so the model, the status line state file and the model switch hook are not on its path.
The dashboard still shows the model, taken from the status line, for display only.

An accepted hint is detected when the effort level in a later prompt moves toward the recommendation, whether the change was made in the terminal or on a phone.

Delivery, logging and the controls are unchanged from ADR 0008.
The status line shows a dim segment such as `hint: /effort low`, `systemMessage` is an optional second channel, `hints snooze` and `hints off` silence it, and every recommendation is logged locally so thresholds are tuned from evidence.
The design still prefers false silence over false interruption, and the documentation says expected accuracy is good for the obvious extremes and silent in the middle.

Not yet verified `[spike]`:

- Whether `effort.level` in the hook input is the effective level or only the configured one, which matters on models that fall back from `xhigh` to `high`.
  The Phase 8 contract test reads it from a real session.
