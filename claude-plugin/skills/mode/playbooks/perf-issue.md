# Perf issue

You own the measurement story.
Tie every fix to a measurement, and do not read source instead of measuring.

1. Capture a baseline on the matching surface and vet it with `../benchmark-checklist/SKILL.md`.
2. Trace the code to ground the hypotheses, and do not claim a ceiling without running it.
   Try the performance mantras in order, cheapest first, and stop when one meets the target:
   1. Do not do it.
   2. Do it, but do not do it again.
   3. Do it less.
   4. Do it later.
   5. Do it when the user is not looking.
   6. Do it concurrently.
   7. Do it cheaper.
3. Plan the fix from the trace.
   If it crosses a function boundary, run `../architect/SKILL.md` first.
   Delegate it to a `welleng:worker` on the `code` role, review the diff and capture a post-fix measurement.
   Verify each attempt before the next, per `principles/sequence-verifiable-units.md`.
4. Compare the artifacts with a query or a diff, not by eye.
   "Inconclusive" or a different surface is not a pass.
5. Cite the measurement in the pull request, and run `playbooks/opening-a-pr.md`.

For sustained improvement of one metric, use `playbooks/hillclimb.md`.

## When the cause is unknown

Diagnose before fixing.
The deliverable of this part is a cited diagnosis.

- **From a live process.**
  Capture the live signal: a CPU profile for a spinning process, a heap snapshot for a leak, a trace for a visual glitch.
  Reduce it to the hot function, the retainer chain or the loop that fires without input.
  Prove the mechanism with cheap instrumentation before you believe it.
- **From a captured artifact.**
  Load the profile, trace or dump with the right tool and turn it into something you can query, such as a SQLite table with one row per sample or frame.
  Query for the frames that hold the most time and walk to the hot path.
  If you have a paired capture, diff before and after, otherwise mark the finding as the strongest hypothesis the artifact supports.

Parse large artifacts in a subagent and keep the reduced finding in the main thread, per `principles/guard-the-context-window.md`.
Map every finding to a file, a symbol and a line.

**Reply:** the baseline, the post-fix number, the delta and the artifact paths, or for a diagnosis the signal, the finding, the proof and the source location.
