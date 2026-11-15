# Well-Engineering

A reproducible, terminal-centric and AI-native development environment for Linux, WSL2 and, as a best-effort fallback, native Windows.

It installs from a single Git repository, keeps the editor, multiplexer, Git tooling and Claude Code working together, and adds only a small amount of custom code on top of mature tools.

## Status

**Pre-implementation.**
The repository currently holds the foundations: repository hygiene, secret scanning, CI, decision records, the security and platform policies, the agent instructions for working on the project, the credentials example with its on-demand loader, and the list of `ecc` plugin features that are disabled to avoid conflicts.
No part of the environment itself is installed or implemented yet.

[CHECKLIST.md](CHECKLIST.md) is the single source of truth for what exists and what has been verified, per platform.
Every feature described below is **planned** unless the checklist says otherwise.

## Contents

- [Design principles](#design-principles)
- [Architecture](#architecture)
- [Components](#components)
- [The `welleng` command line](#the-welleng-command-line)
- [Repository layout](#repository-layout)
- [Platform support](#platform-support)
- [Security](#security)
- [Getting started](#getting-started)
- [Roadmap](#roadmap)
- [Documentation](#documentation)
- [Conventions](#conventions)
- [Known limitations](#known-limitations)
- [License](#license)

## Design principles

- **The multiplexer owns the layout.**
  tmux carries layout, keybindings and persistence, so the terminal emulator is a replaceable skin.
- **Official interfaces only.**
  Claude Code is integrated through its CLI JSON output, hooks, status line, settings and plugins, and never by parsing its internal files.
- **Native formats stay the source of truth.**
  SSH hosts live in `ssh_config`, project instructions in `CLAUDE.md` and `.claude/settings.json`, and tmux behaviour in `tmux.conf`.
  Custom tools read and edit those formats instead of inventing a registry.
- **Four kinds of state stay separate.**
  Tracked configuration, local machine configuration, credentials and runtime state never share a location, see [Security](#security).
- **Honest verification.**
  Anything that has not been run on a platform is not claimed for that platform, and anything verified only on one machine is labelled with that machine.
- **Few custom parts.**
  Existing tools are configured first, glued second and written from scratch last.

Evidence tags used across the documentation:

| Tag | Meaning |
|---|---|
| `[verified: Arch]` | Checked directly on an Arch Linux machine, and only there |
| `[docs]` | Checked against official documentation |
| `[search]` | Seen in web search results only |
| `[spike]` | Plausible but unverified, a spike must confirm it first |

## Architecture

```
  Terminal emulator (skin only: kitty or WezTerm)
            |
  tmux session "welleng:<project>"   (layout from a tmuxp file)
            |
   +--------+----------+-------------+-----------+
   | edit   | git      | agents      | shell     |
   | nvim   | lazygit  | welleng     | zsh or    |
   | claude |          | agents      | PowerShell|
   +---+----+----------+------+------+-----------+
       |                      |
  claudecode.nvim        claude agents --json
  (selection, @file,     plus hook and status line
   diff review)          state files
       |
  Claude Code CLI  <---- hooks and status line ---->  welleng state
       |
  Remote Control (outbound only)  ->  phone
```

| Flow | Mechanism |
|---|---|
| Editor selection to Claude | claudecode.nvim local WebSocket bridge `[spike]` |
| Claude events to the dashboard | Hooks write one small JSON file per session into the runtime state directory `[docs]` |
| Model, effort and usage to the dashboard | The status line script reads the payload and writes the same file `[docs]` |
| Session list and liveness | `claude agents --json` |
| Jump from the dashboard to a session | The tmux pane id captured by the `SessionStart` hook, otherwise `claude attach` |
| Effort hints | The prompt hook writes an estimate, the status line shows it |
| Phone control | Claude Code Remote Control `[docs]` |

Remote machines need nothing from this project.
`welleng ssh` only reads and writes the local SSH configuration.

## Components

### Installation and configuration

**Tool:** chezmoi, see [ADR 0002](docs/adr/0002-chezmoi-for-install-and-config.md).

- A bootstrap script installs `git`, `chezmoi` and `uv`, then runs `chezmoi init --apply`.
- The source state lives under `home/` and is templated per operating system, WSL or native, and package manager.
- Package installs are keyed on a hash of a single `packages/packages.toml` that maps one logical name to the package id on each platform.
- Existing files are diffed first, and a conflicting file is backed up before it is replaced.
- `--dry-run` prints the complete plan and changes nothing.
- Directories that are edited live use symlinks into the repository, with a copy-mode fallback where symlinks are unavailable.
- Uninstall restores files from the newest backup and removes only the symlinks it created.

### Terminal and multiplexer

**Tools:** tmux, kitty on Linux, WezTerm on Windows, tmuxp for layouts, see [ADR 0003](docs/adr/0003-tmux-as-multiplexer-terminal-as-skin.md).

- The default layout has four windows: `edit` (Neovim, Claude and a shell), `git` (lazygit), `agents` (the dashboard) and `shell`.
- `welleng up` computes a session name from the project root and loads the layout, and running it again attaches instead of creating a duplicate.
- A per-project `.welleng/layout.yaml` can override the layout.
- Native Windows uses psmux as a best-effort replacement for tmux `[spike]`.

### Shell and command-line tools

- zsh on Linux and WSL, PowerShell 7 on native Windows, with the same starship prompt in both.
- Core tools: fzf, ripgrep, fd, bat, zoxide, yazi, glow, jq, delta and lazygit.
- `welleng keys` generates the keybinding cheatsheet from tmux, Neovim and the shell, so nothing is maintained by hand.
- The cheatsheet is available as a tmux popup and as a Neovim mapping.

### Editor

**Tool:** Neovim with LazyVim, see [ADR 0006](docs/adr/0006-lazyvim-base-with-nvchad-fallback.md).

- Language servers, formatters and linters come from LazyVim extras and Mason.
- Planned coverage: Python, C and C++, Rust, Go, Java, JavaScript and TypeScript, HTML and CSS, SQL, Bash, Lua, YAML, JSON and Markdown.
- Personal keymaps and theme live in a `lua/user/` layer so they survive upgrades.
- The previous configuration stays runnable through `NVIM_APPNAME` until the new one reaches parity.
- Project-local overrides use Neovim's `exrc` and its trust prompt, so a repository cannot run code silently.

### Git workflow

| Tool | Role |
|---|---|
| lazygit | Overview, commit, branch, history and rebase, with hunk and line staging |
| diffview.nvim | Side-by-side review where the working-tree side is an editable buffer `[spike]` |
| gitsigns.nvim | Always-on hunk signs, stage, reset, preview and blame |
| delta | Pager that gives green and red backgrounds in lazygit and in `git diff` |
| `welleng repos` | Multi-repository overview, see below |

No terminal tool reproduces every behaviour of a graphical diff editor, such as inline word-level highlighting and a "revert block" gutter.
This combination is the closest available, and the gap is documented instead of hidden.

### Claude Code integration

**Decision:** Claude runs in a persistent tmux pane and the editor only provides a bridge, see [ADR 0010](docs/adr/0010-claude-in-a-tmux-pane-with-an-editor-bridge.md).

- claudecode.nvim provides selection sharing, `@file` references and native diff review with accept and reject mappings.
- A small set of contextual prompt keys covers explain, review, fix, write tests and refactor, each a thin wrapper around a canned prompt.
- Subscription login is used only by the Claude Code CLI.
  API-key providers sit in a separate editor module behind a single provider selector and read their keys from the secrets file.
- A global `CLAUDE.md` is managed by chezmoi.

### Project harness

A Claude Code plugin ships a `/harness` skill that sets up a project's agent configuration through a short questionnaire.

- It asks one question at a time, with a short explanation and examples, and accepts a skip token.
  Claude Code ignores an empty prompt, so a literal "press Enter to skip" is not possible, and `-`, `skip` and `s` are accepted instead.
- Free-form answers are rewritten into concise, imperative instructions using a rubric.
- Before writing anything it shows a plan of changes with the exact files and a diff for each modification, and nothing is written until you approve.
- Generated text lives in delimited blocks, so updates replace only managed blocks and never touch the rest of a file.
- Each answer goes to the most deterministic mechanism that fits:

| Intent | Mechanism |
|---|---|
| Always run the formatter after edits | A `PostToolUse` hook |
| Never touch secrets files | `permissions.deny` plus a `PreToolUse` hook |
| Run the tests before finishing | A `Stop` hook, or a documented command for slow suites |
| Coding conventions | A `CLAUDE.md` block or a path-scoped rule file |
| Ask before pushing or deleting | `permissions.ask` entries |
| Query a database | An `.mcp.json` entry with credentials referenced by environment variable |
| A personal preference | `settings.local.json` or the global configuration, never the team files |

- `welleng harness check` validates the result: JSON validity, no empty files, no secrets, and executable hook commands.

### Agent monitoring

- `claude agents --json` is the base layer `[verified: Arch]`, observed on Claude Code 2.1.323.
- Hooks and the status line enrich it with the model, effort, context usage, cost and plan usage windows `[docs]`.
- `welleng agents` shows one row per session with project, state, model, effort, context, cost and age, and sorts sessions waiting for you to the top.
- Enter jumps to the session's tmux pane, or attaches to a background session.
  Terminating a session always asks for confirmation.
- A tmux status segment shows how many sessions are waiting, in every tmux session.
- Subagent counts come only from what hooks expose, and child-process trees are not shown because no official interface exists.
- The adapter validates fields defensively, and a contract test runs against the real installed `claude` to catch schema drift.

### Remote machine registry

**Decision:** OpenSSH config is the registry, see [ADR 0007](docs/adr/0007-openssh-config-as-machine-registry.md).

- `welleng ssh` lists hosts with tags and description and previews the effective settings from `ssh -G`.
- `welleng ssh add`, `edit` and `rm` manage fragments under `~/.ssh/config.d/`, and hand-edited entries are never rewritten.
- Hosts, addresses and usernames are local and never tracked in this repository.

### Mobile access

- **Default:** Claude Code Remote Control `[docs]`.
  The session keeps running on your machine and the phone is a window into it.
  It makes outbound connections only, and it requires a subscription login.
- **Opt-in:** it is off by default and enabled per session.
- **Optional:** Tailscale with SSH and tmux, for attaching to real panes from a phone SSH client.
- **Rejected:** web terminals exposed through port forwarding or tunnels.
- Remote Control does not work for sessions routed through another provider by overriding the API base URL `[docs]`.

Details and the threat summary are in [docs/security.md](docs/security.md).

### Effort recommendations

**Decision:** recommend an effort level only, never a model, and never switch automatically, see [ADR 0013](docs/adr/0013-effort-only-hints.md).

- A local scorer in the prompt hook combines intent verbs, scope hints, session context, attachments and the previous turn.
- It recommends `low`, `medium` or `high`, and leaves `xhigh` and `max` as your own deliberate choice.
- A hint appears only when the recommendation differs from the current effort level by at least two steps, with enough confidence, right after a completed turn, outside any cooldown or snooze.
- It stays silent when the prompt contains `ultrathink` or the current model has no effort setting.
- It is shown as a dim status line segment such as `hint: /effort low`, and `hints snooze` and `hints off` silence it.
- A model-based classification stage exists but is off by default, because it spends subscription usage.
- Every recommendation is logged locally, and `hints report` shows how often hints fired and were accepted.
- Expected accuracy is good for the obvious extremes and silent in the middle, by design.

### Secrets and security

Covered in [Security](#security) and [docs/security.md](docs/security.md).

- `scripts/init-secrets.sh` creates the credentials file from an example with mode 600.
- A zsh helper reads one named secret on demand by parsing the file, never sourcing it, and passes it only to the process that needs it.
- The `glm` function is built on that helper, so no key lives in a shell startup file.

### Continuous integration

Every push and pull request runs:

- a full-history secret scan with a pinned, checksum-verified `gitleaks`
- the repository hygiene script
- Bash syntax checks and ShellCheck on all shell scripts
- the `regression` job: security policy checks, the Python tests and the end-to-end home test in an Arch container
- the `bootstrap` job: a real install in clean Ubuntu, Fedora and Arch containers
- a check that every package id in `packages/packages.toml` exists in the repositories of Ubuntu 24.04, Fedora and Arch

## The `welleng` command line

A small Python package run through `uv`, identical on Linux and Windows.
`welleng doctor`, `keys`, `repos` and `harness` exist, every other command below is **planned**.

| Command | Purpose |
|---|---|
| `welleng` or `welleng up [path]` | Open or attach to the project session, or pick a project when outside one |
| `welleng repos [root]` | Multi-repository overview with branch, staged, unstaged and untracked counts, ahead and behind, and last commit |
| `welleng agents` | Central view of Claude sessions, with `--count` for the tmux segment |
| `welleng ssh [add\|edit\|rm\|ls]` | Pick and manage machines from the SSH config |
| `welleng keys` | Generated, searchable keybinding cheatsheet |
| `welleng doctor` | Report mandatory, recommended and optional components, failing only on missing mandatory ones |
| `welleng harness check` | Validate generated project configuration |
| `welleng hints [snooze\|off\|report]` | Control and review effort recommendations |
| `welleng rc` | Start Remote Control server mode in a dedicated tmux window |
| `welleng update` | Pull, show the drift and the diff, then apply |

## Repository layout

Existing today:

```
.githooks/pre-commit          secret scan and hygiene gate
.github/workflows/ci.yml      CI
.claude/settings.json         project permission baseline
scripts/check-hygiene.sh      hygiene checks shared by the hook and CI
scripts/scan-secrets-fallback.sh
scripts/install-gitleaks.sh   pinned, checksum-verified gitleaks install without root
scripts/check-packages.py     check package ids against pacman, apt and dnf
scripts/init-secrets.sh       create the credentials file with mode 600 and show what is set
scripts/regression.sh         full regression run, see below
scripts/chezmoi-container.sh  run a command in a clean Arch container
tests/                        security policy checks and the end-to-end home test
scripts/apply-ecc-overrides.py  merge the ecc override list into Claude Code settings
packages/packages.toml        logical package name to package id per platform
packages/releases.toml        pinned release archives with SHA-256 for tools without a package
bootstrap/                    install.sh, plan.py and install_release.py
claude-plugin/                the welleng Claude Code plugin: /harness skill and a SessionStart suggestion
scripts/distro-container.sh   run a command in a clean Ubuntu, Fedora or Arch container
tools/                        the welleng Python package (`doctor`, `keys`, `repos`, `harness`) with pytest tests
.chezmoiroot                  points chezmoi at home/
home/                         chezmoi source state: tmux and git config, tpm, welleng config
CLAUDE.md                     agent instructions for this repository
CHECKLIST.md                  verification status per feature and platform
docs/adr/                     architecture decision records
docs/security.md              secrets and remote access model
docs/platforms.md             platform tiers and verification policy
```

Planned, not created yet:

```
bootstrap/                    install.ps1 and the uninstall scripts
home/                         the rest of the chezmoi source state: zsh, starship, kitty, yazi, lazygit, Neovim
```

## Platform support

| Tier | Platform | Policy |
|---|---|---|
| 1 | Linux (Arch, Ubuntu, Fedora) | Full support |
| 1 | WSL2 | Full support, the first-class Windows path |
| 2 | Native Windows | Best effort fallback |

- Keep this repository and your configuration on the WSL ext4 filesystem, never under `/mnt/c`.
- Enabling WSL2 can need administrator rights and a reboot, so a fresh Windows install is resumable and multi-step.
- A claim is only made for a platform where it was run: "Tested on Arch", "Tested in container", "CI-verified bootstrap", and never "WSL2-verified" without a WSL2 run.

The full capability matrix and verification rules are in [docs/platforms.md](docs/platforms.md).

## Security

- No credential is stored in this repository, in a shell startup file or in an editor config.
- Credentials live in `~/.config/welleng/secrets.env` with mode 600, outside any repository.
- A pre-commit hook and CI both scan for secrets.
- Remote access is opt-in per session and never a standing internet-facing service.

| State class | Location | Tracked |
|---|---|---|
| Tracked configuration | this repository | yes |
| Local machine configuration | `~/.config/welleng/local.toml`, `~/.ssh/config.d/` | no |
| Credentials | `~/.config/welleng/secrets.env`, `~/.ssh`, the OS keychain | never |
| Runtime state | `$XDG_STATE_HOME/welleng`, on Windows `%LOCALAPPDATA%\welleng` | no |

See [docs/security.md](docs/security.md) for the Remote Control model and what to do if a secret is committed.

## Getting started

The installer does not exist yet.
What works today is contributing to the foundations.

```sh
git clone git@github.com:Wellbek/welleng.git
cd welleng
git config core.hooksPath .githooks   # enable the pre-commit gate
scripts/check-hygiene.sh              # run the hygiene checks
```

Install `gitleaks` for full secret-scan coverage in the hook with `scripts/install-gitleaks.sh`.
It installs a pinned, checksum-verified release into `~/.local/bin` without root, and CI uses the same script.
Without `gitleaks`, the hook falls back to a shorter built-in scan and prints a warning.

Set up credentials, which are all optional:

```sh
scripts/init-secrets.sh            # creates ~/.config/welleng/secrets.env with mode 600
scripts/init-secrets.sh --status   # shows which variables are set, never their values
```

Nothing is required.
Claude Code signs in with `claude` then `/login`, and GitHub with `gh auth login`.
Optional variables are `ZAI_API_KEY` for the `glm` shell function, `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` for editor providers that use API keys.
The full instructions are in [docs/security.md](docs/security.md#setting-up-credentials).

If you use the `ecc` Claude Code plugin, run `python3 scripts/apply-ecc-overrides.py --dry-run` to preview which of its features are disabled because they conflict with this project, then run it without `--dry-run` to apply them.
The reasons are in [ADR 0011](docs/adr/0011-avoid-overlap-with-the-ecc-plugin.md).

The planned fresh-machine flow, none of which exists yet:

1. Install `git` and `curl`, or use `winget` on Windows.
2. Run the bootstrap script, which installs `chezmoi` and `uv` and then applies the configuration.
3. Run `welleng doctor` and follow its install hints.
4. Sign in to Claude Code and GitHub, and add your own SSH hosts and secrets.

## Roadmap

| Phase | Theme |
|---|---|
| 0 | Baseline, safety, scaffolding and spikes |
| 1 | Core shell and terminal environment, bootstrap, CI matrix |
| 2 | Neovim with LazyVim |
| 3 | Git workflow and the multi-repository overview |
| 4 | Claude Code integration and the project harness |
| 5 | Agent monitoring |
| 6 | Remote machine registry |
| 7 | Mobile access |
| 8 | Effort recommendations |
| 9 | Windows and WSL2 hardening, uninstall, troubleshooting, final documentation |

Each phase ends with tests on the stated platforms, updated documentation and an updated [CHECKLIST.md](CHECKLIST.md).

## Documentation

| Document | Contents |
|---|---|
| [CHECKLIST.md](CHECKLIST.md) | Feature status and the platform each was tested on |
| [docs/adr/](docs/adr/README.md) | Architecture decision records and the evidence tags |
| [docs/security.md](docs/security.md) | Credentials, scanning and remote access |
| [docs/platforms.md](docs/platforms.md) | Tiers, capability matrix and verification rules |
| [CLAUDE.md](CLAUDE.md) | Rules for agents working in this repository |

## Conventions

- Commits are small, one concern each, with Conventional Commits subjects such as `feat:`, `fix:`, `docs:`, `chore:` and `ci:`.
- Significant decisions get a numbered record in `docs/adr/`, and a changed decision gets a new record that supersedes the old one.
- Markdown is written with one full sentence per line.
- The em dash character is not used, and `scripts/check-hygiene.sh` enforces it.
- Shell scripts use `bash` with `set -euo pipefail`, are ShellCheck-clean and are idempotent.
- Custom tooling is Python 3.11 or newer, run through `uv`.

## Known limitations

- Nothing in the environment itself is implemented yet.
- A literal "press Enter to skip" is impossible in Claude Code's input, because an empty prompt is ignored.
- Remote Control cannot control sessions routed to another provider.
- A terminal cannot match a graphical diff editor exactly.
- Native Windows has no tmux, so it relies on a third-party alternative, psmux, that has not been run for this project and is best effort.
- Effort recommendations cannot reliably classify task complexity from a prompt alone, so they stay silent when unsure.

## License

No license has been chosen yet, so all rights are reserved until one is added.
