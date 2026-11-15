# Windows and WSL2

Nothing in this project has been run on Windows or WSL2.
Everything here is written, parsed, or exercised with stubs on Linux, and is labelled that way in [CHECKLIST.md](../../CHECKLIST.md).
Use these paths as a starting point and report what breaks.

## Recommended: WSL2

WSL2 is the first-class Windows path, see [ADR 0004](../adr/0004-wsl2-first-native-windows-best-effort.md).
Inside the distribution it is an ordinary Linux install.

1. Enable WSL2 and install Ubuntu 24.04.
   This can need administrator rights and a reboot.
2. Keep the repository and your configuration on the Linux filesystem, for example `~/src`, never under `/mnt/c`.
   `chmod 600` on `secrets.env` only holds on ext4.
3. Follow [installation](installation.md) inside the distribution.
4. Install WezTerm on the Windows side.
   Set the user environment variable `WELLENG_WSL_DISTRO` to the distribution name, for example `setx WELLENG_WSL_DISTRO Ubuntu-24.04`, and WezTerm starts `wsl.exe -d <distro> --cd ~ -- tmux new -A -s welleng`.

Procedure to verify it: [docs/verification/wsl2.md](../verification/wsl2.md).

## Fallback: native Windows

Best effort.
There is no tmux on native Windows, and the alternative, psmux, has not been run for this project.

```powershell
powershell -ExecutionPolicy Bypass -File bootstrap\install.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File bootstrap\install.ps1
```

- Packages come from winget.
  Tools without a winget id are listed, never installed from an unverified script.
- `-Tiers` selects tiers, default `mandatory,recommended`.
- `-Yes` skips the question.

What is checked so far: `install.ps1` and the profile parse with PowerShell's own parser in CI, and the CI `windows` job runs a dry run and `welleng doctor` on a Windows runner.
That job is best effort and was written without a Windows run, so its first result decides.

### PowerShell profile

Opt in from your PowerShell 7 profile (`$PROFILE`):

```powershell
if (Test-Path "$HOME\Documents\PowerShell\welleng.ps1") { . "$HOME\Documents\PowerShell\welleng.ps1" }
```

It sets up starship, zoxide, the lazygit delta config and the `y` function for yazi, each guarded and never replacing something you already defined.
The credential helpers (`glm`) exist for zsh only.
Tested with stub tools in a PowerShell 7 container on Linux.

### WezTerm

chezmoi on Windows deploys `~/.config/wezterm/wezterm.lua`.
It is ignored on other systems.
It sets scrollback, padding, makes Alt reach the program, and starts PowerShell 7 or WSL2 tmux depending on `WELLENG_WSL_DISTRO`.
Only its Lua syntax was checked.

Procedure to verify: [docs/verification/windows.md](../verification/windows.md).
