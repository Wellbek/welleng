# Command reference

All commands are subcommands of `welleng`.
Running `welleng` alone prints the usage and exits with an error, a subcommand is always required.
Every command that can change something is a dry run by default or asks for `--yes`.

## `welleng doctor`

Reports components by tier: mandatory, recommended and optional.

```sh
welleng doctor [--packages PATH] [--claude]
```

- Each line is `ok` or `missing`, with the executable name.
- It checks that an executable is on `PATH`, not its version.
- Exit code 1 means a mandatory tool is missing, otherwise 0.
- `--claude` adds the installed Claude Code plugins, from `claude plugin list --json` and `claude plugin details`.
  Each enabled plugin shows its version and the always-on token estimate that `claude plugin details` prints.
  That estimate also counts skills marked `disable-model-invocation`, which do not reach the model's context, so it is an upper bound.
  An `advice` line appears when sessions load an older `welleng` plugin than the repository holds.
  This section never changes the exit code, and it takes a few seconds per plugin.

## `welleng up`

Opens or attaches to the project tmux session.

```sh
welleng up [PATH] [--no-attach] [--socket NAME]
```

- The session is named after the project directory, with unsafe characters replaced by `-`.
- It has four windows: `edit` (Neovim), `git` (lazygit), `agents` (`watch -t -n 5 welleng agents`) and `shell`.
- A missing tool degrades that window to a plain shell.
- If the session exists, it is reused, nothing is recreated.
- `--no-attach` creates the session and prints its name, `--socket` selects a tmux socket and exists for tests.
- The `edit` window starts `nvim` with `NVIM_APPNAME` taken from your environment, defaulting to `nvim`.
  To open the project's Neovim configuration, export `NVIM_APPNAME=welleng-nvim` first, see [terminal and editor](terminal-and-editor.md#neovim).
- Attaching was not exercised in tests, only `--no-attach` `[verified: Arch]`.

## `welleng repos`

One-screen overview of the git repositories under a directory.

```sh
welleng repos [ROOT]
```

Columns: branch, staged (`S`), unstaged (`U`), untracked (`?`), ahead, behind and the last commit.
It scans two levels deep and does not fetch, so ahead and behind reflect your last fetch.

## `welleng agents`

Central view of Claude Code sessions, from the official `claude agents --json`.

```sh
welleng agents [--count]
```

- Rows are sorted with sessions waiting for you first.
- Columns: `state`, `project`, `name`, `kind`, `age`.
  When the hook state writer has data, also `model`, `effort`, `ctx`, `cost` and `sub`, see [Claude Code](claude-code.md#session-state-and-the-dashboard).
- `--count` prints only the number waiting for you, or `?` when `claude agents` fails.
  The tmux status line uses this.

## `welleng keys`

Searchable cheatsheet of your tmux key bindings.

```sh
welleng keys [PATTERN] [--tmux-conf PATH]
```

Reads `~/.tmux.conf`, prints bindings grouped by key table, and keeps only lines containing `PATTERN`.
Neovim and lazygit keys are not included, see [terminal and editor](terminal-and-editor.md) for those.

## `welleng ssh`

Machine registry on top of the OpenSSH config, see [remote machines](remote-and-mobile.md#the-machine-registry).

```sh
welleng ssh ls
welleng ssh add NAME HOSTNAME [--user U] [--port P] [--identity PATH] [--jump HOST] [--description TEXT]
welleng ssh rm NAME
welleng ssh migrate [--yes] [--undo] [--config PATH]
```

All accept `--dir DIR` before the action to use a fragment directory other than `~/.ssh/config.d`.

## `welleng update`

```sh
welleng update [--repo PATH] [--yes]
```

See [installation](installation.md#update).
The repository is `--repo`, or `$WELLENG_REPO`, or the one behind chezmoi's source directory.

## `welleng harness`

Plans, applies and checks a project's Claude Code configuration, see [Claude Code](claude-code.md#the-harness-skill).

```sh
welleng harness plan SPEC.json [--project DIR]
welleng harness apply SPEC.json [--project DIR] --yes
welleng harness check [DIR]
```

`plan` writes nothing.
`apply` refuses without `--yes`.
`check` exits 1 when it finds problems.

## `welleng hints`

Controls the effort recommendations, see [Claude Code](claude-code.md#effort-hints).

```sh
welleng hints snooze [--hours N]    # default 4 hours
welleng hints off
welleng hints on
welleng hints report
```

## `welleng rc`

Starts Remote Control, or checks the listening ports around it, see [remote machines](remote-and-mobile.md#a-remote-control).

```sh
welleng rc [--name NAME]
welleng rc --ports snapshot
welleng rc --ports diff
```

`welleng rc` must run inside tmux.
The port check needs Linux with `ss`.
