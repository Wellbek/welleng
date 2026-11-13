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
- psmux: a native Windows tmux-alike written in Rust on ConPTY, MIT licensed, that reads `.tmux.conf`, requires Windows 10 or 11, and installs through winget, Scoop, Cargo or Chocolatey.
  The project README reports session persistence and detach, and the repository is actively released, with version 3.4.0 published on 2026-10-13 `[search]`.
  It has not been run for this project, because the test machine is Linux.

## Decision

tmux carries layout, keybindings and persistence.
The terminal emulator only decides fonts, colours and how tmux is launched.
kitty stays the Linux emulator, WezTerm is the Windows emulator, and tmuxp YAML files define layouts and replace tmuxifier.

## Consequences

Swapping the emulator is a small per-OS file, not a rewrite.
Native Windows without WSL has no tmux, so it relies on psmux as a best-effort second tier.
`[spike]` Spike 6 cannot be completed on Linux.
It needs a Windows host or CI runner and checks four things: that psmux reads the repository's tmux configuration, that the prefix key and pane navigation work, that detach and reattach survive closing the terminal, and that `tmuxp` or an equivalent can load a layout.
Until then the tier stays "best effort, unverified".
See ADR 0004 for the Windows policy.
