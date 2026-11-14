#!/usr/bin/env bash
# Run a command inside a clean distribution container with the repository mounted read-only.
#   scripts/distro-container.sh {ubuntu|fedora|arch} COMMAND [ARGS...]
# The container has python3 and certificates only, so it behaves like a fresh machine.
set -euo pipefail

distro="${1:?usage: distro-container.sh ubuntu|fedora|arch COMMAND...}"
shift
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

case "$distro" in
  ubuntu) image="ubuntu:24.04"; prepare="apt-get update -qq && apt-get install -y -qq python3 ca-certificates git sudo" ;;
  fedora) image="fedora:latest"; prepare="dnf install -y -q python3 ca-certificates git sudo" ;;
  arch) image="archlinux:latest"; prepare="pacman -Syu --noconfirm --needed python ca-certificates git sudo" ;;
  *) echo "unknown distro: $distro" >&2; exit 2 ;;
esac

exec docker run --rm -e WELLENG_E2E_CONTAINER=1 -v "$root:/repo:ro" -w /repo "$image" \
  bash -c "set -euo pipefail; $prepare >/dev/null; git config --global --add safe.directory /repo; \"\$@\"" bash "$@"
