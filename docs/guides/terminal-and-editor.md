# Terminal, shell and editor

Everything here is opt-in or namespaced, see [configuration](configuration.md).
tmux is the multiplexer and the terminal emulator is only a skin, see [ADR 0003](../adr/0003-tmux-as-multiplexer-terminal-as-skin.md).

## A typical session

```sh
export NVIM_APPNAME=welleng-nvim    # once, in your shell startup
welleng up ~/code/myproject          # four windows: edit, git, agents, shell
```

Run it again and it reattaches to the same session.
`welleng repos ~/code` gives a status table of all repositories under a directory.

## tmux

The prefix is `M-o` (Alt and o).
`welleng keys` prints the live list from your `~/.tmux.conf`, and `F1` opens it in a popup.

| Keys | Action |
|---|---|
| `M-o` then `r` | Reload `~/.tmux.conf` |
| `M-o` then `*` | Split side by side |
| `M-o` then `"` | Split top and bottom |
| `M-o` then `h` `j` `k` `l` | Select the pane left, down, up, right |
| `C-h` `C-j` `C-k` `C-l` | Move between panes and Neovim splits without the prefix, through vim-tmux-navigator |
| `M-1` to `M-9`, `M-0` | Select window 1 to 10 |
| `M-u` | Zoom or unzoom the pane |
| `F1` | Key list popup |

Other settings: mouse on, windows and panes numbered from 1, vi keys in copy mode, the status bar on top, window names follow the directory.
tmux plugins come from tpm: dracula for the theme, vim-tmux-navigator and tmux-resurrect.
Install them once with the tpm default, prefix then `I` (capital i).
The kitty terminfo is used when tmux starts from kitty, with true colour either way.

## Neovim

LazyVim with a small user layer.
It runs as `NVIM_APPNAME=welleng-nvim`, so your existing `~/.config/nvim` is not touched, see [ADR 0017](../adr/0017-neovim-as-a-separate-app-name.md).

```sh
NVIM_APPNAME=welleng-nvim nvim
```

On first start, plugins install at the versions in `lazy-lock.json`.
This needs network access and a C compiler for Treesitter.
Language servers install through Mason the first time you open a file of that type.
Enabled language extras: Python, JSON, Markdown, TOML, YAML.
The colour scheme is tokyonight.
Personal options (relative line numbers, scroll offset 6) are in `lua/user/options.lua`, and keys in `lua/user/keymaps.lua`.

Project-local Neovim config works through `exrc`, and Neovim asks before trusting a file.

Keys added on top of LazyVim (`<leader>` is space):

| Key | Action |
|---|---|
| `<leader>wk` | Open the `welleng keys` cheatsheet |
| `<leader>a` ... | Claude Code, see [Claude Code](claude-code.md#editor-bridge) |
| `<leader>gd` | Diffview: working tree |
| `<leader>gm` | Diffview: this branch against `origin/HEAD` |
| `<leader>gH` | Diffview: history of the current file |
| `<leader>gq` | Close Diffview |
| `<leader>gT` | Toggle line blame |

LazyVim's own git keys stay: gitsigns hunk keys under `<leader>gh` and `[h` `]h` to move between hunks.
Press `<leader>` and wait to see every key through which-key.

What is tested: plugins install at the pinned versions, LazyVim loads without errors, the keys exist, and Diffview opens on a real repository, all in an Arch container.
Not exercised: interactive use, completion, Treesitter by eye, Mason installs and Markdown rendering, see the manual checks in [CHECKLIST.md](../../CHECKLIST.md).

## Git

- `~/.gitconfig` comes from `home/dot_gitconfig.tmpl` with your name and email.
- lazygit uses the delta pager through the shell opt-in, and the `git` window of `welleng up` starts it.
- Review a branch in Neovim with `<leader>gm`, and one file's history with `<leader>gH`.
- The delta pager was not looked at in a real lazygit session.

## kitty

Add one line to the end of `~/.config/kitty/kitty.conf`:

```
include ~/.config/welleng/kitty/welleng.conf
```

The file was loaded by the real kitty 0.46.2 on Arch, and a deliberately broken file was rejected.
Put your overrides after the include.

## yazi

With the shell opt-in, `y` opens yazi and changes your shell's directory to where you quit.
The config is `~/.config/welleng/yazi/yazi.toml`: three-column layout, natural sorting with directories first, hidden files and symlink targets shown.
It is used only when you have no `~/.config/yazi` and no `YAZI_CONFIG_HOME`.

## Shell tools

With `WELLENG_SHELL_EXTRAS=1`: starship prompt, zoxide (`z`), fzf key bindings with `fd` as the file source.
The package map also installs ripgrep, bat, jq, glow and delta.
`fd` and `bat` are aliased where Debian calls them `fdfind` and `batcat`.
