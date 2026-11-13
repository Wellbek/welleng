# 0008 - Recommend-only model hints

Status: Superseded by [0013](0013-effort-only-hints.md)
Date: 2026-11-13

## Context

Using a strong model and high effort for a trivial task wastes subscription usage.
The goal is a hint when the current configuration looks mismatched with the task, never an automatic switch.
Prompt length is a poor proxy for complexity.

## Options considered

- Switch models automatically: no officially supported way to rely on this, and it removes user control.
- Call a second model on every prompt to classify it: reliable, but costs usage on every prompt.
- Cheap local heuristics by default, with an optional model-based stage.

## Decision

Hints only recommend, and the user runs `/model` themselves.
The default scorer is local and costs nothing, using several signals together such as intent verbs, scope hints, session context, attachments and the previous turn.
A model-based classification stage exists but is off by default.

## Consequences

The design prefers false silence over false interruption.
A hint fires only when the estimate differs from the current configuration by at least two steps, confidence is above a threshold, a turn has just completed, and no cooldown or snooze is active.
Delivery is the least intrusive option available, a dim status line segment, with `hints snooze` and `hints off` to silence it.
The prompt hook receives the prompt text and the effort level but not the model, so the current model is read from the session state file kept by the status line and the model switch hook, see ADR 0012.
A model change made from a phone or another client also triggers that hook, so an accepted hint can be detected from either side.
Every recommendation is logged locally so thresholds are tuned from evidence.
Expected accuracy is good for the obvious extremes and silent in the middle, and the documentation says so.
