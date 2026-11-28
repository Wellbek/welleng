# Verify phone access

Status of what this covers: `welleng rc`, the port check and the dry runs of `scripts/phone-ssh.sh` are written and tested on a machine.
No phone has connected by either way, so everything below is unverified.
Run each part once with an iPhone and once with an Android phone, and record which one you used.

## A. Remote Control

1. On the machine, run `welleng rc --ports snapshot`.
2. In a running Claude Code session, type `/rc verify`.
   Expected: a URL and a QR code appear.
3. Run `welleng rc --ports diff` in another pane.
   Expected: `ports check: ok`.
   Any line starting with `NEW EXPOSED LISTENER` is a failure, stop and record the address.
4. On the phone, scan the QR code, or open the Claude app, tap **Code** and find the session named `verify`.
   Expected: the earlier conversation is visible.
5. Send a prompt that needs a tool permission.
   Expected: the prompt arrives, and the permission request is shown on the phone and not auto-approved.
6. Approve one request and deny another.
   Expected: the approved action runs and the denied one does not.
7. From the phone, change the effort level.
   Expected: the change applies to that session only, and `welleng hints report` later shows the new level where the hook receives it.
8. Lock the phone, trigger a permission request from the machine, and check for a push notification after enabling **Push when actions required** in `/config`.
9. Run `/rc` on the machine and disconnect.
   Expected: the session disappears from the phone and keeps running in the terminal.
10. Repeat steps 2 to 9 with `welleng rc --name verify` inside tmux, which uses server mode in a window named `rc`, and close that window at the end.

## B. Tailscale SSH and tmux

1. Run `scripts/phone-ssh.sh`, then `install --yes` and `on --yes` as the guide describes.
   Expected: status shows `state Running`, `ssh yes` and a `connect` line.
2. Run `welleng rc --ports snapshot` before step 1 and `welleng rc --ports diff` after it.
   Expected: any new listener is on a `100.` tailnet address or loopback only, record what appears.
3. On the phone, turn on Tailscale and connect with the SSH client to the `connect` line.
   Expected: a sign-in URL in check mode, then a shell as your user.
4. Run `tmux attach -t` with a session from `tmux ls`.
   Expected: the same panes as on the laptop, and input on the phone appears on the laptop.
5. Detach with the prefix and `d`, then with `tmux detach`.
   Expected: the session keeps running.
6. Run `scripts/phone-ssh.sh off --yes` and try to connect again.
   Expected: the connection is refused or times out.

## Record

Update the Phase 7 rows in `CHECKLIST.md` with the phone, its OS, the app versions and the date.
