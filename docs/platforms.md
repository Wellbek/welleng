# Platforms

Well-Engineering targets Linux, WSL2 and native Windows.
This page states what is intended for each, and is strict about what has actually been verified.

Nothing below is implemented yet.
The tables describe the target, and the verification table at the end describes how each claim will be earned.

## Support tiers

| Tier | Platform | Policy |
|---|---|---|
| 1 | Linux (Arch, Ubuntu, Fedora) | Full support |
| 1 | WSL2 | Full support, the first-class Windows path, see ADR 0004 |
| 2 | Native Windows | Best effort fallback |

## Target capability matrix

| Capability | Linux | WSL2 | Windows native |
|---|---|---|---|
| Bootstrap | `install.sh` | `install.sh` inside the distro, `install.ps1` outside | `install.ps1` |
| Package source | pacman, apt, dnf, brew | the distro's package manager | winget, scoop as fallback |
| Terminal emulator | kitty or WezTerm | WezTerm on the Windows host | WezTerm |
| Multiplexer | tmux | tmux | psmux, best effort |
| Shell | zsh | zsh | PowerShell 7 |
| Core CLI tools (fzf, ripgrep, fd, bat, zoxide, delta, lazygit, jq) | Full | Full | Full through winget |
| Neovim with LazyVim and language servers | Full | Full | Partial, Treesitter needs a C compiler |
| claudecode.nvim bridge | Full | Full | `[spike]` |
| Claude Code CLI | Full | Full | `[spike]` |
| `welleng up` layout | Full | Full | Partial, through psmux |
| Agent dashboard | Full | Full | Partial, no tmux pane jump |
| Remote Control | Full | Full | Full |
| SSH registry | Full | Full | Full, with the Windows OpenSSH client |
| Secrets file permission | `chmod 600` | `chmod 600` on ext4 only | NTFS ACL through `icacls` |
| Symlinked configs | Yes | Yes, keep configs on ext4 | Needs Developer Mode, otherwise copy mode with a warning |

## WSL2 guidance

- Keep this repository and your configs on the WSL ext4 filesystem, never under `/mnt/c`.
- Run Claude Code inside WSL for projects that live in WSL.
- Install WezTerm on the Windows side and launch `wsl.exe -d <distro> --cd ~ -- tmux new -A -s welleng`.
- Enabling WSL2 can need administrator rights and a reboot, so a fresh Windows install is a resumable multi-step process, not one command.

## What can and cannot be verified

| Target | How it will be tested | Claim allowed |
|---|---|---|
| Arch Linux | Directly, on the maintainer's machine | "Tested on Arch", and only Arch |
| Ubuntu and Fedora | Scripted fresh installs in containers | "Tested in container" |
| Windows native | CI on `windows-latest` for bootstrap and `doctor`, a manual procedure for anything graphical | "CI-verified bootstrap", the rest "pending manual verification" |
| WSL2 | A manual procedure on a Windows host, with an Ubuntu container as a proxy | "Container-verified", never "WSL2-verified" until run on WSL2 |
| Phone | A manual procedure | "Pending manual verification" |

Anything verified only on the maintainer's Arch machine is labelled as such wherever it appears.
