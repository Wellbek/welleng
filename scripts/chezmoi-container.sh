#!/usr/bin/env bash
# Run a command inside a clean Arch Linux container with the repository mounted read-only.
#   scripts/chezmoi-container.sh tests/e2e/home.sh
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec docker run --rm -v "$root:/repo:ro" -w /repo archlinux:latest bash -c '
  set -euo pipefail
  pacman -Syu --noconfirm --needed chezmoi git tmux zsh python shellcheck >/dev/null
  git config --global --add safe.directory /repo
  "$@"
' bash "$@"
