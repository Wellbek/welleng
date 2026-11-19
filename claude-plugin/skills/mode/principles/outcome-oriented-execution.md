# Outcome-oriented execution

Apply when you run a planned rewrite or migration with explicit phase boundaries.

Optimize for the intended, verifiable end state rather than for smooth intermediate states.
Keeping every intermediate step stable often creates compatibility code that becomes long-lived debt.

- Converge on the target architecture.
- Accept intermediate breakage only when it is planned, scoped and reversible, and declare where it is allowed.
- Keep high-signal checks on the areas you touch while migrating.
- Require full static and runtime verification when the plan completes.
