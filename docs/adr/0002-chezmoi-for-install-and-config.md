# 0002 - chezmoi for installation and configuration

Status: Accepted
Date: 2026-11-13

## Context

The environment must install reproducibly on Linux, WSL2 and Windows.
Configuration differs per operating system and per machine, so templating is required.
Applying must be idempotent and must show a diff before changing anything.

## Options considered

- GNU Stow: symlinks only, no Windows support, no templating.
- Dotbot: runs on Windows, but has no templating and only basic idempotence.
- Nix with home-manager: excellent reproducibility, but heavy and WSL-only on Windows.
- A custom installer: would re-implement most of chezmoi.
- chezmoi: Windows support, per-OS templates, `chezmoi diff` and `chezmoi apply`, and a one-line fresh-machine bootstrap.

## Decision

Use chezmoi as the installation and configuration manager.
The source state lives under `home/`, selected with `.chezmoiroot`.

## Consequences

chezmoi copies files by default, so editing a live config does not edit the repository.
Directories that are edited live, such as the Neovim config, use `symlink_` entries so the target points into the repository.
If symlinks are unavailable on Windows, fall back to copy mode and a documented `chezmoi re-add` workflow.

## Spike result

Tested with chezmoi v2.74.1 on Linux x86_64 against a throwaway repository and a fake `$HOME` `[verified: Arch]`.
The release archive was checksum-verified and run from a scratch directory, nothing was installed system-wide.

| Check | Result |
|---|---|
| `.chezmoiroot` set to `home`, `--source` pointing at the repository root | Works, the source path resolves to `<repo>/home` |
| Per-machine data through `promptStringOnce` | Works, see the prompt note below |
| OS templating with `.chezmoi.os` | Works |
| Per-OS exclusion with `.chezmoiignore` | Works, a Windows-only path is not deployed on Linux |
| Live-edited directory as `symlink_nvim.tmpl` containing `{{ .chezmoi.workingTree }}/nvim` | Works, and an edit made through the target lands in the repository |
| `run_onchange` script keyed on `packages/packages.toml`, which is outside the source root | Works with both `include "../packages/packages.toml"` and `joinPath .chezmoi.workingTree "packages/packages.toml" \| include`, and it re-runs only after the file changes |
| Idempotence | A second apply made no changes, `chezmoi diff` was empty and `chezmoi verify` exited 0 |
| `apply --dry-run --verbose` | Prints the plan and writes nothing, which is the basis for the installer's `--dry-run` |

Findings that shape the installer:

- **A pre-existing, differing file is overwritten silently on the first apply**, with no prompt and no backup.
  The bootstrap must therefore back up conflicting targets itself before the first `chezmoi apply`, as the plan already requires.
- **`--promptString` matches the prompt text, not the data key.**
  Unattended runs must pass the full prompt text, for example `--promptString "Your name=..."`, and must close stdin, otherwise chezmoi waits for input.
- **An ignored child still leaves its parent directory in the plan.**
  Ignore the whole `Documents` directory for the PowerShell profile, not only its `PowerShell` subdirectory.
- Prefer the explicit `.chezmoi.workingTree` form of `include`, so a file outside the source root is addressed the same way everywhere.

Not yet verified `[spike]`:

- Symlink entries on Windows, which need Developer Mode.
- WSL detection through the kernel release string, which was not exercised because the test host is not WSL.
- macOS.
