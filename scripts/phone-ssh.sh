#!/usr/bin/env bash
# Optional phone terminal access: Tailscale SSH into this machine, then attach to tmux.
#
# Usage: scripts/phone-ssh.sh [status|install|on|off] [--yes]
#
#   status   (default) report Tailscale, Tailscale SSH, WSL, systemd and the tmux sessions, change nothing
#   install  install Tailscale from the distribution package and start tailscaled
#   on       sign this machine in to your tailnet and enable Tailscale SSH
#   off      disable Tailscale SSH, the machine stays in the tailnet
#
# Every changing command is printed and only runs with --yes, and every step is idempotent.
# Tailscale SSH needs no OpenSSH server and opens no port on the public network, see ADR 0023.
set -euo pipefail

action="status"
yes=0
for arg in "$@"; do
  case "$arg" in
    status | install | on | off) action="$arg" ;;
    --yes) yes=1 ;;
    -h | --help)
      sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "phone-ssh: unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

act() {
  if [ "$yes" -eq 1 ]; then
    echo "+ $*"
    "$@"
  else
    echo "would run: $*"
  fi
}

have() { command -v "$1" >/dev/null 2>&1; }

is_wsl() { grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; }

pid1() { ps -p 1 -o comm= 2>/dev/null || echo unknown; }

distro_id() {
  if [ -r /etc/os-release ]; then
    # shellcheck disable=SC1091
    (. /etc/os-release && echo "${ID:-unknown} ${ID_LIKE:-}")
  else
    echo unknown
  fi
}

# One field from `tailscale status --json`, empty when Tailscale is missing or not running.
ts_field() {
  have tailscale || return 0
  tailscale status --json 2>/dev/null | python3 -I -c '
import json, sys
try:
    data = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
field = sys.argv[1]
if field == "state":
    print(data.get("BackendState", ""))
elif field == "dns":
    print((data.get("Self") or {}).get("DNSName", "").rstrip("."))
' "$1" || true
}

ssh_enabled() {
  have tailscale || { echo "unknown"; return 0; }
  tailscale debug prefs 2>/dev/null | python3 -I -c '
import json, sys
try:
    print("yes" if json.load(sys.stdin).get("RunSSH") else "no")
except ValueError:
    print("unknown")
' || echo "unknown"
}

status() {
  local state dns
  echo "machine:"
  if is_wsl; then
    echo "  WSL2, pid 1 is $(pid1)"
    if [ "$(pid1)" != "systemd" ]; then
      echo "  advice   tailscaled needs systemd here: add [boot] systemd=true to /etc/wsl.conf, then run wsl --shutdown in Windows"
    fi
    echo "  note     run Tailscale either in WSL2 or on the Windows host, not both, see docs/guides/remote-and-mobile.md"
  else
    echo "  $(distro_id | cut -d' ' -f1), pid 1 is $(pid1)"
  fi

  echo "tailscale:"
  if ! have tailscale; then
    echo "  missing  run: scripts/phone-ssh.sh install"
  else
    state="$(ts_field state)"
    dns="$(ts_field dns)"
    echo "  state    ${state:-tailscaled not running}"
    echo "  ssh      $(ssh_enabled)"
    if [ -n "$dns" ]; then
      echo "  connect  ssh $(id -un)@$dns"
    fi
  fi

  echo "tmux sessions to attach to:"
  if have tmux && tmux ls 2>/dev/null | sed 's/^/  /'; then
    :
  else
    echo "  none, start one with: welleng up"
  fi
}

# Tailscale's own apt repository, added the manual way it documents, without piping a script into sh.
install_apt() {
  local id codename base keyring list
  # shellcheck disable=SC1091
  id="$(. /etc/os-release && echo "$ID")"
  # shellcheck disable=SC1091
  codename="$(. /etc/os-release && echo "${VERSION_CODENAME:-}")"
  if [ -z "$codename" ]; then
    echo "phone-ssh: no VERSION_CODENAME in /etc/os-release, follow https://tailscale.com/download/linux" >&2
    return 1
  fi
  base="https://pkgs.tailscale.com/stable/$id/$codename"
  keyring="/usr/share/keyrings/tailscale-archive-keyring.gpg"
  list="/etc/apt/sources.list.d/tailscale.list"
  if ! curl -fsSI "$base.tailscale-keyring.list" >/dev/null; then
    echo "phone-ssh: Tailscale has no repository for $id $codename yet, follow https://tailscale.com/download/linux" >&2
    return 1
  fi
  [ -f "$keyring" ] || act sudo curl -fsSL "$base.noarmor.gpg" -o "$keyring"
  [ -f "$list" ] || act sudo curl -fsSL "$base.tailscale-keyring.list" -o "$list"
  act sudo apt-get update
  act sudo apt-get install -y tailscale
}

install() {
  if have tailscale; then
    echo "tailscale is already installed: $(tailscale version 2>/dev/null | head -n1)"
  else
    case " $(distro_id) " in
      *" arch "*) act sudo pacman -S --needed tailscale ;;
      *" ubuntu "* | *" debian "*) install_apt ;;
      *)
        echo "phone-ssh: this script installs Tailscale on Arch, Ubuntu and Debian only."
        echo "Elsewhere follow https://tailscale.com/download/linux, then rerun scripts/phone-ssh.sh install to start the service."
        return 1
        ;;
    esac
  fi
  if [ "$(pid1)" = "systemd" ]; then
    if systemctl is-active --quiet tailscaled; then
      echo "tailscaled is running"
    else
      act sudo systemctl enable --now tailscaled
    fi
  else
    echo "phone-ssh: pid 1 is not systemd, so tailscaled cannot be started as a service, see status for the WSL2 fix" >&2
    return 1
  fi
}

on() {
  have tailscale || { echo "phone-ssh: tailscale is missing, run: scripts/phone-ssh.sh install" >&2; return 1; }
  if [ "$(ts_field state)" != "Running" ]; then
    echo "Sign-in: tailscale up prints a login URL, open it and sign in with the account your phone uses."
    act sudo tailscale up
  fi
  if [ "$(ssh_enabled)" = "yes" ]; then
    echo "Tailscale SSH is already on"
  else
    act sudo tailscale set --ssh
  fi
  [ "$yes" -eq 1 ] && status
  return 0
}

off() {
  have tailscale || { echo "tailscale is not installed, nothing to turn off"; return 0; }
  if [ "$(ssh_enabled)" = "no" ]; then
    echo "Tailscale SSH is already off"
  else
    act sudo tailscale set --ssh=false
  fi
  echo "To leave the tailnet entirely: sudo tailscale down"
}

"$action"
if [ "$action" != "status" ] && [ "$yes" -eq 0 ]; then
  echo "dry run: nothing was changed, rerun with --yes"
fi
