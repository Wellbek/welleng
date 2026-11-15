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

## Working style

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
