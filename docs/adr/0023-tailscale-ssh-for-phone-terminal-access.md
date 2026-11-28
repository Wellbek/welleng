# 0023 - Tailscale SSH for terminal access from a phone

Status: Accepted
Date: 2026-11-28

## Context

Remote Control gives a phone the Claude conversation of one session, but not the shell, Neovim or the tmux panes around it.
`docs/security.md` already allowed an optional route over Tailscale, SSH and tmux, with Tailscale device identity plus SSH keys and no public port.
On WSL2, an OpenSSH server inside WSL2 is not reachable from the tailnet when Tailscale runs on the Windows host, unless WSL networking is changed as well.
The route must not become a standing internet-facing service, and it must be easy to switch off.

## Options considered

- OpenSSH server with key-only login, reached over Tailscale on the Windows host, which needs a running `sshd`, key copying to each phone and WSL2 mirrored networking.
- OpenSSH server with key-only login and Tailscale inside WSL2, which needs a running `sshd` and key copying to each phone.
- Tailscale SSH with Tailscale inside the Linux or WSL2 machine, where `tailscaled` answers SSH on the tailnet only and authenticates with the tailnet identity and policy `[docs]`.

## Decision

The optional phone terminal route is Tailscale SSH with Tailscale running inside the Linux or WSL2 machine, set up and switched off with `scripts/phone-ssh.sh`.
Remote Control stays the default way to reach Claude from a phone.

## Consequences

- No `sshd` runs, no SSH key is copied to a phone, and port 22 is answered only for traffic from the tailnet `[docs]`.
- Authentication is the Tailscale account, and the default policy asks for a fresh sign-in every 12 hours in check mode `[docs]`.
  This replaces the "plus SSH keys" rule in `docs/security.md`.
- Whoever controls the Tailscale account can reach a shell on the machine while Tailscale SSH is on, so the account needs strong sign-in, and `scripts/phone-ssh.sh off --yes` switches it off.
- On WSL2, Tailscale must not run on the Windows host at the same time, and `tailscaled` needs systemd `[docs]`.
- The script installs from the Arch package, or from Tailscale's apt repository on Ubuntu and Debian, and points to the official instructions elsewhere, because the upstream one-line installer pipes a script into `sh`.
- Nothing of this has run with a phone, the procedure is in `docs/verification/phone.md`.
