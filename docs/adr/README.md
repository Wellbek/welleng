# Architecture decision records

Each significant decision is recorded as one numbered file in this directory.
Copy `0000-template.md` to add a new one.
Records are never deleted, a decision that changes gets a new record that supersedes the old one.

## Evidence tags

Claims in these records carry one of these tags so the strength of the evidence is always visible.

- `[verified: Arch]` checked directly on an Arch Linux machine, and only there.
- `[docs]` checked against official documentation of the tool in question.
- `[search]` seen in web search results only, not independently confirmed.
- `[spike]` plausible but unverified, a Phase 0 spike must confirm it before the project depends on it.

## Index

| Record | Title | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-chezmoi-for-install-and-config.md) | chezmoi for installation and configuration | Accepted |
| [0003](0003-tmux-as-multiplexer-terminal-as-skin.md) | tmux as the multiplexer, the terminal emulator as a skin | Accepted |
| [0004](0004-wsl2-first-native-windows-best-effort.md) | WSL2 first, native Windows best effort | Accepted |
| [0005](0005-official-claude-code-interfaces-only.md) | Official Claude Code interfaces only | Accepted |
| [0006](0006-lazyvim-base-with-nvchad-fallback.md) | LazyVim base with an NvChad fallback | Accepted |
| [0007](0007-openssh-config-as-machine-registry.md) | OpenSSH config as the machine registry | Accepted |
| [0008](0008-recommend-only-model-hints.md) | Recommend-only model hints | Superseded by 0013 |
| [0009](0009-secrets-outside-the-repository.md) | Secrets live outside the repository | Accepted |
| [0010](0010-claude-in-a-tmux-pane-with-an-editor-bridge.md) | Claude in a tmux pane with an editor bridge | Accepted |
| [0011](0011-avoid-overlap-with-the-ecc-plugin.md) | Avoid overlap with the ecc plugin | Accepted |
| [0012](0012-hook-event-data-contract.md) | Hook event data contract | Accepted |
| [0013](0013-effort-only-hints.md) | Effort-only hints | Accepted |
| [0014](0014-pinned-release-archives-for-tools-without-packages.md) | Pinned release archives for tools without a package | Accepted |
| [0015](0015-opt-in-shell-integration.md) | Opt-in shell integration that never edits existing files | Accepted |
| [0016](0016-behaviour-preserving-wire-in.md) | Wiring into an existing setup must preserve behaviour | Accepted |
