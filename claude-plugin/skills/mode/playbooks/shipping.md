# Shipping

You own what lands.
Verify each pull request independently, land only the verified run from the bottom of the stack, and keep your hands off the stack while it lands.
Merging changes a shared branch, so run this playbook only when the user asked to ship in this conversation.

1. Verify each pull request before it lands.
   One `welleng:worker` per pull request on the `verification` role, which did not write the code, runs the change the way a user would, parent against head.
   It posts `PASS`, `PASS+NOTES` or `FAIL` as a comment on the pull request.
   Green CI and an approving review are not verdicts, because neither runs the change as a user would.
2. Land only the contiguous verified run from the bottom.
   Walk up from the lowest unmerged pull request and stop at the first one without `PASS` or `PASS+NOTES`.
   That one is the ceiling.
3. Check that each verdict still describes the code.
   Compare `git patch-id` at the verdict's commit with the current head.
   If the patch changed, the change gets a fresh verdict.
4. Land bottom-up, one at a time, with `gh pr merge <pr> --squash`.
   Read the result back with `gh pr view <pr> --json state,mergedAt,baseRefName`, because a queued merge or an armed auto-merge is not a merge.
   After a merge, retarget the next pull request to the trunk with `gh pr edit <pr> --base <trunk>`, move its patch onto the merge result and push with `--force-with-lease`.
   Step 3 decides whether its verdict survives.
5. Change nothing else on the stack while it lands.
   If a merge stalls, find out why before you touch anything.
6. Stop at the ceiling.
   Extending the run takes new verdicts.

**Reply:** the verified run and its ceiling, each verdict and who produced it, what landed and how you confirmed it, and what the next gap needs.
