# User guides

These guides explain how to install, use and configure Well-Engineering.
They describe what exists today, and every claim about verification points to [CHECKLIST.md](../../CHECKLIST.md).
Anything verified only on the maintainer's Arch Linux machine is labelled as such.

| Guide | Read it to |
|---|---|
| [Installation](installation.md) | Install the tools, deploy the configuration, connect an existing setup, update and uninstall |
| [Command reference](commands.md) | Look up every `welleng` command and its options |
| [Configuration](configuration.md) | Find every file the project deploys, every opt-in and every environment variable |
| [Claude Code](claude-code.md) | Use the plugin, the `/welleng:harness` skill, the agents dashboard, effort hints and the editor bridge |
| [Workflow](workflow.md) | Use `/welleng:mode`, its playbooks and the standalone workflow skills |
| [Terminal, shell and editor](terminal-and-editor.md) | Learn the tmux, Neovim, git, kitty, yazi and shell setup and its keys |
| [Remote machines and mobile](remote-and-mobile.md) | Manage SSH hosts and run Remote Control from a phone safely |
| [Windows and WSL2](windows.md) | Use the Windows paths, which are not verified yet |

For the reasons behind the design, read the [decision records](../adr/README.md).
For problems, read [troubleshooting](../troubleshooting.md).

## Which path should I take

| You want | Do this |
|---|---|
| Everything, on a fresh Linux machine | [Installation](installation.md), the full flow |
| Only the `welleng` commands | `uv tool install --editable tools`, then [commands](commands.md) |
| Only the Claude Code skills | [Just the skills](../../README.md#just-the-skills) |
| To keep your current zsh, tmux and SSH setup untouched | [Installation](installation.md#connect-an-existing-setup), the wire-in is reversible and changes nothing until you run it |
