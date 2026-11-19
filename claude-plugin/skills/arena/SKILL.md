---
name: arena
description: "Run N parallel attempts at the same task, pick the strongest as a base and graft the best parts of the others into it. Use for /welleng:arena, bakeoffs and contested designs."
disable-model-invocation: true
---

# Arena

Before launching anything, open a todo list with one entry per phase: frame, fan out, cross-judge, pick, graft, verify.

## Cost

An arena costs about N times a single attempt.
State N and the models before you spawn, in one line.
N defaults to 3.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate produces.
2. Write a rubric of three to six concrete, gradeable criteria for this task.
   Only you and the judge see it.
3. Take the runners from the `panel` role in `../mode/roles.md`, by default `fable`, `opus` and `sonnet` at `high`.
   Repeat one model when the work is bound by generation rather than judgment.
4. Give each candidate its own output location, per `../mode/principles/separate-before-serializing-shared-state.md`.
   For code, spawn with `isolation: "worktree"` and name the commit to start from.
   Otherwise use `<scratch>/arena-<slug>/candidate-<n>/`.

## Phase B: Fan out

Spawn all candidates in one message as `welleng:worker` subagents.
Each brief holds the task, the paths of shared context, its own output location and the request to return the artifact with a short rationale that names the alternatives it considered and rejected.
If a candidate produces nothing, go on with N-1 and note the dropout.

## Phase C: Cross-judge

After every candidate finishes, spawn one judge on the `judgment` role but a different model family from the session's own model, so a `fable` or `sonnet` judge when you run on `opus`.
Tell it to read only, and check `git status` afterwards.
The judge scores each candidate by path label, criterion by criterion, and recommends a base.
It never sees which model produced which candidate.

## Phase D: Pick a base

Read every candidate end to end and score each against the rubric yourself.
Compare with the judge.
Agreement confirms the pick, and disagreement means one of you is biased or the rubric is ambiguous, so read both rationales again.
Pick the base that a future maintainer can extend most easily without breaking invariants.
On a tie, prefer the cleaner boundary or the smaller API.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting, usually one or two things each.
Fold each graft in by hand so the result stays coherent, per `../mode/principles/redesign-from-first-principles.md`.
If the candidates converge on one shape, ship the consensus and note it.
If they diverge wildly, Phase A was under-specified, so reframe and rerun instead of averaging.

## Phase F: Verify

Verify the result like any other output, per `../mode/principles/prove-it-works.md`.
A problem the arena missed means either the frame was wrong or you missed a graft, so go back instead of patching over it.
Remove the candidate worktrees that hold nothing you keep.

## Output

The synthesized artifact and a short note: the base and why, the judge's verdict, each graft and its source, what was rejected and why, convergence or dropouts, and the verification result.
