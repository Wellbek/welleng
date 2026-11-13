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
| Pre-commit secret scan, `gitleaks` path | implemented | - | `gitleaks` is not installed on the Arch machine, the hook branch itself has not run locally |
| Hygiene script: tracked secrets files and em dashes | tested | Arch, CI (ubuntu-latest) | Checks text content only |
| CI: secret scan, hygiene, ShellCheck | tested | GitHub Actions, ubuntu-latest | No Windows or container-matrix job yet |
| Architecture decision records 0001 to 0011 | implemented | - | 0011 details wait for the plugin overlap spike |
| `docs/security.md` and `docs/platforms.md` | implemented | - | Design rules and upstream claims, not yet verified on a real setup |
| Project agent instructions and permission baseline | implemented | - | The deny rules have not been exercised yet |
| Move credentials out of shell startup files into `secrets.env` | planned | - | Needs the maintainer to rotate credentials first |
| Read-only snapshot of the existing configuration | planned | - | The snapshot contains secrets until they are rotated, so it waits for that step |
| Spike 1: chezmoi with `.chezmoiroot` and symlinked directories | planned | - | Also needed on Windows |
| Spike 2: claudecode.nvim with Claude in an external tmux pane | planned | - | |
| Spike 3: hook input and output schemas, user-only messages | planned | - | |
| Spike 4: overlap with the `ecc` plugin | planned | - | |
| Spike 5: Remote Control permission approval flow | planned | - | Security claims are documented upstream, see `docs/security.md` |
| Spike 6: psmux viability on Windows | planned | - | |

## Phase 1 - Core shell and terminal environment

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| chezmoi source state and `packages/packages.toml` | planned | - | |
| `bootstrap/install.sh` and `install.ps1` with `--dry-run` | planned | - | |
| tmux configuration cleanup, keeping the existing prefix | planned | - | |
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

## Phase 8 - Model recommendations

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Local scorer in the prompt hook | planned | - | Accurate for the extremes, silent in the middle by design |
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
