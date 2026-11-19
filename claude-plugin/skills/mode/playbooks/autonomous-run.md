# Autonomous run

You own the exit condition.
Define done, then drive to it without stopping.

1. State the exit condition as a checkable predicate before the first iteration, such as "tests green", "reproduction fixed" or "all three pull requests merged".
2. Pick the wake mechanism.
   Use the session's `/loop` command when it is available.
   For an event, such as CI finishing or a merge, run a background watcher that notifies you, with a long heartbeat as a fallback.
   Without an event, use a fixed heartbeat sized to when the result is worth checking again.
3. Each iteration makes the smallest change the evidence justifies, verifies it against the predicate, commits it if it advanced and discards it if it did not, per `principles/sequence-verifiable-units.md`.
4. Mid-run discoveries that support the goal are yours: broken skills, related bugs, flaky checks, tooling failures.
   Fix them in their own commits and return to the predicate.
   Surface only irreversible actions, product or preference decisions no experiment can settle, actions the Well-Engineering hard rules reserve for the user, or a real dead end.
5. Log every iteration with `../show-me-your-work/SKILL.md`: what changed and whether the predicate moved.
6. Stop when the predicate is met.
   A plateau is not a stop, so change approach to get past it.
   Never relax the predicate to declare victory.

**Reply:** the exit condition, the iterations run, what landed, what was discarded and the final state of the predicate.
