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
| `welleng update`: fetch, show commits and drift, then apply only `~/.config/welleng` and `~/.config/welleng-nvim` | tested | Arch: 5 unit tests with real git repositories and a stub chezmoi (dry run by default, pull only with `--yes`, dirty tree refused, apply scope limited), and a live dry run that correctly refused a dirty tree | Not run with a real chezmoi apply through this command |
| `bootstrap/install.ps1` | implemented, verification pending | Parses with PowerShell's own parser in a container and in CI, never run | Same row as in Phase 9, see `docs/verification/windows.md` |
| tmux configuration cleanup, keeping the existing prefix | tested | Arch, tmux 3.6a, isolated server: loads without errors, prefix `M-o` kept, `h` and `l` pane keys corrected, F1 falls back to the key list, kitty detected through `KITTY_WINDOW_ID` | The Neovim navigation bindings and the plugins loaded by tpm were not exercised |
| `welleng up`: four-window project session (edit, git, agents, shell) | tested | Arch: unit tests against a real tmux on an isolated socket (windows created, second call reuses the session, panes start in the project directory), and a live run | Implemented directly with tmux commands, not with tmuxp. Missing tools degrade to a plain shell. Attaching (`attach-session` or `switch-client`) was not exercised, only `--no-attach` |
| Opt-in shell integration `init.zsh`, starship and lazygit (delta) config | tested | Tested in container (Arch): parses, guarded with no tools present, fd alias on Debian naming, a user's own starship config wins, lazygit config is chained | Not run in a real interactive session. The maintainer's own `~/.zshrc` is not modified, see ADR 0015 |
| `welleng keys` generated cheatsheet | tested | Arch: 3 unit tests, and the real `dot_tmux.conf` parses | Reads tmux bindings only, Neovim and lazygit keys are not included yet. It is a filtered list, not an interactive fuzzy finder |
| Regression harness: `scripts/regression.sh` with hygiene, secret scan, ShellCheck, security policy, Python and end-to-end stages | tested | Arch host plus an Arch container: `--strict` run passes all 10 stages, and planted violations (a filled secret, an API-key-shaped token, a pipe into a shell) are caught | The CI `regression` and `bootstrap` jobs ran green on GitHub Actions. Only Arch is covered, Ubuntu and Fedora end-to-end runs are not written |
| End-to-end home test `tests/e2e/home.sh` | tested | Arch container, chezmoi from pacman, throwaway HOME: apply, verify, idempotence, credential handling, tmux load, `glm` with a stub `claude` and a hostile secrets file | Externals (tpm) are excluded because they need the network |
| Static security checks `tests/security/static.sh` | tested | Arch host | Policy checks on tracked files, not a replacement for a dependency or CVE scan |
| `welleng doctor` skeleton | tested | Arch: 4 pytest tests pass, and a live run reports the real machine and exits 1 on missing mandatory tools | Looks executables up on `PATH` only, it does not check versions, and Windows is not run. Not in CI yet |
| Linux container matrix: `tests/e2e/distro.sh` on Ubuntu 24.04 and Fedora | tested | Tested in container: bootstrap, then the home end-to-end test (28 checks) and the Python tests (95 passed, 2 skipped for kitty and yazi) on each distro. Running it exposed a test that assumed chezmoi is not in `/usr/bin`, now fixed | The GitHub Actions `distro` job has not run yet. Arch is covered by the existing regression job |
| Windows CI job for bootstrap and `doctor` | implemented, verification pending | Written in `.github/workflows/ci.yml`, not yet run on GitHub | `continue-on-error`, because native Windows is best effort (ADR 0004). The `-DryRun` and `doctor` steps are guesses until the first run |

## Phase 2 - Neovim

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| LazyVim base with a `lua/user/` layer | tested | Tested in container (Arch, Neovim from pacman, network to GitHub): plugins install, LazyVim loads, startup prints no errors, the user keymap layer is active, no plugin failed to load | Not used interactively. The container test does not exercise the UI, completion or Treesitter highlighting by eye |
| Language extras and Mason bootstrap | implemented, verification pending | Extras for Python, JSON, Markdown, TOML and YAML are enabled and load in container | Mason installs language servers on first use of a file type, that step was not run. Manual check: open a `.py` file and confirm the server attaches |
| Markdown rendering in the editor | implemented, verification pending | The LazyVim markdown extra loads in container | Rendering was not looked at. Manual check: open a `.md` file and confirm headings and code blocks render |
| `NVIM_APPNAME` separation from the previous configuration | tested | Tested in container: the configuration uses only `welleng-nvim` directories, and the `uninstall.sh` test leaves unrelated files alone | The new configuration is not the default `nvim`, switching it is the maintainer's decision, see ADR 0017. Not run next to the real `~/.config/nvim` |

## Phase 3 - Git workflow

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| lazygit configuration with the delta pager | tested | Tested in container (Arch): see the opt-in shell integration row, `LG_CONFIG_FILE` is chained after the user's own file | The delta pager itself was not looked at in a real lazygit session |
| gitsigns and diffview keymaps | tested | Tested in container (Arch, Neovim from pacman): the keys exist, and `:DiffviewOpen` opens a view on a real repository with an uncommitted change | Not used interactively. LazyVim supplies the gitsigns hunk keys. No terminal tool reproduces every behaviour of a graphical diff editor |
| `welleng repos` multi-repository overview | tested | Arch: 4 unit tests against real throwaway git repositories (branch, staged, unstaged, untracked, ahead and behind) and a live run | Scans two levels deep, no remote fetch, so ahead and behind reflect the last fetch |

## Phase 4 - Claude Code integration and project harness

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Global instructions managed by chezmoi | implemented | Tested in container: the file is deployed under `~/.config/welleng/claude/` and no `~/.claude` is created. A unit test checks the rules (no em dash, import line) | Opt-in through one `@` import line in the user's own `~/.claude/CLAUDE.md`, a live Claude Code session has not loaded it |
| `welleng` Claude Code plugin skeleton | tested | Arch: `claude plugin validate` passes on Claude Code 2.1.325, and the SessionStart hook is exercised by piping events (suggests once in a bare git repo, silent when configured, on resume, outside a repo or on garbage input) | The hook was not run inside a live Claude Code session, so how its `additionalContext` is presented is unverified. The plugin has not been installed from a marketplace |
| claudecode.nvim bridge and contextual prompt keys | implemented, verification pending | Tested in container: the keys exist in normal and visual mode, and the pane detection logic is unit tested (own pane excluded, `claude` and version-number commands matched). A `claude` pane appears as `claude` in tmux on Arch `[verified: Arch]` | The send, type and focus flow with a live `claude --ide` session was not run, see ADR 0019 and `docs/verification/interactive.md` |
| `/harness` questionnaire skill with a plan-of-changes preview | implemented, verification pending | - | The skill text validates, but no live session has run the questionnaire. Manual check: install the plugin, run `/harness` in a throwaway repository and confirm nothing is written before approval. It needs `welleng` on PATH, install with `uv tool install` from `tools/` |
| `welleng harness plan`, `apply` and `check` | tested | Arch: 9 unit tests: plan writes nothing, apply is idempotent, existing JSON and Markdown are preserved, managed blocks replace only their own text, credentials and literal MCP env values are refused, invalid JSON is never overwritten, `apply` needs `--yes` | Hook commands are checked for existence and the executable bit only, not run |

## Cross-cutting: connecting to an existing setup

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Wire-in `scripts/wire-in.sh` and `tests/e2e/wire-in.sh` | tested | Arch container with copies of the maintainer's real zshrc, tmux and ssh config, and with synthetic files: 23 checks each, covering dry run, idempotence, `ssh -G` identical for every host, tmux prefix and errors unchanged, zsh status, errors, aliases, exports and key bindings unchanged, exact restore by `--undo`. Then applied on the real machine with the same before and after comparison `[verified: Arch]` | The comparison uses a non-interactive `zsh -i -c`, an interactive session is not proven identical. Not run on other distributions or macOS |
| Installed on the maintainer machine: `welleng` through `uv tool install --editable`, chezmoi from a pinned release, `~/.config/welleng` deployed, the three blocks wired, the plugin installed from the local marketplace | tested | Arch, real machine: `welleng` runs from PATH, `welleng agents --count` works, `claude plugin list` shows the plugin enabled | The tmux segment is not active in already-running tmux servers until their config is reloaded |
| Plugin hooks in a live session | tested | Arch, headless `claude -p` on 2.1.325: `SessionStart` ran and produced the JSON, `UserPromptSubmit` ran with exit 0 | Interactive sessions are not exercised. The hook input carried no `effort` field in headless mode, so hints stay silent there, see ADR 0016 |

## Phase 5 - Agent monitoring

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Hook and status line state writer | implemented, verification pending | Arch: 12 subprocess and unit tests: nothing printed, mode 600 files, prompt text and transcript path never written, subagent ids tracked, hostile session ids ignored, stale files pruned, `SessionEnd` cleanup | No live Claude Code session has produced these files, see ADR 0018. The status line is an opt-in that the plugin does not set |
| `welleng agents` dashboard, base layer | tested | Arch: 8 unit tests with synthetic data, and a live run against `claude agents --json` on Claude Code 2.1.325 `[verified: Arch]` | Shows state, project, name, kind and age from the CLI, plus model, effort, context, cost and subagents from the state writer when it has data (tested with synthetic state files). There is no interactive jump or terminate yet |
| `welleng agents --count` for a tmux status segment | tested | Arch: prints the waiting count or `?`, and the segment is wired through `tmux-agents.conf`, a loaded config shows it in `status-right` | Only visible in a tmux server that reloaded the config, and the interactive look was not checked |
| Contract test against the installed `claude` | tested | Arch, Claude Code 2.1.325: the real `claude agents --json` output parses and every state maps to a known value | Covers `agents --json` only, not the hook or status line payloads. Skipped automatically where `claude` is not installed, including CI |

## Phase 6 - Remote machine registry

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| `welleng ssh` list, add, remove | tested | Arch: 11 unit tests in temporary directories with fake hosts: round trip, mode 600 fragments, hand-written entries listed but never removed, config injection through newlines, spaces, quotes and comments rejected, duplicates rejected | No `edit` command yet, remove and add again. No interactive picker. Not run against the real `~/.ssh` and not tested through an actual `ssh` connection |
| One-time `Include` migration: `welleng ssh migrate` | tested | Arch: 6 unit tests in temporary directories: dry run by default, line placed first, backup kept, mode 600, idempotent, existing Include recognised, exact `--undo`, symlinked config. `ssh -G` resolves a hand-written host identically before and after and finds a managed host | Not run against the real `~/.ssh`. The real `ssh` check substitutes an absolute path, because a relative Include resolves against the real `~/.ssh` |

## Phase 7 - Mobile access

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Remote Control helpers: `welleng rc` | implemented, verification pending | Arch: unit tests for the tmux command, which refuses `bypassPermissions`, and the outside-tmux error | `claude remote-control` was not started, so no phone ever connected. Procedure: `docs/verification/phone.md`. Not available for sessions routed to another provider |
| Port-diff security check: `welleng rc --ports snapshot` and `diff` | tested | Arch: unit tests for parsing and the exposed or loopback split, and a live snapshot and diff on the real machine reported `ok` | Linux with `ss` only. It has not yet been run around a real Remote Control start |
| Manual phone verification procedure | implemented, verification pending | Written, see `docs/verification/phone.md` | Needs a real device |

## Phase 8 - Effort recommendations

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| Local scorer in the prompt hook, effort level only | implemented, verification pending | Arch: 10 unit and subprocess tests of the scorer and hook, `claude plugin validate` passes. The hook ran silently in a live headless session, which carried no effort level | Accuracy on real prompts is unmeasured, the keyword lists are a first guess to tune from the log. The "first prompt after a completed turn" condition of ADR 0013 is not implemented, the cooldown stands in for it. Manual check: run a session at `/effort high`, send `rename foo to bar`, and confirm one user-only hint appears |
| Check that `effort.level` is the effective level in a real session | planned | - | Matters on models that fall back from `xhigh` to `high` |
| Hint delivery by `systemMessage`, cooldown, snooze and off switch | tested | Arch: cooldown, snooze, off, `ultrathink`, missing effort level and low confidence all stay silent in tests, and the hook prints a single JSON object | No status line segment yet, `systemMessage` rendering in a live session is unverified `[spike]` |
| Recommendation log and `welleng hints report` | tested | Arch: the log holds estimate and levels only, a test asserts the prompt text is never written | Acceptance detection from later effort changes is not implemented |

## Phase 9 - Windows, WSL2, hardening and documentation

| Feature | Status | Tested on | Known limitations |
|---|---|---|---|
| PowerShell profile and WezTerm configuration | implemented, verification pending | The profile parses and runs with stub tools in a PowerShell 7 container on Linux (guards, `y` changes directory, lazygit config chained). The WezTerm file passes a Lua syntax check | Never run on Windows, and WezTerm itself was not started. Both are opt-in and Windows-only through `.chezmoiignore` |
| WSL2 guide and verification procedure | implemented, verification pending | Written, see `docs/verification/wsl2.md` | Needs a WSL2 host to verify |
| `bootstrap/install.ps1` and the native Windows procedure | implemented, verification pending | Parses with PowerShell's own parser in a container, and in CI. Never run, see `docs/verification/windows.md` | Best effort, needs a Windows host |
| Uninstall and rollback: `scripts/uninstall.sh` and `wire-in.sh --undo` | tested | Arch container: dry run changes nothing, `--yes` removes deployed files, keeps `secrets.env` and the user's own files, and restores the user's zshrc, tmux and ssh files byte for byte | The `uv tool` and plugin removal steps ran only as dry-run text on the real machine |
| Troubleshooting guide | implemented | Written from the problems met while building this, `docs/troubleshooting.md` | Entries were not tried by a second person |
