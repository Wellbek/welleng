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
| `bootstrap/install.sh` with `--dry-run`, `--yes`, `--tiers` | tested | Tested in container: Ubuntu 24.04, Fedora latest and Arch latest, 20 checks each, covering dry run, real install, mandatory tools on PATH, idempotence and a rejected bad checksum | Never run on the maintainer host, by design. macOS and Homebrew are not run. Applying the chezmoi config is a separate opt-in flag that was not exercised here |
| Pinned release archives: `packages/releases.toml`, `bootstrap/install_release.py`, `scripts/pin-releases.py` | tested | Tested in container (three distros) and 8 unit tests: wrong digest, non-https, path traversal, missing member, zip and tar | Linux x86_64 and aarch64 only, aarch64 digests are pinned but the binaries were not run |
| `bootstrap/install.ps1` | planned | - | |
| tmux configuration cleanup, keeping the existing prefix | tested | Arch, tmux 3.6a, isolated server: loads without errors, prefix `M-o` kept, `h` and `l` pane keys corrected, F1 falls back to the key list, kitty detected through `KITTY_WINDOW_ID` | The Neovim navigation bindings and the plugins loaded by tpm were not exercised |
| tmuxp default layout and `welleng up` | planned | - | |
| Opt-in shell integration `init.zsh`, starship and lazygit (delta) config | tested | Tested in container (Arch): parses, guarded with no tools present, fd alias on Debian naming, a user's own starship config wins, lazygit config is chained | Not run in a real interactive session. The maintainer's own `~/.zshrc` is not modified, see ADR 0015 |
| `welleng keys` generated cheatsheet | tested | Arch: 3 unit tests, and the real `dot_tmux.conf` parses | Reads tmux bindings only, Neovim and lazygit keys are not included yet. It is a filtered list, not an interactive fuzzy finder |
| Regression harness: `scripts/regression.sh` with hygiene, secret scan, ShellCheck, security policy, Python and end-to-end stages | tested | Arch host plus an Arch container: `--strict` run passes all 7 stages, and planted violations (a filled secret, an API-key-shaped token, a pipe into a shell) are caught | The CI `regression` and `bootstrap` jobs ran green on GitHub Actions. Only Arch is covered, Ubuntu and Fedora end-to-end runs are not written |
| End-to-end home test `tests/e2e/home.sh` | tested | Arch container, chezmoi from pacman, throwaway HOME: apply, verify, idempotence, credential handling, tmux load, `glm` with a stub `claude` and a hostile secrets file | Externals (tpm) are excluded because they need the network |
| Static security checks `tests/security/static.sh` | tested | Arch host | Policy checks on tracked files, not a replacement for a dependency or CVE scan |
| `welleng doctor` skeleton | tested | Arch: 4 pytest tests pass, and a live run reports the real machine and exits 1 on missing mandatory tools | Looks executables up on `PATH` only, it does not check versions, and Windows is not run. Not in CI yet |
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
| `welleng repos` multi-repository overview | tested | Arch: 4 unit tests against real throwaway git repositories (branch, staged, unstaged, untracked, ahead and behind) and a live run | Scans two levels deep, no remote fetch, so ahead and behind reflect the last fetch |

## Phase 4 - Claude Code integration and project harness

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Global instructions managed by chezmoi | planned | - | |
| `welleng` Claude Code plugin skeleton | tested | Arch: `claude plugin validate` passes on Claude Code 2.1.325, and the SessionStart hook is exercised by piping events (suggests once in a bare git repo, silent when configured, on resume, outside a repo or on garbage input) | The hook was not run inside a live Claude Code session, so how its `additionalContext` is presented is unverified. The plugin has not been installed from a marketplace |
| claudecode.nvim bridge and contextual prompt keys | planned | - | |
| `/harness` questionnaire skill with a plan-of-changes preview | implemented, verification pending | - | The skill text validates, but no live session has run the questionnaire. Manual check: install the plugin, run `/harness` in a throwaway repository and confirm nothing is written before approval. It needs `welleng` on PATH, install with `uv tool install` from `tools/` |
| `welleng harness plan`, `apply` and `check` | tested | Arch: 9 unit tests: plan writes nothing, apply is idempotent, existing JSON and Markdown are preserved, managed blocks replace only their own text, credentials and literal MCP env values are refused, invalid JSON is never overwritten, `apply` needs `--yes` | Hook commands are checked for existence and the executable bit only, not run |

## Phase 5 - Agent monitoring

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Hook and status line state writer | planned | - | |
| `welleng agents` dashboard, base layer | tested | Arch: 8 unit tests with synthetic data, and a live run against `claude agents --json` on Claude Code 2.1.325 `[verified: Arch]` | Shows state, project, name, kind and age only. Model, effort, context and cost need the hook state writer, and there is no interactive jump or terminate yet |
| `welleng agents --count` for a tmux status segment | tested | Arch: prints the waiting count, or `?` when `claude` fails | The tmux config does not call it yet, wiring it in changes the deployed tmux file and is still to do |
| Contract test against the installed `claude` | tested | Arch, Claude Code 2.1.325: the real `claude agents --json` output parses and every state maps to a known value | Covers `agents --json` only, not the hook or status line payloads. Skipped automatically where `claude` is not installed, including CI |

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
