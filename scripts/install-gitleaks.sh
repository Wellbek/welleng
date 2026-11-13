#!/usr/bin/env bash
# Install a pinned, checksum-verified gitleaks release without root.
#   scripts/install-gitleaks.sh [DEST_DIR]    default destination: ~/.local/bin
# Override the pinned version with GITLEAKS_VERSION.
# Used by developers and by CI, so the scanner version is defined in one place.
set -euo pipefail

version="${GITLEAKS_VERSION:-8.30.1}"
dest="${1:-$HOME/.local/bin}"

case "$(uname -s)" in
  Linux) os="linux" ;;
  Darwin) os="darwin" ;;
  *) echo "unsupported operating system: $(uname -s)" >&2; exit 1 ;;
esac
case "$(uname -m)" in
  x86_64 | amd64) arch="x64" ;;
  aarch64 | arm64) arch="arm64" ;;
  *) echo "unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac

archive="gitleaks_${version}_${os}_${arch}.tar.gz"
base="https://github.com/gitleaks/gitleaks/releases/download/v${version}"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

curl -sSfL -o "$tmp/$archive" "$base/$archive"
curl -sSfL -o "$tmp/checksums.txt" "$base/gitleaks_${version}_checksums.txt"

if command -v sha256sum >/dev/null 2>&1; then
  verify=(sha256sum -c -)
else
  verify=(shasum -a 256 -c -)
fi
(cd "$tmp" && grep " ${archive}\$" checksums.txt | "${verify[@]}")

tar -xzf "$tmp/$archive" -C "$tmp" gitleaks
mkdir -p "$dest"
install -m 0755 "$tmp/gitleaks" "$dest/gitleaks"
echo "installed: $dest/gitleaks"
"$dest/gitleaks" version
