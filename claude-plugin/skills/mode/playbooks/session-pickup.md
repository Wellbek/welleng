# Session pickup

You own the resume point.
Read the prior trail, do not redo it.

1. Locate the prior trail.
   To continue a conversation of your own, the user resumes it with `claude --resume` or `/resume`.
   To take over another agent's work, use what it left in the repository: the branch and worktree, its commits, a resume note from `playbooks/pause-safely.md` in `.git/welleng-resume-*.md`, a decision log from `../show-me-your-work/SKILL.md`, and the pull request with its comments.
   Never read Claude Code's transcript files.
2. Rebuild the operational state: what already landed (`git log`, `git diff` against the base), the open todos and the decisions made.
   Treat the trail as authoritative input and resist re-deriving it.
3. Compare what shipped with what was planned and name the resume point.
   Do not rerun the prior reproduction or redo completed work.
4. Route the remaining work to the matching playbook.
5. Verify the inherited claims against the original goal on the real artifact, per `principles/prove-it-works.md`.
   A passing prior self-report is not proof.

**Reply:** where the prior agent stopped, what you inherited and what you redid, the resume point and the outcome.
