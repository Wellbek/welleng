#!/usr/bin/env bash
# Whole-product test on one distribution: bootstrap the tools, then run the home end-to-end test
# and the Python tests with what the bootstrap installed. Runs only inside a container.
#   scripts/distro-container.sh ubuntu tests/e2e/distro.sh
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [ "${WELLENG_E2E_CONTAINER:-}" != "1" ]; then
  echo "refusing to install packages outside a container" >&2
  exit 3
fi

HOME="$(mktemp -d)"
export HOME
export PATH="$HOME/.local/bin:$PATH"

echo "== bootstrap"
"$root/bootstrap/install.sh" --yes

echo "== home end-to-end"
"$root/tests/e2e/home.sh"

echo "== Python tests"
# The repository is mounted read-only, so work on a copy.
copy="$(mktemp -d)"
cp -r "$root/." "$copy/"
rm -rf "$copy/.git" "$copy/tools/.venv"
(cd "$copy/tools" && uv run --quiet pytest -q)
