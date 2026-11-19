# Refactoring

You own the contract.
The structure changes and the behavior does not.

If the cleanup reveals a missing feature or a real bug, split it out and ship the structural change first against the pinned behavior.
Large or cross-cutting structural work belongs to `../figure-it-out/SKILL.md`.

1. Pin the behavior first.
   Write a characterization test, a snapshot or an equivalence harness that captures the current behavior before any structure moves.
   A type check and a lint are not a pin.
2. Name the structure the code is missing, per `principles/model-the-domain.md`.
   Keep boring code when the shape is already clear and local.
   The reshape must delete branches or invalid states, not add indirection.
3. Name the target shape: the module layout, types and call graph you would build today, per `principles/redesign-from-first-principles.md`.
   If it crosses a function boundary, run `../architect/SKILL.md` first.
4. Subtract before you add, per `principles/subtract-before-you-add.md`.
   Delete dead code, collapse one-caller wrappers and drop redundant validators before the new shape arrives.
5. Move in small behavior-preserving steps, each keeping the pin green.
   For an API reshape, migrate every caller and delete the old API in the same wave, per `principles/migrate-callers-then-delete-legacy-apis.md`.
   Spot-check every rename against the files, because strings and prose escape a symbol search.
   Delegate mechanical edits to a `welleng:worker` on the `code` role.
6. Prove that the behavior is unchanged on the real artifact, with an equivalence check for larger reshapes.
7. Confirm the change is worth keeping.
   If the diff does not lower reader load somewhere, per `principles/minimize-reader-load.md`, revert it.
8. Commit in order: the subtraction, the reshape, then the follow-on cleanup.
   Run `playbooks/opening-a-pr.md`.

**Reply:** the structure that changed, the pin, the equivalence proof, the reader-load change, and what shipped and what was reverted.
