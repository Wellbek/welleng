# Installation

Well-Engineering installs from one Git repository.
Nothing here is verified on a real fresh machine.
The flow is tested in clean Ubuntu 24.04, Fedora and Arch containers, and the pieces were applied on the maintainer's Arch machine.

## Requirements

- `git` and Python 3.11 or newer.
- Linux or WSL2, see [Windows and WSL2](windows.md) for the Windows paths.
- Network access, for packages and the pinned release archives.
- `sudo` for the system package manager, unless you run as root.

## 1. Clone

```sh
git clone git@github.com:Wellbek/welleng.git
cd welleng
git config core.hooksPath .githooks   # only if you will commit to the repository
```

## 2. Install the tools

Preview first, nothing is changed:

```sh
bootstrap/install.sh --dry-run
```

Then install:

```sh
bootstrap/install.sh            # shows the plan, asks, then installs
bootstrap/install.sh --yes      # no question
bootstrap/install.sh --tiers mandatory    # only the mandatory tier
```

How it works:

- The package map `packages/packages.toml` lists each tool with its pacman, apt, dnf, brew, winget and scoop name.
- Tools are grouped in tiers: `mandatory`, `recommended` and `optional`.
  The default is `mandatory,recommended`.
- Packages come from your system package manager.
- A tool the package manager does not offer comes from a pinned release archive listed in `packages/releases.toml`.
  Pinned today: chezmoi, uv, lazygit, delta, starship, glow and yazi, for Linux x86_64 and aarch64.
  The aarch64 digests are pinned but those binaries were never run.
  The archive is checked against a SHA-256 digest before anything is extracted, and it is installed into `~/.local/bin`.
  A wrong digest, a non-https address or an unsafe archive path stops the install.
- Tools that are already present are skipped, so running it again is safe.

Make sure `~/.local/bin` is on your `PATH`.

## 3. Install the `welleng` command

```sh
uv tool install --editable tools
welleng doctor
```

The install is editable, so a `git pull` updates the command without reinstalling.
`welleng doctor` lists mandatory, recommended and optional tools and exits with 1 only when a mandatory tool is missing.

## 4. Deploy the configuration

The configuration is managed by chezmoi.
The source state is `home/`, selected by `.chezmoiroot`.

```sh
chezmoi init --apply --source <path to the repository>
```

You are asked once for a git author name and email, and chezmoi remembers them.
For an unattended run:

```sh
chezmoi init --apply --source <repo> \
  --promptString "Git author name=Ada" --promptString "Git author email=ada@example.org"
```

You can also run `bootstrap/install.sh --chezmoi` to do this as part of the install.
To deploy only part of it, give a target path, for example `chezmoi apply ~/.config/welleng`.

After a deploy from a clone, chezmoi has no default source directory, so export the clone's path for `welleng update`:

```sh
export WELLENG_REPO="$HOME/path/to/welleng"
```

The wire-in step (below) adds a managed block to your `~/.tmux.conf`, and a bare `chezmoi apply` would overwrite the file and drop that block.
After wiring in, keep using `welleng update --yes`, which applies only `~/.config/welleng` and `~/.config/welleng-nvim`, or rerun `scripts/wire-in.sh` after any full apply.

Important: `chezmoi apply` writes `~/.tmux.conf` and `~/.gitconfig`.
If you already have those files, read the diff with `chezmoi diff` first.
Everything else is deployed under `~/.config/welleng` and `~/.config/welleng-nvim`, which never overlap your existing files.

## Connect an existing setup

If you already use zsh, tmux and OpenSSH, connect them with one small managed block each:

```sh
scripts/wire-in.sh --dry-run    # show exactly what would change
scripts/wire-in.sh              # add the three blocks
scripts/wire-in.sh --undo       # remove them again
```

- Each file is backed up once, as `FILE.welleng-bak`.
- The blocks sit between `# >>> welleng >>>` and `# <<< welleng <<<` lines, and `--undo` removes only those.
- The script was run against copies and then the real files of the maintainer's machine, with before and after comparisons of the zsh environment, the tmux prefix and `ssh -G` output `[verified: Arch]`.
  An interactive zsh session was not proven identical, only a non-interactive one.

The zsh block sources `~/.config/welleng/shell/init.zsh`.
By default that only defines the credential helpers and the `glm` function, and nothing visible changes.
For the prompt, zoxide, fzf, lazygit and yazi integration, set `WELLENG_SHELL_EXTRAS=1` in `~/.zshrc` before the block, see [Configuration](configuration.md#shell).

## Credentials

Nothing is required.
Sign in to Claude Code with `claude` then `/login`, and to GitHub with `gh auth login`.
For the optional keys:

```sh
scripts/init-secrets.sh            # creates ~/.config/welleng/secrets.env with mode 600, never overwrites
scripts/init-secrets.sh --status   # shows which variables are set, never their values
```

Then edit `~/.config/welleng/secrets.env`.
See [security](../security.md#setting-up-credentials) for the model.

## Install the Claude Code plugin

See [Claude Code](claude-code.md#install-the-plugin).

## Update

```sh
welleng update          # dry run: fetch, list new commits, show drift
welleng update --yes    # pull fast-forward only, then apply
```

It refuses to run when the repository has uncommitted changes.
It applies only `~/.config/welleng` and `~/.config/welleng-nvim`, never your own files.
Neovim plugin versions are pinned in `lazy-lock.json`, so an update never changes them unless the repository's lock file changed.

## Uninstall

```sh
scripts/uninstall.sh            # dry run, lists what would be removed
scripts/uninstall.sh --yes
```

Removes the wired blocks (restoring your files), the files under `~/.config/welleng` and `~/.config/welleng-nvim`, welleng state and Neovim caches, and the uv tool and plugin when those commands exist.
Never removes `secrets.env`, files you created in those directories, `~/.ssh/config.d` fragments, system packages, or chezmoi itself.
The tests restore the wired files byte for byte in a container.
The `uv tool` and plugin removal steps ran only as dry-run text on the real machine.

## If something fails

See [troubleshooting](../troubleshooting.md).
