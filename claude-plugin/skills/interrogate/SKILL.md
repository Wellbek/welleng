---
name: interrogate
description: "Adversarial review in which several models try to break a change or a design, keeping only findings that a run proves. Use for /welleng:interrogate, reviewing a PR, challenging a design or stress-testing code."
disable-model-invocation: true
---

# Interrogate

Adversaries try to break a change or a design.
A finding survives only when a run proves it.
Report the findings and do not apply fixes.

## Frame

The scope is what the user names.
Otherwise it is the branch diff from its merge base with the base branch, through the working tree.

State the intent the way `../in-your-own-words/SKILL.md` describes, from the user's message, the commits and the PR description.
If the intent stays unclear, ask the user.

A worktree starts from the current commit, so it already holds the committed part of the scope.
Write the uncommitted part to a patch so every adversary sees the same code:

```
git diff HEAD --binary > <scratch>/uncommitted.patch
git ls-files --others --exclude-standard > <scratch>/untracked.txt
```

## Fan out

Take the adversaries from the `panel` role in `../mode/roles.md`, by default `fable`, `opus` and `sonnet` at `high`.
State the number of adversaries and their models in one line before you spawn, because each one costs a full review.

Spawn them in one message as `welleng:worker` subagents with `isolation: "worktree"`.
Each brief holds the scope as a commit range, the intent, the patch path, the untracked file list with the main checkout's path, and this text:

> Apply the patch with `git apply` and copy the untracked files from the main checkout into your worktree.
> Break this change.
> Prove each finding with a run against the real code, such as a failing test, a repro script or command output that shows the wrong behavior.
> For a design or plan, run a prototype or probe the current tree.
> Keep repros in your own worktree.
> Report each finding with a title, the exact command, the output it printed, and the output the intent requires.
> Leave out anything you did not run, including style, naming, structure and risks that need a future change to matter.
> No findings is a valid result.

## Verify

Rerun each finding's command yourself, or in a `welleng:worker` on the `verification` role.
Keep a finding when the output shows the failure and the failure breaks the intent.
Drop the rest, and merge findings that share a root cause.
Adversaries find different failures, so the verdict keeps every verified finding.
Remove the adversary worktrees afterwards.

## Output

- **Intent**, the restatement.
- **Findings**, each with the command, its output, how it breaks the intent and the adversaries that found it.
  Say "no verified findings" when none survive.
- **Dropped**, for each adversary the number of dropped findings and why.
