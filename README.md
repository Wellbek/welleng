# Well-Engineering

A reproducible, terminal-centric and AI-native development environment for Linux and WSL2, with native Windows as a best-effort fallback.
One Git repository installs the shell, tmux, Neovim, Git tooling and a Claude Code plugin, and keeps them working together.

**Status: early, Linux first.**
Tested on Arch Linux and in Ubuntu, Fedora and Arch containers.
Not yet verified: native Windows, WSL2, macOS, phone access and the editor bridge.
[CHECKLIST.md](CHECKLIST.md) is the source of truth for what exists and on which platform it was tested.

## Claude Code skills

The `welleng` plugin ships these skills.
Type them as `/welleng:<name>`, they cost no context until used.
The plugin has no hooks and needs nothing but Claude Code, so it can be installed without the rest of this repository, see [option 1](#option-1-the-skills).

| Skill | What it does |
|---|---|
| `/welleng:harness` | Sets up a project's Claude Code config through a short questionnaire, shows a diff, writes nothing until you approve |
| `/welleng:mode` | Rigorous mode for any non-trivial task: picks a playbook, delegates to subagents, proves the work on the real artifact |
| `/welleng:in-your-own-words` | Plays back your goal and the problem behind it before any work starts |
| `/welleng:sharpen` | Rewrites a prompt to be deeper, without doing the task |
| `/welleng:architect` | Settles types, signatures and module shape before code crosses a function boundary |
| `/welleng:tdd` | Fixes a bug test-first with a failing regression test |
| `/welleng:blast-radius` | Finds what a small change could break elsewhere and proves it safe by running code |
| `/welleng:interrogate` | Adversarial review where several models try to break a change, keeping only proven findings |
| `/welleng:arena` | Runs N parallel attempts at one task and merges the best parts |
| `/welleng:swarm` | Fans out parallel workers over slices of a job and returns one report |
| `/welleng:figure-it-out` | Designs an auditable playbook when no existing one fits |
| `/welleng:show-me-your-work` | Keeps a TSV decision trail for long or unattended work |
| `/welleng:how` | Explains how a subsystem works |
| `/welleng:why` | Explains why something is built that way, from the record |
| `/welleng:teach` | Explains a change or subsystem so you understand it, diagram by diagram |
| `/welleng:bro` | Restates the last message in plain words |
| `/welleng:ketchup` | Catches you up on what changed and lists decisions waiting on you |
| `/welleng:write` | Writes prose a tired engineer understands on the first read, removes AI tells |
| `/welleng:no-comments` | Strips comments before review and flags code that needs a reshape instead |
| `/welleng:correct` | Turns mistakes agents keep repeating into architecture, types, lints or tests |
| `/welleng:benchmark-checklist` | Vets a performance number before you report or act on it |
| `/welleng:verify-setup` | Generates a project skill that drives the app like a user and captures evidence |
| `/welleng:verify-maintain` | Keeps that verification skill honest after the app changes |
| `/welleng:reflect` | Turns what a long task taught into edits to existing skills, for approval |

This repository also has one project skill, `verify-welleng`, which drives a live Claude Code session to verify the plugin, its hooks and the CLI.
See the [workflow guide](docs/guides/workflow.md) for how the skills fit together.

## Install

Pick one of three options.
Each later option includes the earlier ones.

| Option | You get | Changes on your machine |
|---|---|---|
| [1. The skills](#option-1-the-skills) | Every `/welleng:` skill and the two subagents | One Claude Code plugin, no clone |
| [2. The skills and the hooks](#option-2-the-skills-and-the-hooks) | Also effort hints, the status line, the `welleng` command and its session dashboard | A clone, two plugins, one `uv` tool and optionally one settings entry |
| [3. The full development setup](#option-3-the-full-development-setup) | Also the shell, tmux, Neovim, Git tooling and remote access | Packages and the configuration under `$HOME`, with backups |

### Option 1: the skills

Add this repository as a plugin marketplace and install only the `welleng` plugin.
Nothing is cloned by hand, and nothing in your shell, tmux or editor changes.

```sh
claude plugin marketplace add Wellbek/welleng
claude plugin install welleng@welleng-local
```

Inside a running session the same works as `/plugin marketplace add Wellbek/welleng` and `/plugin install welleng@welleng-local`, then restart the session.
Update later with `claude plugin marketplace update welleng-local` and `claude plugin update welleng@welleng-local`.

- Every skill except `/welleng:harness` works on its own.
  `/welleng:harness` also needs the `welleng` command: `uv tool install "git+https://github.com/Wellbek/welleng#subdirectory=tools"`.
- `/welleng:show-me-your-work` runs a small helper with `python3`.
- The plugin has no hooks, so nothing runs unless you call a skill, see [ADR 0022](docs/adr/0022-skills-plugin-without-hooks.md).

Tested by installing from a local clone into an empty Claude Code config on WSL2 Ubuntu: 24 skills, 2 subagents and no hooks were loaded.
Installing from GitHub by `owner/repo` has not been run.

### Option 2: the skills and the hooks

The hooks add effort hints and per-session state, and the `welleng` command reads that state.
This needs `python3`, `git`, `uv` and a clone at a stable path, because the status line runs a script from it.
Your shell, tmux and editor stay untouched.

```sh
git clone https://github.com/Wellbek/welleng.git ~/.local/share/welleng
claude plugin marketplace add ~/.local/share/welleng
claude plugin install welleng@welleng-local
claude plugin install welleng-hooks@welleng-local
uv tool install --editable ~/.local/share/welleng/tools   # welleng agents, hints, harness and doctor
welleng doctor --claude                                     # both plugins should be listed
```

Then add the status line to your own `~/.claude/settings.json`, with your real home directory in place of `/home/you`:

```json
"statusLine": {"type": "command", "command": "python3 -I /home/you/.local/share/welleng/claude-plugin-hooks/hooks/statusline.py"}
```

- Effort hints read the effort level from the status line, so without it they stay silent, see [ADR 0021](docs/adr/0021-effort-level-from-the-status-line-state.md).
- If you already have a status line, call `statusline.py` from your own script instead of replacing it.
- Update with `git -C ~/.local/share/welleng pull`, then `claude plugin marketplace update welleng-local` and `claude plugin update` for both plugins.
- What each hook does is in [Claude Code](docs/guides/claude-code.md#install-the-plugins).

This option as a whole has not been run on a clean machine.

### Option 3: the full development setup

On Linux or inside WSL2.
Every step has a dry run, and the [installation guide](docs/guides/installation.md) explains each one.

```sh
git clone git@github.com:Wellbek/welleng.git
cd welleng
bootstrap/install.sh --dry-run        # see the plan, nothing changes
bootstrap/install.sh                  # install the tools
uv tool install --editable tools      # the welleng command
welleng doctor                        # what is installed and what is missing
chezmoi init --apply --source .       # deploy the configuration, read `chezmoi diff` first
scripts/wire-in.sh --dry-run          # optional: connect an existing zsh, tmux and SSH setup
claude plugin marketplace add .       # the Claude Code plugins, as in option 2
claude plugin install welleng@welleng-local
claude plugin install welleng-hooks@welleng-local
```

Then add the status line as in option 2, with the path of this clone.

Credentials are all optional, see [configuration](docs/guides/configuration.md#credentials).

## What you get

| Area | Contents |
|---|---|
| Install | chezmoi source state, one `packages/packages.toml` for pacman, apt and dnf, backups before any overwrite |
| Terminal | tmux owns the layout, kitty or WezTerm is only a skin, `welleng up` opens a project session |
| Shell | zsh or PowerShell 7 with starship, fzf, ripgrep, fd, bat, zoxide, yazi, delta and lazygit |
| Editor | Neovim with LazyVim and claudecode.nvim |
| Claude Code | The skills plugin above, a hooks plugin for effort hints and session state, and a tmux counter of sessions waiting for you |
| Remote | OpenSSH config as the machine registry, Claude Code Remote Control for the phone, optional Tailscale SSH into tmux, see [working from a phone](docs/guides/remote-and-mobile.md#working-from-a-phone) |

## The `welleng` command

| Command | Purpose |
|---|---|
| `welleng up [path]` | Open or attach to the project session |
| `welleng agents` | Overview of Claude sessions, `--count` feeds the tmux segment |
| `welleng repos [root]` | Branch, changes, ahead and behind for many repositories |
| `welleng ssh [add\|rm\|ls\|migrate]` | Manage machines from the SSH config |
| `welleng keys` | Generated keybinding cheatsheet |
| `welleng doctor` | Report mandatory, recommended and optional components |
| `welleng harness plan\|apply\|check` | Preview, write and validate a project's Claude Code config |
| `welleng hints [snooze\|off\|report]` | Control effort recommendations |
| `welleng rc` | Start Remote Control in tmux |
| `welleng update` | Pull the repository and apply the owned config |

## Principles

- **The multiplexer owns the layout.**
  The terminal emulator is replaceable.
- **Official interfaces only.**
  Claude Code is used through its CLI JSON output, hooks, status line, settings and plugins.
- **Native formats stay the source of truth.**
  SSH hosts, `CLAUDE.md` and `tmux.conf` are edited directly, there is no custom registry.
- **Four kinds of state stay apart.**
  Tracked configuration, local configuration, credentials and runtime state never share a location.
- **Honest verification.**
  A feature is claimed only on a platform where it was run.
- **Few custom parts.**
  Configure existing tools first, glue second, write from scratch last.

## Platforms

| Tier | Platform | Policy |
|---|---|---|
| 1 | Linux (Arch, Ubuntu, Fedora) | Full support |
| 1 | WSL2 | Full support, keep the repository on the ext4 filesystem, never under `/mnt/c` |
| 2 | Native Windows | Best effort |

Evidence tags used in the docs: `[verified: Arch]`, `[docs]`, `[search]`, `[spike]`, defined in [docs/adr/README.md](docs/adr/README.md).

## Security

- No credential lives in this repository, a shell startup file or an editor config.
- Credentials live in `~/.config/welleng/secrets.env` with mode 600.
- A pre-commit hook and CI both scan for secrets.
- Remote access is opt-in per session and never a standing internet-facing service.

Details are in [docs/security.md](docs/security.md).

## Documentation

| Document | Contents |
|---|---|
| [docs/guides/](docs/guides/README.md) | Installation, commands, configuration, Claude Code, workflow, terminal and editor, remote, Windows |
| [CHECKLIST.md](CHECKLIST.md) | Feature status and the platform each was tested on |
| [docs/adr/](docs/adr/README.md) | Architecture decision records |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Known problems and fixes |
| [docs/verification/](docs/verification/README.md) | Manual procedures for what needs a device or a live session |
| [docs/platforms.md](docs/platforms.md) | Tiers and verification rules |
| [CLAUDE.md](CLAUDE.md) | Rules for agents working in this repository |

## Contributing

- Enable the hooks once per clone with `git config core.hooksPath .githooks`.
- Run `scripts/check-hygiene.sh` before pushing and `scripts/regression.sh --strict` after significant changes.
- One concern per commit, with a Conventional Commits subject.
- Record significant decisions as a numbered file in `docs/adr/`.
- Markdown has one sentence per line, and the em dash is not used.

## Known limitations

- Native Windows, WSL2 and macOS have never been run.
- A literal "press Enter to skip" is impossible in Claude Code, so the questionnaire accepts `-`, `skip` and `s`.
- Remote Control cannot control sessions routed to another provider.
- Native Windows has no tmux, so it relies on psmux, which is untested here.
- Effort recommendations stay silent when the task complexity is unclear.

## License

No license has been chosen yet, so all rights are reserved.
