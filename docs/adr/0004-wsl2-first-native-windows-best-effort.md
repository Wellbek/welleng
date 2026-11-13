# 0004 - WSL2 first, native Windows best effort

Status: Accepted
Date: 2026-11-13

## Context

The environment is terminal-centric and built on tools that are Unix-first.
Windows must still be a supported platform.

## Options considered

- Native Windows only: tmux and several tools do not exist natively, so parity is not achievable.
- WSL2 only: simplest, but excludes machines where WSL2 cannot be enabled.
- WSL2 as the first-class path, with native Windows as a best-effort fallback.

## Decision

WSL2 is the first-class Windows path.
Native Windows with PowerShell 7, WezTerm and psmux is a documented fallback, labelled best effort.

## Consequences

The repository and its configuration stay on the WSL ext4 filesystem, never under `/mnt/c`, for performance and file permissions.
Claude Code runs inside WSL for WSL projects, so the CLI, Neovim and tmux share one operating system.
A one-command fresh Windows install is not fully possible when WSL2 must be enabled, because that can need administrator rights and a reboot.
The bootstrap is therefore resumable and prints what to do after the reboot.
Nothing is claimed as WSL2-verified until it is run on a real WSL2 host, container runs are labelled as proxies.
