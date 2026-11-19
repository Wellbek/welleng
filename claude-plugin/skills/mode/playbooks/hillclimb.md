# Hillclimb

You own the metric and the integrity of the experiment.
Supervise and review, and delegate the attempts.
This playbook is for sustained improvement of one measurable thing against a target.
A one-off fix is `playbooks/bug-fix.md` or `playbooks/perf-issue.md`.

The core discipline is one change, one measurement, keep or revert.
Never stack untested changes, and never claim a win from reading code.

1. Ground the workload before choosing the metric.
   Name the realistic dimensions that can move the result, such as data size, history, state and concurrency, and select a case that reproduces the user's complaint.
   Then fix one metric, the direction that counts as better, and a stop predicate that pairs a target with a minimum number of attempts.
2. Build the measurement harness, prove its sensitivity, then freeze it, per `principles/build-the-lever.md`.
   Vet it with `../benchmark-checklist/SKILL.md`, and make it print its error count and a count of the work done.
   Record the baseline and a green run of the regression tests before any change.
3. Open a decision log with `../show-me-your-work/SKILL.md`, one row per attempt, kept out of the repository.
4. Ground each hypothesis in a specific mechanism, ordered by the performance mantras in `playbooks/perf-issue.md`.
5. Loop, one hypothesis per iteration:
   - Hand the change to a `welleng:worker` on the `code` role with a tight scope, and review the diff.
     Run independent hypotheses in parallel worktrees.
   - Measure before and after with the frozen harness, and run the regression tests.
   - Keep the change only when the metric moves past the noise and the tests stay green, otherwise revert it in full.
   - Commit each accepted change on its own, staging only its files, and log the row either way.
6. Push past the first plateau by changing category, combining near-misses or rereading the source.
   Correctness and simplicity outrank the number.
7. Stop when the predicate is met or the remaining ideas are not worth their cost.
   Never relax the predicate, and surface a dead end instead of spinning.
8. Run `playbooks/opening-a-pr.md` with the accepted commits in the order they landed.

**Reply:** the metric and target, the baseline and final value with the percent change, iterations kept and reverted, each accepted change in one line, the log path and the next idea you would try.
