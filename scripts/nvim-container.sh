#!/usr/bin/env bash
# Run tests/e2e/nvim.sh in a clean Arch container with Neovim, a compiler and network access.
#   scripts/nvim-container.sh                    test the configuration
#   scripts/nvim-container.sh --update-lock      also refresh home/dot_config/welleng-nvim/lazy-lock.json
# The image is cached as welleng-e2e-nvim, set WELLENG_REBUILD=1 to rebuild it.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image="welleng-e2e-nvim"

if [ "${WELLENG_REBUILD:-}" = "1" ] || ! docker image inspect "$image" >/dev/null 2>&1; then
  docker build -q -t "$image" - <<'DOCKERFILE' >/dev/null
FROM archlinux:latest
RUN pacman -Syu --noconfirm --needed neovim git gcc make tree-sitter-cli ripgrep fd curl unzip >/dev/null
DOCKERFILE
fi

if [ "${1:-}" = "--update-lock" ]; then
  out="$(mktemp -d)"
  trap 'rm -rf "$out"' EXIT
  docker run --rm -e WELLENG_NVIM_LOCK_OUT=/out -v "$out:/out" -v "$root:/repo:ro" -w /repo "$image" tests/e2e/nvim.sh
  cp "$out/lazy-lock.json" "$root/home/dot_config/welleng-nvim/lazy-lock.json"
  echo "updated home/dot_config/welleng-nvim/lazy-lock.json"
else
  exec docker run --rm -v "$root:/repo:ro" -w /repo "$image" tests/e2e/nvim.sh
fi
