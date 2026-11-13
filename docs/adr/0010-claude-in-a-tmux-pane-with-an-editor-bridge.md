# 0010 - Claude in a tmux pane with an editor bridge

Status: Accepted
Date: 2026-11-13

## Context

Claude Code should work with the editor, with selection sharing and diff review, without being trapped inside it.
The session should be visible to monitoring and to Remote Control as an ordinary session.

## Options considered

- Run `claude` in a Neovim terminal buffer: the session dies when Neovim quits.
- Use only a terminal split with no bridge: loses selection and diff review.
- Run `claude` in a tmux pane and let claudecode.nvim provide only the bridge.

## Decision

`claude` runs in a persistent tmux pane.
claudecode.nvim provides the bridge only: selection, `@file` references and native diff review.

## Consequences

The session survives Neovim quitting, tmux navigation is uniform, and the dashboard and Remote Control see an ordinary session.
`[spike]` Confirm claudecode.nvim supports an external terminal provider, and that the CLI finds the Neovim server through the IDE lock file.
If it does not, fall back to an editor-hosted terminal.
