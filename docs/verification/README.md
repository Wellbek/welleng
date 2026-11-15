# Manual verification procedures

Some features cannot be tested from the maintainer's Linux machine or from CI.
Each procedure here is a short, repeatable checklist for a person with the right device.
When you finish one, record the result in `CHECKLIST.md` with the platform and the date, and use the evidence tags from `docs/adr/README.md`.
A feature stays "implemented, verification pending" until its procedure has been run.

| Procedure | Needs | Covers |
|---|---|---|
| [windows.md](windows.md) | A Windows 11 machine | `bootstrap/install.ps1`, native fallback, psmux |
| [wsl2.md](wsl2.md) | Windows 11 with WSL2 | The first-class Windows path |
| [phone.md](phone.md) | A phone with the Claude app | Remote Control and the port check |
| [interactive.md](interactive.md) | An interactive Claude Code session | Hooks, effort hints and the `/harness` skill |
