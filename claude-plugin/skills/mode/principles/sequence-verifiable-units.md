# Sequence work into verifiable units

Apply when you do multi-step work, such as sweeps, migrations and runs of similar edits, and when you order commits and PRs.

Order the work as small units that each end in a state you can check, and do not move on until the current one is green.

In a sweep, each unit is a bracket: a known-good state, one change, the check, then the next unit.
Run the per-unit check even when a tool makes the edits.

Deliver in the order that proves the work: the failing test before the fix, the subtraction before the reshape, the baseline before the treatment.
Each commit lands on its own.
