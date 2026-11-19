---
name: show-me-your-work
description: "Keep a reviewable decision trail for long or unattended work, as a TSV log with one row per decision, its reason, its evidence and its result. Use for /welleng:show-me-your-work."
disable-model-invocation: true
---

# Show me your work

Keep one decision log per run of work.

## Format

One TSV file with one row per decision.
Cells stay on one line, and evidence is a pointer, never prose.
The columns are:

- `ts`, an ISO 8601 time in UTC.
- `phase`, the phase or workstream.
- `decision`, what was chosen or done, in one line.
- `why`, the reason in plain words.
  If a principle drove it, say the principle plainly.
- `evidence`, a commit, a pull request, a `file:line`, or the path of an artifact, a trace or a screenshot.
- `result`, the outcome, such as `tests green`, `reverted`, `INCONCLUSIVE` or `open`.

Write each row the way you would tell a teammate what you did, through `/welleng:write`.

## Logging a row

Use the helper in this skill's folder:

```
python3 -I <this skill's folder>/scripts/log.py <logfile> <phase> <decision> <why> <evidence> <result>
```

It stamps the time, writes the header on first use, flattens tabs and newlines, and quotes cells that a spreadsheet would run as a formula.

Log decision points and checkpoints, not every action: a fork you chose, a unit completed with its verification result, a pivot or revert with its trigger, a blocker, a fixed gate.
In a loop, log one row per iteration.

A run is one conversation, including its later turns.
When a run adds to a log that already has rows, its first row has phase `start` and names the time range of the rows it did not write.
Use phase `start` for nothing else.

## Where the log lives

By default the log is a working file, not committed: `decisions.tsv` in the work directory, or `.audit/<task-slug>.tsv` when several efforts run at once.
Add it to `.git/info/exclude` when the repository does not ignore it.
Commit it only when a reviewer needs the trail to trust the result.

## Rules

- The log is append-only.
  A wrong call gets a new row that supersedes it, never an edit or a deletion.
- Prefer evidence that a committed script produced over a one-off command.

## Audit the log before handing back

Walk this run's rows against what happened in this conversation, the commits and the files.

- Every row maps to a real decision or action.
- Every evidence pointer resolves and shows what the row claims.
- A fork, pivot or abandoned approach that shaped the work but has no row is a gap, so add one.

Correct the log, not the story.
Add a superseding row for a wrong one.

## Review by another model

Before handing back, spawn a `welleng:worker` on a different model from the one that did the work, such as `fable` when the work ran on `opus`.
Give it the log path, the commit range and the task, and ask it to flag what the user should look at:

- Decisions with weak or missing evidence.
- Verification that was skipped or claimed without proof.
- Choices that look risky in hindsight, such as a premature call, scope creep or a guard over a symptom.
- Gaps the user would miss on a quick skim.

Every reply for a run with a log ends with an "Attention" section.
Its first line is `reviewed by <model>`, then each flag with the rows it points at.
"No flags" is a valid result.

## Reading the log

`column -s$'\t' -t decisions.tsv` renders it in a terminal, and GitHub renders a committed TSV as a table.
Other skills route their audit trail here instead of inventing a format.
