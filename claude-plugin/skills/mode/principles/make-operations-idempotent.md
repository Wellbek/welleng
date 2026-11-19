# Make operations idempotent

Apply when you design commands, lifecycle steps or loops that run amid crashes, restarts and retries.

Every state-changing operation converges to the correct state however many times it runs and wherever the previous run stopped.

Derive each step from the state that exists, not from what the previous run meant to do.
Read the current state, compare it to the goal and apply only the difference.

Anything a run leaves behind, such as a lock, a temporary file or a half-written record, must be recognizable as stale by the next run.
Write to a temporary path and rename it into place.

Ask what happens if it runs twice, and what happens if the previous run crashed at every possible point.
