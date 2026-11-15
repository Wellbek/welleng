# Verify Remote Control from a phone

Status of what this covers: `welleng rc` and the port check are written and unit tested.
No phone has connected, so the approval flow and the effort change from a phone are unverified.

## Steps

1. On the machine, run `welleng rc --ports snapshot`.
2. Inside tmux, run `welleng rc --name verify`.
   Expected: a tmux window named `rc` appears, started with `--permission-mode default`.
3. Run `welleng rc --ports diff`.
   Expected: `ports check: ok`.
   Any line starting with `NEW EXPOSED LISTENER` is a failure, stop and record the address.
4. On the phone, open the Claude app, find the session named `verify`, and send a prompt that needs a tool permission.
   Expected: the prompt arrives, and the permission request is shown on the phone and not auto-approved.
5. Approve one request and deny another.
   Expected: the approved action runs and the denied one does not.
6. From the phone, change the effort level.
   Expected: the change applies to that session only, and `welleng hints report` later shows the new level where the hook receives it.
7. Close the `rc` window.
   Expected: the session disappears from the phone.

## Record

Update the Phase 7 rows in `CHECKLIST.md` with the phone, the app version and the date.
