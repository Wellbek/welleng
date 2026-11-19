# Pause safely

You own a clean stop that a cold-start agent can resume from.
Use this only when the user asks for a pause.
On "keep going" or "do not stop", do not pause.

1. Stop at a safe boundary.
   Finish the current atomic step or back out of it, start nothing new and stop any running subagents.
2. Take no irreversible action to pause, such as a push or a new pull request.
3. Make the work durable.
   Commit uncommitted edits as one `wip:` commit on the current branch, and if the tree is broken, say so in one line of the commit body.
4. Write the resume note to `.git/welleng-resume-<slug>.md` in the repository, where git never tracks it.
   Capture the goal, what you were doing, progress and what is verified, the current state, the next steps, the key files and the gotchas.
   If a decision log exists, point at it instead of duplicating it.

**Reply:** where you are, what is on disk and what was only in your head, the commits you made, whether the tree is clean, the resume note path and the first action on resume.
