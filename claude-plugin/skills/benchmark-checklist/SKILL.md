---
name: benchmark-checklist
description: "Vet a performance number before you report or act on it. Checks the limiter, tuning, physical limits, errors, repeatability, end-to-end relevance and whether the work happened. Use for /welleng:benchmark-checklist."
disable-model-invocation: true
---

# Benchmark checklist

Use this when you produce a performance number: a before and after, a regression claim, a hillclimb harness, or a choice between libraries or settings.
Answer each question with evidence from a run, not a guess from reading the code.

For a quick ballpark the user asked for, one run is enough.
Still answer questions 4 and 7, and say that it is one run.
A choice between options is never a ballpark.

## Before you run anything

- Write down the claim you expect to make, in the words you would ship, such as "export is 30% faster at p50 on the 60k-row dataset".
  The questions test that sentence.
- Read the measurement script and note what it times, counts and ignores.
- Check the load with `uptime` and the core count with `nproc`.
  If the machine is busy and you cannot stop the load, interleave the sides so both see the same noise, and say so.

## The questions

1. **Why not double?**
   Name the limiter from a profile taken in a run you do not report, because profilers slow the work down.
   Use CPU per process (`top`, `pidstat`), a runtime profiler (`py-spy`, `perf`, `node --cpu-prof`), I/O wait and syscall counts (`strace -c`), then map the hot spot to source.
   If the load generator saturates first, you measured the load generator.
2. **Was it tuned?**
   Run every side the way production runs it: release builds, production flags, the same versions and data, caches as warm or cold as production sees them.
   If one side runs on defaults, you compared configurations, not implementations, so tune it and measure again before you pick a winner.
3. **Did it break limits?**
   Do the arithmetic against disk and network bandwidth and against your cores.
   Removing a piece that takes 10% of the run can make the run at most about 11% faster.
   A result past a limit measured a cache, a no-op or a bug.
4. **Did it error?**
   Count failures and non-success responses, and check that outputs are correct, not only present.
   If the script does not count errors, add the count.
5. **Does it reproduce?**
   Run each side at least 5 times, alternating A, B, A, B, and report the median and the range.
   A gap smaller than the run-to-run spread is no measurable difference.
6. **Does it matter?**
   Next to any micro result, measure the end-to-end path a user waits on, and report the micro result as a share of the whole.
7. **Did it even happen?**
   Confirm that the work ran inside the timed region: the request arrived, the rows were written, the result was used.
   Lazy code and timeouts produce numbers for work that never ran.

## Report

- Lead with the verdict: faster, slower, no measurable difference or inconclusive.
- Give the number with its unit, the run count, the range and the limiter.
  For example, "p50 went from 41 ms to 33 ms, median of 7 runs per side, range 32 to 35 ms after, bound by JSON parsing on one core."
- Call it inconclusive when you cannot name the limiter, when a side ran untuned, or when you could not answer questions 4 and 7, and name the gap.
- Keep one primary number in a PR body and link the runs.
