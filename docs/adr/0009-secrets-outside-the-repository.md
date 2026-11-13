# 0009 - Secrets live outside the repository

Status: Accepted
Date: 2026-11-13

## Context

API keys in shell startup files and editor configs are easy to leak, especially in a repository that is meant to become public.
The project handles several credential types: Claude subscription login, third-party API keys and SSH keys.

## Options considered

- Keep keys in shell rc files, which is simple but leaks through dotfile repositories.
- A secrets manager such as `age` or `pass`, which is better but heavier to adopt first.
- A mode-600 file outside any repository, with secret scanning to catch mistakes.

## Decision

Four kinds of state are kept strictly separate:

| Class | Location | Tracked |
|---|---|---|
| Tracked configuration | this repository | yes |
| Local machine configuration | `~/.config/welleng/local.toml`, `~/.ssh/config.d/` | no |
| Credentials | `~/.config/welleng/secrets.env` with mode 600, `~/.ssh`, the OS keychain | never |
| Runtime state | `$XDG_STATE_HOME/welleng`, on Windows `%LOCALAPPDATA%\welleng` | no |

Scripts and shell aliases read credentials from `secrets.env` and never embed them.
Secret scanning runs in a pre-commit hook and in CI from the first commit.

## Consequences

Subscription login is used only by the Claude Code CLI, and API-key providers sit in a separate lane with one provider selector.
On WSL, `chmod 600` only works on the ext4 filesystem, not under `/mnt/c`.
On Windows the file permission is set through an NTFS ACL.
An optional move to `age` or `pass` stays open for later.
