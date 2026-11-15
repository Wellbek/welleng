# Verify WSL2

Status of what this covers: nothing in this project has been run on WSL2, so none of it may be called verified there.

## Steps

1. Enable WSL2 and install Ubuntu 24.04, which can need administrator rights and a reboot.
2. Keep the repository on the Linux filesystem, for example under `~/src`, never under `/mnt/c`.
3. Run `bootstrap/install.sh --dry-run`, then `bootstrap/install.sh`.
   Expected: the same result as the Ubuntu container run recorded in `CHECKLIST.md`.
4. Run `scripts/regression.sh --quick`.
   Expected: every stage passes or is skipped for a missing tool, never fails.
5. Check that `chmod 600 ~/.config/welleng/secrets.env` sticks, with `stat -c %a`.
   Expected: `600`, which only holds on the ext4 filesystem.
6. Run `welleng doctor`, `welleng keys` and `welleng repos`.
   Expected: they behave as on Linux.

## Record

Add a "Tested on WSL2" note, with the Windows build and the distribution, to the rows that passed.
