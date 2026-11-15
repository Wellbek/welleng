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

diffview_opens() (
  local repo
  repo="$(mktemp -d)"
  git -C "$repo" init -q .
  git -C "$repo" config user.email t@example.invalid
  git -C "$repo" config user.name t
  echo one >"$repo/f.txt"
  git -C "$repo" add f.txt
  git -C "$repo" commit -q -m init
  echo two >>"$repo/f.txt"
  cd "$repo"
  # Mason may print an abort notice when Neovim exits while a tool is still installing, that is
  # unrelated, so assert on a success marker and on the absence of Lua errors only.
  local out
  out="$(timeout 120 nvim --headless '+DiffviewOpen' '+lua vim.wait(2000, function() return false end)' \
    '+lua assert(require("diffview.lib").get_current_view() ~= nil); print("DIFFVIEW_OK")' +qa 2>&1)"
  case "$out" in *DIFFVIEW_OK*) ;; *) echo "$out"; return 1 ;; esac
  case "$out" in *"Error executing"* | *"stack traceback"* | *E5108*) echo "$out"; return 1 ;; esac
)

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
check "the diffview commands and keys exist" nv "+lua assert(vim.fn.maparg('<leader>gd','n') ~= '' and vim.fn.maparg('<leader>gH','n') ~= '' and vim.fn.maparg('<leader>gm','n') ~= '')" +qa
check "the gitsigns blame toggle key exists" nv "+lua assert(vim.fn.maparg('<leader>gT','n') ~= '')" +qa
check "the Claude bridge is loaded at startup, so claude --ide can find the editor" nv "+lua assert(vim.fn.exists(':ClaudeCodeSend') == 2 and vim.fn.exists(':ClaudeCodeAdd') == 2)" +qa
check "the contextual Claude prompt keys exist in normal and visual mode" nv "+lua for _,k in ipairs({'e','f','t','r'}) do assert(vim.fn.maparg('<leader>a'..k,'n') ~= '' and vim.fn.maparg('<leader>a'..k,'v') ~= '') end" +qa
check "the Claude pane is found by command name or version, and never the own pane" nv "+lua local c=require('user.claude'); assert(c.find_pane('%1\\tzsh\\n%2\\t2.1.325\\n', '%1') == '%2'); assert(c.find_pane('%1\\tclaude\\n', '%1') == nil); assert(c.find_pane('%1\\tzsh\\n%3\\tnvim\\n', '%9') == nil)" +qa
check "diffview opens on a real repository with a change" diffview_opens
check "exrc is enabled so projects can add local config safely" nv "+lua assert(vim.o.exrc == true)" +qa
check "no plugin failed to load" bash -c "[ -z \"\$(timeout 120 nvim --headless '+lua for n,p in pairs(require(\"lazy\").plugins()) do if not p._.loaded and not p.lazy then print(n) end end' +qa 2>&1)\" ]"
if [ -n "${WELLENG_NVIM_LOCK_OUT:-}" ]; then
  cp "$XDG_CONFIG_HOME/$NVIM_APPNAME/lazy-lock.json" "$WELLENG_NVIM_LOCK_OUT/lazy-lock.json"
fi

finish
