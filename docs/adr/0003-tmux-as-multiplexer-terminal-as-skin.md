# 0003 - tmux as the multiplexer, the terminal emulator as a skin

Status: Accepted
Date: 2026-11-13

## Context

Layout, keybindings and session persistence should not depend on one terminal emulator.
The same muscle memory must work on Linux and, through WSL2, on Windows.

## Options considered

- tmux: mature, best-in-class detach and persistence, runs on Linux and WSL2, no native Windows build.
- WezTerm built-in multiplexer: cross-platform, but detach and persistence are weaker and tied to its own server.
- Zellij: no Windows support and no gain over tmux for this project.
- kitty and Ghostty splits: no detach, no Windows build.
- psmux: a native Windows tmux-alike that reads `.tmux.conf`, but it is young and self-reported `[search]`.

## Decision

tmux carries layout, keybindings and persistence.
The terminal emulator only decides fonts, colours and how tmux is launched.
kitty stays the Linux emulator, WezTerm is the Windows emulator, and tmuxp YAML files define layouts and replace tmuxifier.

## Consequences

Swapping the emulator is a small per-OS file, not a rewrite.
Native Windows without WSL has no tmux, so it relies on psmux as a best-effort second tier `[spike]`.
See ADR 0004 for the Windows policy.
