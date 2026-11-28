# Configuration

This page lists everything the project deploys or reads, where it lives, how to change it and how to switch it off.
The guiding rule is [ADR 0015](../adr/0015-opt-in-shell-integration.md): nothing replaces a file you already have.
Almost everything lives under `~/.config/welleng` and is activated by one line you add yourself.

## Where things live

| Path | Contents | Managed by |
|---|---|---|
| `~/.config/welleng/` | Shell helpers, starship, lazygit, kitty, yazi, tmux segment, Claude instructions, `ecc` overrides, `secrets.env` | chezmoi, except `secrets.env` |
| `~/.config/welleng-nvim/` | The Neovim configuration, used as `NVIM_APPNAME=welleng-nvim` | chezmoi |
| `~/.tmux.conf`, `~/.gitconfig` | tmux and git configuration | chezmoi, these two do replace a file of that name |
| `~/.local/state/welleng/` | Hint switches and log, port snapshot, `sessions/` state files | welleng commands and hooks |
| `~/.ssh/config.d/` | One fragment per host added with `welleng ssh add` | `welleng ssh` |
| `~/.local/bin/` | Tools from pinned release archives | `bootstrap/install.sh` |

State paths follow `$XDG_STATE_HOME` when it is set.
Nothing is ever read from or written to `~/.claude/` by welleng code, see [ADR 0005](../adr/0005-official-claude-code-interfaces-only.md).
Hand edits to files that chezmoi deploys are overwritten by the next `chezmoi apply`, so change them in the repository.
Per-machine overrides belong in your own files, which the opt-ins below load first or last as noted.

## Shell

Opt in with one line at the very end of `~/.zshrc`, or let `scripts/wire-in.sh` add it:

```sh
[[ -r ~/.config/welleng/shell/init.zsh ]] && source ~/.config/welleng/shell/init.zsh
```

By default it only:

- defines `glm`, see [Claude Code](claude-code.md#glm),
- aliases `fd` and `bat` where Debian and Ubuntu name them `fdfind` and `batcat`.

Set this in `~/.zshrc` before the line to turn on the visible integrations:

```sh
export WELLENG_SHELL_EXTRAS=1
```

Each integration is skipped when you already set it up yourself.

| Integration | Behaviour | You keep control by |
|---|---|---|
| starship | Prompt, using `~/.config/welleng/starship.toml` | having your own `~/.config/starship.toml` or `STARSHIP_CONFIG` |
| zoxide | `z` and `zi` | already running `zoxide init` |
| fzf | Key bindings, and `fd` as the default file source | already having the fzf widgets or `FZF_DEFAULT_COMMAND` |
| lazygit | Adds the delta pager config after your own `~/.config/lazygit/config.yml` | setting `LG_CONFIG_FILE` yourself |
| yazi | Uses `~/.config/welleng/yazi` and defines `y`, which changes directory on exit | having a `~/.config/yazi` directory or `YAZI_CONFIG_HOME`, or your own `y` |

Tested in containers and on Arch with stub tools.
It was not run in a real interactive session, see [CHECKLIST.md](../../CHECKLIST.md).

## Credentials

`~/.config/welleng/secrets.env` has mode 600 and lives outside every repository.
Format: `NAME=value`, one per line, no `export`, no spaces around `=`.

| Variable | Used by | Needed |
|---|---|---|
| `ZAI_API_KEY` | the `glm` function | only if you use `glm` |
| `ANTHROPIC_API_KEY` | editor providers that use API keys | no, and never export it globally because it can override your subscription login |
| `OPENAI_API_KEY` | optional editor providers | no |

The file is parsed one name at a time on demand and is never sourced or exported.
Set the location with `WELLENG_SECRETS_FILE`.
Nothing in this project prints, copies or commits a value.
A repository check fails on any tracked secrets file.

## tmux

`~/.tmux.conf` is deployed from `home/dot_tmux.conf`.
It keeps the prefix `M-o` (Alt and o).
Keys are listed in [terminal and editor](terminal-and-editor.md#tmux).

The "waiting" counter in the status line is a separate file, `~/.config/welleng/tmux-agents.conf`, loaded with `source-file -q`.
It calls `~/.config/welleng/tmux-waiting.sh`, a script, because a closing parenthesis inside a tmux `#()` command ends the command early.
It shows `waiting:N` when N Claude sessions wait for you, and nothing otherwise.
Add the line yourself if you do not use the full `dot_tmux.conf`, and deploy both files:

```
source-file -q ~/.config/welleng/tmux-agents.conf
```

## Neovim

The configuration is LazyVim with a small user layer, run under its own name so your existing `~/.config/nvim` is untouched.
Details and keys are in [terminal and editor](terminal-and-editor.md#neovim).
Make it your default in your shell with `export NVIM_APPNAME=welleng-nvim`, or use an alias.

Plugin versions are pinned in `lazy-lock.json`.
To change them deliberately, run `scripts/nvim-container.sh --update-lock` and commit the result.

## kitty and WezTerm

- kitty: add `include ~/.config/welleng/kitty/welleng.conf` to `~/.config/kitty/kitty.conf`.
  It sets shell integration, scrollback, copy on select, makes Alt reach tmux on macOS and allows programs to write the clipboard.
  Put your own settings after the include to override them.
  A commented `shell tmux new -A -s welleng` line starts every window in the welleng session.
- WezTerm, Windows only: deployed to `~/.config/wezterm/wezterm.lua` by chezmoi on Windows and ignored elsewhere.
  Set `WELLENG_WSL_DISTRO` to start in a WSL2 tmux session, otherwise it starts PowerShell 7.

## Git

`~/.gitconfig` is rendered from a template with your name and email.
Change them with `chezmoi edit-config` and `chezmoi apply`,.
lazygit gets the delta pager through the shell opt-in above.

## PowerShell

Windows only, opt in from your PowerShell 7 profile, see [Windows and WSL2](windows.md).

## Claude Code

| File | Purpose | Activation |
|---|---|---|
| `claude-plugin/` | The `welleng` plugin: `/welleng:harness`, a session start suggestion, effort hints and the state writer | `claude plugin install`, see [Claude Code](claude-code.md#install-the-plugin) |
| `~/.config/welleng/claude/CLAUDE.md` | Global agent instructions | one `@~/.config/welleng/claude/CLAUDE.md` line in your own `~/.claude/CLAUDE.md` |
| `~/.config/welleng/ecc-overrides.json` | Features of the `ecc` plugin that conflict with this project | `python3 scripts/apply-ecc-overrides.py`, preview with `--dry-run` |
| `claude-plugin/hooks/statusline.py` | Status line that records model, effort, context and cost | add it to your own settings, see [Claude Code](claude-code.md#session-state-and-the-dashboard) |

## Environment variables

| Variable | Effect |
|---|---|
| `WELLENG_SHELL_EXTRAS=1` | Turns on the visible shell integrations |
| `WELLENG_SECRETS_FILE` | Alternative credentials file |
| `WELLENG_REPO` | Repository used by `welleng update` |
| `WELLENG_WSL_DISTRO` | WSL2 distribution for the WezTerm configuration |
| `NVIM_APPNAME` | Selects the Neovim configuration, `welleng-nvim` for this project's |
| `XDG_STATE_HOME`, `XDG_CONFIG_HOME` | Standard locations, honoured where noted |
| `vim.g.welleng_claude_pane` | Neovim variable that pins the tmux pane for contextual prompts |
