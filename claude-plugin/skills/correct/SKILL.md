---
name: correct
description: "Find the mistakes agents keep repeating in this repository and make each one impossible. Tries architecture first, then types, then a lint whose error names the fix, then a test, and writes docs last. Keeps a table pairing each rule with what enforces it. Use for /welleng:correct."
disable-model-invocation: true
---

# Correct

The user keeps correcting agents in this repository for the same mistakes.
Change the repository so the next agent cannot make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example and takes the shortest path that compiles.
Design the repository so a change that looks right from one file is right for the whole repository.

## Find the mistake classes

Read the record, never Claude Code's transcripts:

- Recent commits, especially fixes, reverts (`git log --grep '^Revert'`) and follow-up commits that touch the same lines.
- Review threads, with `gh api repos/{owner}/{repo}/pulls/<number>/comments` on recent pull requests.
- The agent instruction files, such as `CLAUDE.md`, and the rules table if one exists.
- Comments that explain a workaround.
- The corrections the user gave in the current conversation.

Group the mistakes into classes.
A class counts once it has happened twice.

## Fix each class at the highest level that works

1. **Eliminate it with architecture.**
   Give each piece of state one owner and each task one supported way.
   Hide internals so the wrong import fails, replace hand-synced lists with one source of truth, and delete old ways and dead code an agent would copy.
2. **Enforce it with types**, so the bad state cannot be written.
3. **Enforce it with a check.**
   If bad code still compiles, add a lint, a hook or a CI check whose error names the file, type or function to use instead.
   If the pattern is already common, fail only when a change adds more.
4. **Test the behavior**, per `../mode/principles/test-behavior-not-implementation.md`.
5. **Write docs or agent rules last**, and only for judgment calls, because nothing fails when an agent skips them.

## Fix and prove

Fix the most frequent classes now, one commit each.
Prove each new check fails on a real past mistake, such as the commit that made it.
Run the same command locally and in CI.
An exception goes on the offending line, with a reason, an expiry date and the user's approval.

## Keep the rule table

Keep a table in the project's `CLAUDE.md` that pairs each rule with what enforces it, inside a managed block named `rules`.
When `welleng` is installed, write it through `welleng harness plan` and `welleng harness apply` with a `claude_md` intent named `rules`.
Otherwise edit the block between `<!-- welleng:begin rules -->` and `<!-- welleng:end rules -->` by hand.

| Rule | Enforced by |
|---|---|
| Example: no em dash in tracked files | `scripts/check-hygiene.sh`, run by the pre-commit hook and CI |
| Example: reproduce a bug before fixing it | Nothing, judgment call |

When the user corrects you, fix the mistake and add the rule.
If the rule was already there and nothing enforces it, that is a repeat, so fix it at the highest level in the same change.
Drop a rule once its mistake cannot happen.

**Reply:** each class with its evidence, the level you picked, and why a higher level did not work.
