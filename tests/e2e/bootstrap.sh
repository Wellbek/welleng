#!/usr/bin/env bash
# End-to-end test of bootstrap/install.sh. It really installs packages, so it refuses to run
# unless WELLENG_E2E_CONTAINER=1 is set, which scripts/distro-container.sh does inside a container.
#   scripts/distro-container.sh ubuntu tests/e2e/bootstrap.sh
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=../lib.sh
. "$root/tests/lib.sh"

if [ "${WELLENG_E2E_CONTAINER:-}" != "1" ]; then
  echo "refusing to install packages outside a container" >&2
  exit 3
fi

HOME="$(mktemp -d)"
export HOME
export PATH="$HOME/.local/bin:$PATH"

echo "dry run"
out="$("$root/bootstrap/install.sh" --dry-run)"
check "dry run says nothing changed" grep -q "dry run: nothing was changed" <<<"$out"
check "dry run installed nothing" test ! -e "$HOME/.local/bin"

echo "install"
check "install succeeds" "$root/bootstrap/install.sh" --yes
mapfile -t manager < <(command -v pacman apt-get dnf | head -n 1 | xargs -n1 basename)
case "${manager[0]}" in apt-get) mgr=apt ;; *) mgr="${manager[0]}" ;; esac
remaining="$(python3 -I "$root/bootstrap/plan.py" "$mgr" --tiers mandatory)"
check "no mandatory tool is left to install" test -z "$remaining"
for tool in git chezmoi uv tmux zsh nvim rg fzf zoxide lazygit jq; do
  check "$tool is on PATH" command -v "$tool"
done
check "installed chezmoi runs" chezmoi --version
check "installed uv runs" uv --version

echo "idempotence"
second="$("$root/bootstrap/install.sh" --yes --tiers mandatory 2>&1)"
check "second run has nothing to install" grep -q "nothing to install" <<<"$second"

echo "tampering"
bad="$(mktemp -d)"
sed 's/sha256 = "[0-9a-f]\{64\}"/sha256 = "0000000000000000000000000000000000000000000000000000000000000000"/' \
  "$root/packages/releases.toml" >"$bad/releases.toml"
check_not "a wrong checksum is rejected" python3 -I "$root/bootstrap/install_release.py" glow --manifest "$bad/releases.toml" --dest "$bad/bin"
check "nothing was written after a rejected checksum" test ! -e "$bad/bin/glow"

finish
