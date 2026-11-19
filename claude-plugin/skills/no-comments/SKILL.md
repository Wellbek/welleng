---
name: no-comments
description: "Strip comments before review with the comment-reviewer subagent, fix what its flags point at, and offer to encode claimed constraints as checks. Use for /welleng:no-comments."
disable-model-invocation: true
---

# No comments

## Scope

Use the files or diff the user names.
Otherwise use the current diff against the base branch, by default `main`, including the working tree.

## Steps

1. Spawn the `welleng:comment-reviewer` subagent with the scope, on the `judgment` role from `../mode/roles.md`.
   Do not restate its rules.
2. Inspect its report and its diff.
   Reject an edit to application code, an edit outside the scope, a deleted comment that one of its exceptions protects, and a `MUST KILL` flag whose reason is wrong.
   Before accepting a thin `IMPORTANT` or `do not remove` verdict, trace the symbol or run `../why/SKILL.md` on it.
   If a report fails these checks, revert it and rerun the reviewer once with the failure named.
   If the second report fails too, report the work as open.
3. Fix trivial accepted flags directly: delete a dead path, drop a parameter, use the real API.
   If a fix needs a new shape, run `../architect/SKILL.md` once for all accepted flags and stop at the sketch.
4. Make the smallest root-cause fix inside the scope, per `../mode/principles/fix-root-causes.md`, and remove every workaround the flags name.
   If the root cause is outside the scope, land the in-scope part and report the rest as open.
   Never add a guard over a symptom.
5. A constraint comment such as `do not remove` or `talk to X before changing` gets an offer: the cheapest in-scope type, runtime check, test or lint that enforces it.
   Encode it only after the user approves, then delete the comment.
   Otherwise delete the comment and report the constraint as unenforced.
6. Report the number of deleted comments, restored comments, reruns, the architect sketch, the fixes, the encodings offered and made, and the open work.
