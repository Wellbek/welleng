# Worktree cleanup

This playbook deletes local state with no code review to catch a slip, so the gates below are the review.

1. Record `df -h .` and list the worktrees with `git worktree list --porcelain`.
   For each one, collect its size (`du -sh`), the last commit date, whether its branch is merged into the trunk (`git branch --merged <trunk>`), its uncommitted tracked edits and untracked files (`git -C <path> status --porcelain`), and its pull request state (`gh pr list --head <branch> --state all`).
   Read the paths from git, never type them by hand.
2. List the live Claude Code sessions with `claude agents --json`, or `welleng agents` in a Well-Engineering setup.
   A worktree that is a live session's working directory is in use.
   Ask the user which other worktrees they consider in use, because the list cannot see everything.
3. Pause on irreversible loss.
   Uncommitted tracked edits are lost when a worktree is removed, so show the diff and get a decision first.
   Untracked scratch files are safe to drop, but name them.
   Clean, merged and unused worktrees proceed.
4. Remove the confirmed set with `git worktree remove <path>`, adding `--force` only for a worktree the user cleared.
   Then run `git worktree prune`.
   Branch refs survive, so no commits are lost.
5. Record `df -h .` again and list the worktrees.

**Reply:** the free space before and after, the worktrees removed, and one line for each one kept with the reason.
