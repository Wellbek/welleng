# Bug fix

You own this task: plan, review, verify.
Delegate the investigation and the fix to subagents and stay in the lead.

Be scientific.
Every shipped line traces to runtime evidence.
A change that "might help" is a hypothesis, not a fix, and it does not ship.
When evidence refutes a hypothesis, revert what it motivated.

1. Reproduce the bug yourself, as close as possible to how a user meets it.
   Use the project's verification skill under `.claude/skills/verify-*/` when one exists.
   Ask the user to reproduce only with a specific reason the tools cannot reach the target, after driving it as far as it goes.
   If it will not reproduce directly, synthesize the trigger, tighten the conditions or add instrumentation until it fires.
2. Narrow down the cause.
   List the candidate hypotheses and rule them out until one survives, seeded with a trace of the affected code and `../why/SKILL.md` for regression history.
   Each pass, take the split that cuts the most remaining space, get runtime evidence and eliminate.
   When program state is unclear, add logging and read it as the code runs.
   Confirm the surviving mechanism with runtime evidence, per `principles/fix-root-causes.md`.
3. Plan the fix.
   If it crosses a function boundary, run `../architect/SKILL.md` first.
   Delegate the implementation to a `welleng:worker` on the `code` role with a specific scope.
4. Verify on the same surface as the reproduction.
   The original reproduction now passes.
   "Inconclusive" or a different surface is not a pass, so flag it.
   Unit tests show branch behavior, not the absence of the bug.
5. Commit the failing reproduction before the fix, per `../tdd/SKILL.md` when the bug has a cheap test path, and per `principles/sequence-verifiable-units.md`.
6. Run `playbooks/opening-a-pr.md`.

**Reply:** what was broken, the root cause, the fix and how you verified it, with the failing-then-passing output pasted verbatim and the platform it ran on.
