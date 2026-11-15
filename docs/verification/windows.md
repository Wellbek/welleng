# Verify native Windows

Status of what this covers: `bootstrap/install.ps1` is written and has never run.
WSL2 is the supported Windows path, native Windows is best effort, see ADR 0004.

## Steps

1. On a clean Windows 11 machine, open PowerShell 7 and clone this repository on a local NTFS path.
2. Run `powershell -ExecutionPolicy Bypass -File bootstrap\install.ps1 -DryRun`.
   Expected: a plan is printed, the exit code is 0, and nothing was installed.
3. Run it without `-DryRun`, answer `y`.
   Expected: each package installs through winget, and tools without a winget id are listed as manual.
4. Open a new terminal and run `python -I bootstrap\plan.py winget --tiers mandatory`.
   Expected: no output, which means no mandatory tool is left.
5. Check the optional terminal tmux alternative: install `psmux`, start a session, split a pane, detach and attach again.
   Expected: the four checks listed in ADR 0003 pass.
   If they do not, record which one failed.

## Record

Update the `bootstrap/install.ps1` and Spike 6 rows in `CHECKLIST.md` with the Windows build number and the date.
