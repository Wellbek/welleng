---
name: why
description: "Explain why something is built the way it is, from the record and not the code, for design rationale, regressions, postmortems and decisions. Use for /welleng:why."
disable-model-invocation: true
---

# Why

Answer from the record, not from the code.

1. Find the change that introduced the target and every later change to it.
   Use `git log -S '<symbol>'`, `git log -L` for a function, `git log --follow -- <path>` and `git blame -w -C`.
2. Read what the authors wrote: the commit messages, then the pull request and its review threads.
   Find the pull request with `gh pr list --search <sha> --state all`, read it with `gh pr view <number> --comments`, and read review threads with `gh api repos/{owner}/{repo}/pulls/<number>/comments`.
3. Read the decision records when the repository keeps them, such as `docs/adr/`, and any linked issue.
4. When that trail is thin, look at other sources the repository points to, such as a changelog entry or the documentation of a dependency.

Cite what the authors wrote, with the commit, pull request or file.
Mark your own inferences as inferences.
Say plainly which part of the question the record does not answer.
