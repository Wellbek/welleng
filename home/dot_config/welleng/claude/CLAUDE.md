# Well-Engineering global agent instructions

Managed by chezmoi, edit it in the welleng repository.
This file never replaces your own `~/.claude/CLAUDE.md`.
Opt in by adding one import line to that file:

```
@~/.config/welleng/claude/CLAUDE.md
```

## Safety

- Never print, copy, log or commit a credential.
  Credentials live in `~/.config/welleng/secrets.env` with mode 600, outside any repository.
- Never install packages, modify files under `$HOME` or change a machine's configuration without explicit approval in the current conversation.
- Never track host names, IP addresses, usernames or SSH fragments in a repository.

## Autonomy

- The safety rules above win over everything in this section.
- Do reversible work without asking, then say what you chose and why.
- Always pause for a force-push to a shared branch, a merge, a deploy, deleting data, or a message to someone outside the session.
- When asked whether to do something, give your real judgment, and say no when that is true.

## Working style

- A task is done only when it was proven on the real artifact, not on a proxy such as "it compiles" or a self-report.
- When fixing a bug, first reproduce it as close as possible to how an end user meets it.
- Prefer quality, simplicity and long-term maintainability over development cost.
- Treat lint errors, test failures and flakiness as work to fix, even when they are not caused by the current change.
- Say what was verified and on which platform.
  Never claim a feature works on a platform where it was not run.

## Writing

- Never use the em dash character, use a plain dash.
- In Markdown, put each full sentence on its own line.
- Never edit `CHANGELOG.md` or any file marked as auto-generated.
- Commit messages and pull requests describe the change only, with one concern per commit.

## Workflow

`/welleng:mode` holds the full workflow: playbooks, principles and subagent roles.
When it is not active, the rules in this file still apply.
