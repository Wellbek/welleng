# Explain the number

Apply when you measure, or you trust, report or act on a measured number such as a speedup, a regression, a latency or an eval result.

- Write down the decision before the run, with the result that would change it and the noise floor.
- Ask "why not double?" and name the resource or code path that bounds the result, from a profile taken during a run.
- List what else the number could be measuring, such as errors, cached or skipped work or noise, and rule each one out with evidence.
- Keep the run count, the spread and the limiter with the number.

For a performance number, run `/welleng:benchmark-checklist`.
