#!/usr/bin/env bash
# End-to-end test of the Neovim configuration in a throwaway XDG tree. Needs network access to
# GitHub for the plugins, neovim, git, and a C compiler for Treesitter.
#   tests/e2e/nvim.sh
#   WELLENG_NVIM_LOCK_OUT=DIR tests/e2e/nvim.sh   also write a fresh lazy-lock.json into DIR
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=../lib.sh
. "$root/tests/lib.sh"

for tool in nvim git; do
  command -v "$tool" >/dev/null 2>&1 || { echo "missing tool: $tool" >&2; exit 3; }
done

work="$(mktemp -d)"
trap 'rm -rf "$work" 2>/dev/null || true' EXIT
export HOME="$work/home" XDG_CONFIG_HOME="$work/config" XDG_DATA_HOME="$work/data" XDG_STATE_HOME="$work/state" XDG_CACHE_HOME="$work/cache"
mkdir -p "$HOME" "$XDG_CONFIG_HOME"
export NVIM_APPNAME=welleng-nvim
cp -r "$root/home/dot_config/welleng-nvim" "$XDG_CONFIG_HOME/$NVIM_APPNAME"

nv() { timeout 900 nvim --headless "$@"; }

if [ -f "$XDG_CONFIG_HOME/$NVIM_APPNAME/lazy-lock.json" ]; then
  check "plugins install at the pinned versions" nv "+Lazy! restore" +qa
else
  check "plugins install (no lockfile yet)" nv "+Lazy! sync" +qa
fi
check "lazy-lock.json exists" test -s "$XDG_CONFIG_HOME/$NVIM_APPNAME/lazy-lock.json"
check "LazyVim loads" nv "+lua assert(require('lazyvim'))" +qa
check "startup prints no errors" bash -c "[ -z \"\$(timeout 120 nvim --headless +qa 2>&1)\" ]"
check "the user keymap layer is active" nv "+lua assert(vim.fn.maparg('<leader>wk','n') ~= '')" +qa
check "the Claude Code bridge keys exist" nv "+lua assert(vim.fn.maparg('<leader>ab','n') ~= '')" +qa
check "exrc is enabled so projects can add local config safely" nv "+lua assert(vim.o.exrc == true)" +qa
check "no plugin failed to load" bash -c "[ -z \"\$(timeout 120 nvim --headless '+lua for n,p in pairs(require(\"lazy\").plugins()) do if not p._.loaded and not p.lazy then print(n) end end' +qa 2>&1)\" ]"
if [ -n "${WELLENG_NVIM_LOCK_OUT:-}" ]; then
  cp "$XDG_CONFIG_HOME/$NVIM_APPNAME/lazy-lock.json" "$WELLENG_NVIM_LOCK_OUT/lazy-lock.json"
fi

finish
