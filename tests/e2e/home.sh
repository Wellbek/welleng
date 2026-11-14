#!/usr/bin/env bash
# End-to-end test of the chezmoi source state, in a throwaway HOME.
# Needs chezmoi, git, tmux and zsh on PATH. Never touches the real HOME.
#   tests/e2e/home.sh
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=../lib.sh
. "$root/tests/lib.sh"

for tool in chezmoi git tmux zsh; do
  command -v "$tool" >/dev/null 2>&1 || { echo "missing tool: $tool" >&2; exit 3; }
done

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
export HOME="$work/home"
mkdir -p "$HOME"
# Never inherit the real machine's configuration.
unset XDG_CONFIG_HOME XDG_DATA_HOME XDG_STATE_HOME XDG_CACHE_HOME
src="$work/src"
cp -r "$root" "$src"
rm -rf "$src/.git" "$src/tools/.venv"

cz() { chezmoi --source "$src" --destination "$HOME" "$@"; }

echo "chezmoi apply"
chezmoi init --source "$src" --destination "$HOME" \
  --promptString "Git author name=Test User" \
  --promptString "Git author email=test@example.invalid" >/dev/null 2>&1
check "init succeeds" test -f "$HOME/.config/chezmoi/chezmoi.toml"
check "apply succeeds (externals excluded)" cz apply --exclude=externals
check "verify reports no drift" cz verify --exclude=externals

echo "idempotence"
check "second apply changes nothing" bash -c "[ -z \"\$(chezmoi --source '$src' --destination '$HOME' diff --exclude=externals)\" ]"
check "git config rendered with the prompted name" grep -q "name = Test User" "$HOME/.gitconfig"
check "git config rendered with the prompted email" grep -q "test@example.invalid" "$HOME/.gitconfig"

echo "credentials"
check "secrets.env is never created by apply" test ! -e "$HOME/.config/welleng/secrets.env"
check "secrets example is deployed" test -f "$HOME/.config/welleng/secrets.env.example"
check_not "no key-like string in deployed files" \
  grep -rEq '(sk-[A-Za-z0-9]{20,}|[0-9a-f]{32}\.[A-Za-z0-9]{10,})' "$HOME"

echo "tmux"
check "tmux config loads without errors" bash -c "
  out=\$(tmux -L e2e-welleng -f '$HOME/.tmux.conf' start-server \; show -g prefix 2>&1) || true
  tmux -L e2e-welleng kill-server >/dev/null 2>&1 || true
  ! printf '%s' \"\$out\" | grep -qiE 'unknown command|error|invalid'"

echo "zsh helpers"
helper="$HOME/.config/welleng/shell/welleng.zsh"
check "welleng.zsh parses" zsh -n "$helper"
bin="$work/bin"
mkdir -p "$bin"
printf '#!/bin/sh\nprintf "%%s|%%s" "$ANTHROPIC_AUTH_TOKEN" "$ANTHROPIC_BASE_URL"\n' >"$bin/claude"
chmod +x "$bin/claude"
secrets="$work/secrets.env"
printf 'ZAI_API_KEY=fake-test-value\n' >"$secrets"
chmod 600 "$secrets"
out="$(PATH="$bin:$PATH" WELLENG_SECRETS_FILE="$secrets" zsh -c ". '$helper'; glm")"
check "glm passes the key only to the child process" test "$out" = "fake-test-value|https://api.z.ai/api/anthropic"
cat >"$work/leak.zsh" <<ZSH
. '$helper'
glm >/dev/null
print -r -- "\${ANTHROPIC_AUTH_TOKEN-unset}|\${ANTHROPIC_BASE_URL-unset}"
ZSH
leak="$(PATH="$bin:$PATH" WELLENG_SECRETS_FILE="$secrets" zsh "$work/leak.zsh")"
check "glm does not export the key into the shell" test "$leak" = "unset|unset"
check_not "glm fails clearly without a key" env PATH="$bin:$PATH" WELLENG_SECRETS_FILE="$work/missing.env" zsh -c ". '$helper'; glm"
printf 'ZAI_API_KEY=$(touch %s/pwned)\n' "$work" >"$secrets"
PATH="$bin:$PATH" WELLENG_SECRETS_FILE="$secrets" zsh -c ". '$helper'; glm" >/dev/null 2>&1 || true
check "a hostile secrets file is parsed, never executed" test ! -e "$work/pwned"

finish
