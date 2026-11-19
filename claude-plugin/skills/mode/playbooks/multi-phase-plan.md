# Multi-phase plan

You own the plan, not the code.
The plan is a checklist that an owner runs box by box and the user audits from the evidence.
Do not implement.

1. When the change is one or two files with an obvious approach, skip the plan, say so and stop.
2. Settle open questions with `playbooks/prototype.md` before you write.
   Ask the user only about a product or preference decision that no run can settle.
3. Write the plan file in the repository's local planning location when it has one, such as a gitignored `docs/research/`, otherwise in a scratch folder.
   Open with what changes, the pull requests in landing order and the dependency graph: which branch from the trunk, which wait for which, and the files each may touch.
   Then write one section per pull request, each one change with its own evidence, per `principles/sequence-verifiable-units.md`.
   Each section has checkboxes for its dependencies, the files it edits, the one change it builds, the result you see and its verification.
4. Tests alone are not enough.
   A pull request counts as verified only when its unit, live and, where relevant, performance boxes are all checked.
   Each live box drives the real surface with a concrete scenario and a pass predicate, and names the platform.
   A pull request that changes an interaction waits for the user's review before merge.
5. Hand back the plan path and stop.
   Execution starts on the user's explicit go.

**Reply:** the plan path, the pull requests with their dependencies, the set gated on review and what stays unproven.
