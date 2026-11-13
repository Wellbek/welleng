# 0006 - LazyVim base with an NvChad fallback

Status: Accepted
Date: 2026-11-13

## Context

The editor needs language servers, formatting, linting, Treesitter and good keymap discoverability.
The existing configuration is a clone of a third-party NvChad setup with local uncommitted edits, which is not a sound long-term base.

## Options considered

- NvChad: maintained, but language support is manual and the current copy is a fork.
- kickstart.nvim: minimal by design, so the project would re-assemble LazyVim.
- AstroNvim: viable, with no clear advantage here.
- LazyVim: very actively maintained, one extra per language, which-key built in.

## Decision

Use LazyVim as the base, with a `lua/user/` layer for personal keymaps and theme so they survive upgrades.
Keep the old configuration runnable as `NVIM_APPNAME=nvchad nvim` until LazyVim reaches parity, then retire it.

## Consequences

Nothing is deleted during migration.
`[spike]` Confirm the LazyVim extras behave on the target Neovim release, and pin plugin versions with the lockfile.
Extra names in the planning notes are from memory and are confirmed during the Neovim phase.
