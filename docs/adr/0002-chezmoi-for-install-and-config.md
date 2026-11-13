# 0002 - chezmoi for installation and configuration

Status: Accepted
Date: 2026-11-13

## Context

The environment must install reproducibly on Linux, WSL2 and Windows.
Configuration differs per operating system and per machine, so templating is required.
Applying must be idempotent and must show a diff before changing anything.

## Options considered

- GNU Stow: symlinks only, no Windows support, no templating.
- Dotbot: runs on Windows, but has no templating and only basic idempotence.
- Nix with home-manager: excellent reproducibility, but heavy and WSL-only on Windows.
- A custom installer: would re-implement most of chezmoi.
- chezmoi: Windows support, per-OS templates, `chezmoi diff` and `chezmoi apply`, and a one-line fresh-machine bootstrap.

## Decision

Use chezmoi as the installation and configuration manager.
The source state lives under `home/`, selected with `.chezmoiroot`.

## Consequences

chezmoi copies files by default, so editing a live config does not edit the repository.
Directories that are edited live, such as the Neovim config, use `symlink_` entries so the target points into the repository.
`[spike]` Confirm symlinked directories work with `.chezmoiroot`, and with Windows symlink permissions (Developer Mode).
If symlinks are unavailable on Windows, fall back to copy mode and a documented `chezmoi re-add` workflow.
