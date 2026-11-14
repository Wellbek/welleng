# 0015 - Opt-in shell integration that never edits existing files

Status: Accepted
Date: 2026-11-14

## Context

A dotfile manager that deploys `~/.zshrc` overwrites a long-lived personal configuration on the first apply.
The maintainer's existing zsh and prompt setup is large and is not described by this repository.

## Options considered

- Deploy `~/.zshrc`, `~/.config/starship.toml` and `~/.config/lazygit/config.yml`, which is the usual chezmoi layout and replaces existing files.
- Deploy a namespaced `~/.config/welleng/` tree and ask the user to add one line to their own `~/.zshrc`.

## Decision

Everything lives under `~/.config/welleng/`, including `shell/init.zsh`, `starship.toml` and `lazygit.yml`.
`init.zsh` guards every integration on the tool existing, uses the Well-Engineering prompt only when the user has no starship configuration, and appends its lazygit file after the user's own.
No existing file in `$HOME` is modified by an apply.

## Consequences

The new defaults do nothing until the user opts in with one line.
A full replacement of the shell setup is a separate, explicit later step that needs the maintainer's approval.
