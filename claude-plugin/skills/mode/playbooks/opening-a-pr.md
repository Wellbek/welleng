# Opening a PR

Every other playbook ends here.

1. Work from a branch or worktree off the trunk, and keep unrelated work out of it.
2. Shape the history into small commits that each land on their own, with Conventional Commits subjects and one concern per commit.
3. Clean the diff.
   Run `../no-comments/SKILL.md` on code changes.
   If the session offers the built-in `simplify` skill, run it over the diff as well.
4. Run the project's checks, such as the tests, the linters and `scripts/regression.sh --strict` in the Well-Engineering repository, and paste the result.
5. Write the title as `type(scope): subject`, naming a real symbol when one carries the change.
6. Write the body through `../write/SKILL.md`: at most 40 lines under the headings `Why`, `What changed`, `Scope`, `Tradeoffs`, `Blast radius` and `Verification`, with empty ones dropped.
   `Tradeoffs` lists only the rejected alternatives a reviewer would ask about.
   `Verification` names the platform each check ran on.
7. Follow the user's instruction files on attribution.
   In a Well-Engineering setup, no commit or pull request mentions an AI assistant or co-authorship.
8. Push and open the pull request ready for review with `gh pr create`, never as a draft.
   Stack follow-ups by base branch.
   Pushing is outward-facing, so do it only when the user asked for a pull request or a push in this conversation.

Opening a pull request does not start `playbooks/babysit.md`.
