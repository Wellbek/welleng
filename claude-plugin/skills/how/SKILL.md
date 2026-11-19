---
name: how
description: "Explain how a subsystem or feature works, for code walkthroughs before a change and for placement, ownership and layering questions. Use for /welleng:how."
disable-model-invocation: true
---

# How

Answer "how does X work?" from the code.
If the scope is ambiguous, state your reading of it and go ahead, the user can redirect.

## 1. Explain

Spawn one `Explore` subagent with the user's question and this brief:

> Write an architectural explanation for a senior engineer who is new to this area.
> Explore the code and explain it well enough that they can start working in it with confidence.
> Cite `file:line` for every claim.
> Do not edit any file.

Run `git status --short` afterwards and confirm that nothing changed.

## 2. Present

Present the subagent's explanation.
Light edits for clarity or for context from the conversation are fine, but do not rewrite it.
Run it through `/welleng:write`.
