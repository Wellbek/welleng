#!/usr/bin/env bash
# Install the tools Well-Engineering needs, from the package map.
#   bootstrap/install.sh --dry-run             show the plan, change nothing
#   bootstrap/install.sh                       show the plan, ask, then install
#   bootstrap/install.sh --yes                 install without asking
#   bootstrap/install.sh --tiers mandatory     limit to some tiers, default mandatory,recommended
#   bootstrap/install.sh --chezmoi             also run `chezmoi init --apply` for this repository
# Packages come from the system package manager, run with sudo unless already root.
# Tools without a package are installed from pinned, checksum-verified release archives into
# ~/.local/bin, never from an unverified remote script. Idempotent: present tools are skipped.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dry_run=0
assume_yes=0
run_chezmoi=0
tiers="mandatory,recommended"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) dry_run=1 ;;
    --yes) assume_yes=1 ;;
    --chezmoi) run_chezmoi=1 ;;
    --tiers) tiers="${2:?--tiers needs a value}"; shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

case "$(uname -s)" in
  Linux | Darwin) ;;
  *) echo "unsupported shell platform: $(uname -s), use bootstrap/install.ps1 on Windows" >&2; exit 1 ;;
esac

if command -v pacman >/dev/null 2>&1; then manager=pacman
elif command -v apt-get >/dev/null 2>&1; then manager=apt
elif command -v dnf >/dev/null 2>&1; then manager=dnf
elif command -v brew >/dev/null 2>&1; then manager=brew
else echo "no supported package manager found (pacman, apt, dnf, brew)" >&2; exit 1
fi

if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
  echo "Python 3.11 or newer is required to read the package map." >&2
  echo "Install it with your package manager first (pacman: python, apt: python3, dnf: python3, brew: python)." >&2
  exit 1
fi

export PATH="$HOME/.local/bin:$PATH"
pkgs=()
others=()
while IFS=$'\t' read -r kind name value; do
  case "$kind" in
    pkg) pkgs+=("$value"); printf 'package   %-10s %s\n' "$name" "$value" ;;
    fallback) others+=("$name"); printf 'release   %-10s pinned archive (or manual: %s)\n' "$name" "$value" ;;
    unavailable) others+=("$name"); printf 'manual    %-10s %s\n' "$name" "$value" ;;
  esac
done < <(python3 -I "$root/bootstrap/plan.py" "$manager" --tiers "$tiers")

if [ "${#pkgs[@]}" -eq 0 ] && [ "${#others[@]}" -eq 0 ]; then
  echo "nothing to install"
fi
if [ "$dry_run" -eq 1 ]; then
  echo "dry run: nothing was changed"
  exit 0
fi
if [ "$assume_yes" -eq 0 ] && { [ "${#pkgs[@]}" -gt 0 ] || [ "${#others[@]}" -gt 0 ]; }; then
  printf 'Proceed? [y/N] '
  read -r answer
  [ "$answer" = "y" ] || { echo "aborted"; exit 1; }
fi

sudo_cmd=()
if [ "$(id -u)" -ne 0 ]; then
  command -v sudo >/dev/null 2>&1 || { echo "sudo is required to install packages" >&2; exit 1; }
  sudo_cmd=(sudo)
fi

if [ "${#pkgs[@]}" -gt 0 ]; then
  case "$manager" in
    pacman) "${sudo_cmd[@]}" pacman -S --noconfirm --needed "${pkgs[@]}" ;;
    apt)
      "${sudo_cmd[@]}" apt-get update -qq
      "${sudo_cmd[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y "${pkgs[@]}"
      ;;
    dnf) "${sudo_cmd[@]}" dnf install -y "${pkgs[@]}" ;;
    brew) brew install "${pkgs[@]}" ;;
  esac
fi

for name in ${others[@]+"${others[@]}"}; do
  # A tool without a pinned release stays in the remaining list below.
  python3 -I "$root/bootstrap/install_release.py" "$name" || true
done

echo
python3 -I "$root/bootstrap/plan.py" "$manager" --tiers "$tiers" >"${TMPDIR:-/tmp}/welleng-remaining.$$" || true
remaining="$(cut -f2 "${TMPDIR:-/tmp}/welleng-remaining.$$" | paste -sd' ' -)"
rm -f "${TMPDIR:-/tmp}/welleng-remaining.$$"
status=0
if [ -n "$remaining" ]; then
  echo "still missing: $remaining"
  echo "see the notes in packages/packages.toml for how to install them by hand"
  # Only a missing mandatory tool is a failure.
  if python3 -I "$root/bootstrap/plan.py" "$manager" --tiers mandatory | grep -q .; then status=1; fi
fi
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "add \$HOME/.local/bin to PATH" ;; esac

if [ "$run_chezmoi" -eq 1 ]; then
  command -v chezmoi >/dev/null 2>&1 || { echo "chezmoi is not installed, cannot apply the configuration" >&2; exit 1; }
  chezmoi init --apply --source "$root"
else
  echo "configuration not applied, run: chezmoi init --apply --source \"$root\"   (or rerun with --chezmoi)"
fi
exit "$status"
