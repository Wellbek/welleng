---
name: swarm
description: "Fan out N parallel workers over slices of a job or as a race, then return one aggregated report. Use for /welleng:swarm, parallel coverage, one worker per package or per file, and races."
disable-model-invocation: true
---

# Swarm

Before launching anything, open a todo list with one entry per phase: frame, fan out, aggregate, report.

## Phase A: Frame

1. State the done predicate and the report the swarm returns.
2. Choose the shape: slices of the work, N workers racing on one brief, or both.
   For a race, declare the selection rule before spawning: first pass, rank all, or best of.
3. Take the worker model from the `mechanical` role in `../mode/roles.md`.
   Use the `verification` role when the workers check correctness.
   For a race between models, name each arm's model up front.
4. State N and the models in one line before you spawn, because a swarm costs about N times one worker.
5. Give each worker its own writable output.
   When workers verify or measure commits, each brief names the exact SHAs and the method, and the worker records both in its result.

## Phase B: Fan out

Spawn all workers in one message as `welleng:worker` subagents.
Use `isolation: "worktree"` when a worker edits files, and name the commit it starts from.

Every brief stands alone: the goal, the scope, the exact slice or race arm, how to verify, and what to report.
Reports use `PASS`, `ISSUES` or `BLOCKED` with evidence.
A worker that can prove a defect lists every defect it can prove, not only the first.

If a worker drops out, go on with N-1 and note it.

## Phase C: Aggregate

Read every result.
Drop a result that does not record the SHAs and method its brief names, and respawn that worker once.
After a second miss, record a gap, which never counts as a pass.
For coverage, every slice needs a result.
For a race, apply the rule declared up front.
Do not paste raw worker output.

## Phase D: Report

Return one report in the chat: a result table, one line per issue, the gaps and dropouts, and the race rule when one applied.
Remove worker worktrees that hold nothing you keep.
