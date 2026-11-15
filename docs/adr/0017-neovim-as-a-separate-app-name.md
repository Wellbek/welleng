# 0017 - Neovim runs as a separate NVIM_APPNAME

Status: Accepted
Date: 2026-11-15

## Context

ADR 0006 chose LazyVim and said the old configuration stays runnable as a fallback.
A chezmoi-managed `~/.config/nvim` would replace the maintainer's existing, working Neovim setup on the first apply, which ADR 0015 rules out.

## Decision

The configuration lives in `home/dot_config/welleng-nvim/` and runs as `NVIM_APPNAME=welleng-nvim nvim`.
Its config, data, state and cache directories are all separate from the default ones.
`lazy-lock.json` pins every plugin, and `scripts/nvim-container.sh --update-lock` regenerates it in a container.
`tests/e2e/nvim.sh` restores the pinned versions in a clean container and checks that LazyVim loads without errors, that the user keymap layer and the Claude Code bridge keys exist, and that no plugin failed to load.
`exrc` is on, and Neovim asks before trusting a project-local file.
The Claude Code bridge starts only the plugin's loopback server, Claude itself stays in its tmux pane, see ADR 0010.

## Consequences

Switching the default `nvim` to this configuration is a separate step that needs the maintainer's approval, for example an alias.
The container test proves the configuration loads, it does not prove that language servers work, because Mason installs them on first use of a file type.
`uninstall.sh` removes the `welleng-nvim` directories and leaves `~/.config/nvim` alone.
