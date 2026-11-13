# Implementation checklist

This is the single source of truth for what exists and what has been verified.
A feature is marked `tested` only together with the platform it was tested on.
Anything that needs a device or an operating system that has not been reached is marked `implemented, verification pending` with a link to a manual procedure.

## Status values

| Status | Meaning |
|---|---|
| planned | Designed, nothing written |
| implemented | Written, not yet exercised |
| tested | Exercised, with the platform named in the "Tested on" column |

## Phase 0 - Baseline, safety and scaffolding

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Repository scaffolding: `.gitignore`, `.gitattributes`, `.editorconfig` | tested | Arch, ignore rules checked with `git check-ignore` | Line-ending rules are not yet exercised on Windows |
| Pre-commit secret scan, fallback path | tested | Arch, with synthetic fake secrets in a throwaway repository | Short pattern list, a safety net only |
| Pre-commit secret scan, `gitleaks` path | tested | Arch, gitleaks 8.30.1 in a throwaway repository: clean file passes, a fake token is blocked, the placeholder passes the allowlist | Only the Linux x64 build was run |
| `scripts/install-gitleaks.sh` pinned, checksum-verified install | tested | Arch: installs without root, and a corrupted archive is rejected with nothing installed | macOS and arm64 branches are written but not run |
| Hygiene script: tracked secrets files and em dashes | tested | Arch, CI (ubuntu-latest) | Checks text content only |
| CI: secret scan, hygiene, ShellCheck | tested | GitHub Actions, ubuntu-latest | No Windows job yet |
| CI: package id check on Ubuntu 24.04, Fedora and Arch containers | tested | GitHub Actions, three container jobs, all green. The Arch job first failed on a partial upgrade and was fixed with a full `pacman -Syu` | Checks that ids exist, not that the packages install or that their versions are new enough |
| Architecture decision records 0001 to 0012 | implemented | - | Claims carry evidence tags, see the ADR index |
| `docs/security.md` and `docs/platforms.md` | implemented | - | Design rules and upstream claims, not yet verified on a real setup |
| Project agent instructions and permission baseline | implemented | - | The deny rules have not been exercised yet |
| Credentials example, on-demand loader, `glm` function and `scripts/init-secrets.sh` | tested | Arch: file created with mode 600, never overwritten, parsed and not sourced, and `glm` run with a stub `claude` and a fake key | The real `glm` against the provider has not been run, it needs a new key |
| Plaintext credentials removed from the shell startup file and the editor config | tested | Arch, the count of key-like strings is zero in both files | Revoked keys can remain in editor local history and in Claude Code's own history file, outside this repository |
| Read-only snapshot of the existing configuration | tested | Arch: 122 files copied to a mode-700 directory outside any repository, three files compared identical | The snapshot predates the credential removal and still holds the revoked keys, delete it when it is no longer needed |
| Spike 1: chezmoi with `.chezmoiroot` and symlinked directories | tested | Arch, chezmoi v2.74.1, throwaway repository and fake home, see ADR 0002 | Windows symlinks, WSL detection and macOS are not verified |
| Spike 2: claudecode.nvim with Claude in an external tmux pane | tested | Arch, Neovim 0.12.1, plugin commit `bcf1f08`, throwaway home: server, lock file, loopback-only listener and cleanup, see ADR 0010 | A real `claude --ide` connection and diff accept or reject are not yet verified |
| Spike 3: hook input and output schemas, user-only messages | implemented | Read from the official hooks reference, see ADR 0012 | Documented behaviour only, no hook was run live, `TMUX_PANE` inheritance and `systemMessage` rendering are unverified |
| Spike 4: overlap with the `ecc` plugin | tested | Arch, by reading the plugin source version 2.2.3, see ADR 0011 | Findings come from reading code, not from running every hook |
| `ecc` override list and `scripts/apply-ecc-overrides.py` | tested | Arch: dry run, apply, idempotence and key preservation on a copy of the real settings, then applied to the real settings | The disabled GateGuard hook stopped gating in the running session without a restart `[verified: Arch]`. Whether a skill deny rule also stops a typed slash command is not yet verified, see ADR 0011 |
| Spike 5: Remote Control permission approval flow | implemented | Read from the official documentation, see `docs/security.md` | Approvals from a real phone are not verified, that stays a manual procedure |
| Spike 6: psmux viability on Windows | planned | - | Cannot run on Linux, needs a Windows host or CI runner, the four checks are listed in ADR 0003 |

## Phase 1 - Core shell and terminal environment

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| `packages/packages.toml` and `scripts/check-packages.py` | tested | Arch (pacman), Ubuntu 24.04 (apt) and Fedora latest (dnf), in containers: every listed id exists, two wrong dnf ids were found and removed | brew, winget and scoop ids are written from upstream names and not yet checked |
| chezmoi base: `.chezmoiroot`, prompts, per-OS ignore, tpm external, `.gitconfig`, `.tmux.conf` | tested | Arch, chezmoi v2.74.1, fake home: apply, rendered output, zero-line diff, `verify` exit 0 | zsh, starship, kitty, yazi, lazygit and the Neovim directory are not in the source state yet. Windows and WSL are not verified |
| `bootstrap/install.sh` and `install.ps1` with `--dry-run` | planned | - | |
| tmux configuration cleanup, keeping the existing prefix | tested | Arch, tmux 3.6a, isolated server: loads without errors, prefix `M-o` kept, `h` and `l` pane keys corrected, F1 falls back to the key list, kitty detected through `KITTY_WINDOW_ID` | The Neovim navigation bindings and the plugins loaded by tpm were not exercised |
| tmuxp default layout and `welleng up` | planned | - | |
| zsh cleanup, starship prompt, fd, delta, lazygit | planned | - | |
| `welleng keys` generated cheatsheet | planned | - | |
| `welleng doctor` skeleton | planned | - | |
| Linux container matrix in CI | planned | - | |
| Windows CI job for bootstrap and `doctor` | planned | - | |

## Phase 2 - Neovim

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| LazyVim base with a `lua/user/` layer | planned | - | |
| Language extras and Mason bootstrap | planned | - | |
| Markdown rendering in the editor | planned | - | |
| `NVIM_APPNAME` fallback to the previous configuration | planned | - | |

## Phase 3 - Git workflow

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| lazygit configuration with the delta pager | planned | - | |
| gitsigns and diffview keymaps | planned | - | No terminal tool reproduces every behaviour of a graphical diff editor |
| `welleng repos` multi-repository overview | planned | - | |

## Phase 4 - Claude Code integration and project harness

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Global instructions managed by chezmoi | planned | - | |
| `welleng` Claude Code plugin skeleton and settings merge | planned | - | |
| claudecode.nvim bridge and contextual prompt keys | planned | - | |
| `/harness` questionnaire skill with a plan-of-changes preview | planned | - | An empty Enter is not accepted by Claude Code, a skip token is used |
| `welleng harness check` validator | planned | - | |

## Phase 5 - Agent monitoring

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Hook and status line state writer | planned | - | |
| `welleng agents` dashboard | planned | - | Model and usage only for sessions that ran the hooks |
| tmux status segment | planned | - | |
| Contract test against the installed `claude` | planned | - | |

## Phase 6 - Remote machine registry

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| `welleng ssh` list, add, edit, remove | planned | - | |
| One-time `Include` migration of the SSH config | planned | - | |

## Phase 7 - Mobile access

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Remote Control helpers | planned | - | Not available for sessions routed to another provider |
| Port-diff security check | planned | - | |
| Manual phone verification procedure | planned | - | Needs a real device |

## Phase 8 - Effort recommendations

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Local scorer in the prompt hook, effort level only | planned | - | Accurate for the extremes, silent in the middle by design |
| Check that `effort.level` is the effective level in a real session | planned | - | Matters on models that fall back from `xhigh` to `high` |
| Status line delivery, cooldown, snooze and off switch | planned | - | |
| Recommendation log and report | planned | - | |

## Phase 9 - Windows, WSL2, hardening and documentation

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| PowerShell profile and WezTerm configuration | planned | - | |
| WSL2 guide | planned | - | Needs a WSL2 host to verify |
| Native Windows fallback notes | planned | - | Best effort |
| Uninstall and rollback | planned | - | |
| Troubleshooting guide | planned | - | |
