# Troubleshooting

Start with `welleng doctor`, which lists missing tools by tier, and `scripts/regression.sh --quick`, which checks the repository itself.

## The `welleng` command is not found

It is installed with `uv tool install --editable tools` from the repository, which puts it in `~/.local/bin`.
Make sure that directory is on `PATH`.
The editable install follows the repository, so a `git pull` updates it without reinstalling.

## The tmux status line shows no "waiting" count

- The segment appears only when at least one Claude Code session is waiting for you.
- tmux reads `~/.tmux.conf` at server start, so reload it with the prefix key and `r`, or start a new server.
- Run `welleng agents --count` in a shell.
  `?` means `claude agents --json` failed, and `0` means nothing is waiting.

## Effort hints never appear

- Run `welleng hints report`.
  If "prompts that carried no effort level" keeps growing, the hook input does not carry the effort level in your sessions, and the hint stays silent by design, see ADR 0016.
- A hint needs a gap of two levels or more between the task and the current level, so it never fires at `medium` for ordinary work.
- `welleng hints on` clears a snooze or an off switch.

## The plugin is not active

- `claude plugin list` should show `welleng@welleng-local` as enabled.
- Plugins load at session start, so start a new session after installing.
- `claude plugin validate claude-plugin` checks the manifest and the hooks file.

## Undoing the connection to your shell, tmux and SSH config

`scripts/wire-in.sh --undo` removes the three blocks and leaves your own lines alone.
The first change to each file is also saved next to it as `FILE.welleng-bak`.
`scripts/uninstall.sh` shows everything it would remove, and `scripts/uninstall.sh --yes` removes it.
It never removes `secrets.env`.

## The installer cannot download a tool

`bootstrap/install_release.py` refuses any archive whose SHA-256 differs from `packages/releases.toml`, and prints both digests.
A mismatch means the release changed or the download was corrupted.
Do not edit the digest by hand, run `scripts/pin-releases.py NAME`, review the diff, and commit it.
On a minimal container, install `ca-certificates` first, Python cannot verify https without them.

## Credentials

- Credentials live only in `~/.config/welleng/secrets.env` with mode 600, and `scripts/init-secrets.sh` creates it.
- `glm` says the key is not set: add `ZAI_API_KEY=` to that file.
- A key that was ever printed or committed must be revoked, deleting the line is not enough.

## Neovim

- Use `NVIM_APPNAME=welleng-nvim nvim` to run this configuration next to your own.
- Plugin versions are pinned by `lazy-lock.json`, restore them with `:Lazy restore`.
- Treesitter parsers need a C compiler and the `tree-sitter` command line tool.

## Windows and WSL2

Keep the repository on the WSL ext4 filesystem, `chmod 600` does not work under `/mnt/c`.
Nothing here has been verified on Windows or WSL2, see `docs/verification/`.

## `claude --ide` finds no Neovim

The bridge plugin must be loaded when Neovim starts, because it creates the lock file that `claude --ide` looks for.
Run `NVIM_APPNAME=welleng-nvim nvim`, then `:echo exists(':ClaudeCodeSend')`, which must print 2.
If it prints 0, the plugin spec lost its `lazy = false` setting, because a spec with `keys` is lazy by default.
Several Neovim instances in one project make the auto-connect ambiguous, so use `/ide` to choose.

## `init.zsh` prints "defining function based on alias"

zsh refuses to parse a function definition `name() { ... }` when an alias with that name already exists.
Current versions define `y` with the `function` keyword, so run `welleng update --yes` to get the fixed file.

## `welleng update` says to give the repository

chezmoi has no default source directory when you deployed from a clone with `--source`.
Export `WELLENG_REPO` with the clone's path, or pass `--repo`.

