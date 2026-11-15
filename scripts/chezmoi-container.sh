#!/usr/bin/env bash
# Run a command inside a clean Arch Linux container with the repository mounted read-only.
#   scripts/chezmoi-container.sh tests/e2e/home.sh
# The image with the test tools is built once and cached as welleng-e2e-arch, set
# WELLENG_REBUILD=1 to rebuild it from the newest base image.
# WELLENG_USER_FILES=DIR mounts DIR read-only at /user-files, WELLENG_DEBUG is passed through.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image="welleng-e2e-arch"

if [ "${WELLENG_REBUILD:-}" = "1" ] || ! docker image inspect "$image" >/dev/null 2>&1; then
  docker build -q -t "$image" - <<'DOCKERFILE' >/dev/null
FROM archlinux:latest
RUN pacman -Syu --noconfirm --needed chezmoi git tmux zsh python shellcheck openssh diffutils starship zoxide fzf fd >/dev/null \
 && git config --global --add safe.directory /repo
DOCKERFILE
fi

extra=(-e "WELLENG_DEBUG=${WELLENG_DEBUG:-}")
if [ -n "${WELLENG_USER_FILES:-}" ]; then
  extra+=(-v "$WELLENG_USER_FILES:/user-files:ro" -e WELLENG_USER_FILES=/user-files)
fi
exec docker run --rm "${extra[@]}" -v "$root:/repo:ro" -w /repo "$image" "$@"
