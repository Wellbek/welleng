# Feature

You own the design: plan, review, verify.
Delegate the implementation and stay in the lead.

1. Trace the affected code.
2. Run `../architect/SKILL.md` for the shape, naming the data shape first.
3. Write a throughput checkpoint as four todo items.
   A dimension that does not apply keeps its item with `n/a` and the reason.
   - Blocking first steps, which run before any fan-out.
   - Independent workstreams, such as disjoint files, services or layers, which can run in parallel.
   - Shared mutable state, which you split by default, per `principles/separate-before-serializing-shared-state.md`.
   - The smallest safe decomposition, and if one worker is best, why.
4. Delegate the code to a `welleng:worker` on the `code` role with a specific scope: the file paths, the named data shape and its structure per `principles/model-the-domain.md`, and the success criteria.
   When the implementation admits several valid shapes and the choice matters, run `../arena/SKILL.md` instead, so the alternatives surface and a judge guards the pick.
   Port an improvement to a shared piece to every consumer and verify each one.
5. Verify on the matching surface, with the project's verification skill when one exists.
   "Inconclusive" or a different surface is not a pass, so flag it.
6. Shape the history into small ordered commits, building, verifying and committing each unit before the next, per `principles/sequence-verifiable-units.md`.
7. If the design is contested, run `../interrogate/SKILL.md` before shipping.
8. Run `playbooks/opening-a-pr.md`.

Code-coupled work, such as one feature or one migration, goes to a single owner who fans out internally after the blocking phase.
Fan out at the top level only for slices that produce independent artifacts.

**Reply:** what you built, what you chose and why, the throughput checkpoint and the open decisions, with a table for design alternatives.
