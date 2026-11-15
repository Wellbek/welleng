#!/usr/bin/env bash
# Prove that scripts/wire-in.sh does not break an existing zsh, tmux and OpenSSH setup.
# Needs chezmoi, tmux, zsh and openssh, and never touches the real HOME.
#   tests/e2e/wire-in.sh                          synthetic fixtures
#   WELLENG_USER_FILES=DIR tests/e2e/wire-in.sh   DIR holds copies named zshrc, tmux.conf, ssh_config
# Real files are only compared by hash and counts, their content is never printed.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=../lib.sh
. "$root/tests/lib.sh"

for tool in chezmoi tmux zsh ssh; do
  command -v "$tool" >/dev/null 2>&1 || { echo "missing tool: $tool" >&2; exit 3; }
done

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
HOME="$work/home"
export HOME
mkdir -p "$HOME/.ssh"
unset XDG_CONFIG_HOME XDG_DATA_HOME XDG_STATE_HOME XDG_CACHE_HOME

fixtures="${WELLENG_USER_FILES:-$work/fixtures}"
if [ -z "${WELLENG_USER_FILES:-}" ]; then
  mkdir -p "$fixtures"
  printf 'export EDITOR=vim\nalias ll="ls -l"\nPS1="> "\n' >"$fixtures/zshrc"
  printf 'set -g prefix M-o\nset -g status-right "%%H"\nbind r source-file ~/.tmux.conf\n' >"$fixtures/tmux.conf"
  printf 'Host alpha\n  HostName alpha.example.invalid\n  User dev\nHost beta\n  HostName beta.example.invalid\n  Port 2222\nHost *\n  ServerAliveInterval 30\n' >"$fixtures/ssh_config"
fi
[ -f "$fixtures/zshrc" ] && cp "$fixtures/zshrc" "$HOME/.zshrc"
[ -f "$fixtures/tmux.conf" ] && cp "$fixtures/tmux.conf" "$HOME/.tmux.conf"
[ -f "$fixtures/ssh_config" ] && cp "$fixtures/ssh_config" "$HOME/.ssh/config"
chmod 600 "$HOME/.ssh/config" 2>/dev/null || true

hashof() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }

# snapshot DIR: observable behaviour of the three tools, written as files in DIR.
snapshot() {
  local out="$1"
  mkdir -p "$out"
  : >"$out/ssh"
  if [ -f "$HOME/.ssh/config" ]; then
    while IFS= read -r host; do
      printf '== %s\n' "$host" >>"$out/ssh"
      ssh -G "$host" 2>/dev/null | grep -v -i '^include' >>"$out/ssh" || true
    done < <(awk 'tolower($1)=="host" {for (i = 2; i <= NF; i++) if ($i !~ /[*?!]/) print $i}' "$HOME/.ssh/config" | sort -u)
  fi
  tmux -L e2e-wire kill-server >/dev/null 2>&1 || true
  # One invocation: the server exits as soon as it has no session.
  tmux -L e2e-wire -f "$HOME/.tmux.conf" start-server \; show -g prefix \; show -g status-right >"$out/tmux-opts" 2>"$out/tmux-err" || true
  grep '^prefix' "$out/tmux-opts" >"$out/tmux-prefix" || true
  grep '^status-right' "$out/tmux-opts" >"$out/tmux-status" || true
  tmux -L e2e-wire kill-server >/dev/null 2>&1 || true
  rc=0
  zsh -i -c 'alias; print -l ${(k)parameters} ${(k)functions}; typeset -x; bindkey; print -r -- "PROMPT=$PROMPT RPROMPT=$RPROMPT"; print -l $precmd_functions $chpwd_functions' >"$out/zsh-out" 2>"$out/zsh-err" </dev/null || rc=$?
  echo "$rc" >"$out/zsh-rc"
  sort -u "$out/zsh-out" -o "$out/zsh-out"
}

orig_z="$(hashof "$HOME/.zshrc")"
orig_t="$(hashof "$HOME/.tmux.conf")"
orig_s="$(hashof "$HOME/.ssh/config")"
snapshot "$work/before"

echo "deploy the welleng directory only"
chezmoi init --source "$root" --destination "$HOME" \
  --promptString "Git author name=Test" --promptString "Git author email=t@example.invalid" >/dev/null 2>&1
check "chezmoi applies only ~/.config/welleng" chezmoi --source "$root" --destination "$HOME" apply --exclude=externals "$HOME/.config/welleng"
check "the user's own files were not touched by the deploy" test "$orig_z$orig_t$orig_s" = "$(hashof "$HOME/.zshrc")$(hashof "$HOME/.tmux.conf")$(hashof "$HOME/.ssh/config")"
check "no tmux, git or zsh file was deployed" test ! -e "$HOME/.gitconfig"

echo "wire-in"
check "dry run succeeds" "$root/scripts/wire-in.sh" --dry-run
check "dry run changed nothing" test "$orig_z$orig_t$orig_s" = "$(hashof "$HOME/.zshrc")$(hashof "$HOME/.tmux.conf")$(hashof "$HOME/.ssh/config")"
check "apply succeeds" "$root/scripts/wire-in.sh"
after_z="$(hashof "$HOME/.zshrc")"
after_t="$(hashof "$HOME/.tmux.conf")"
after_s="$(hashof "$HOME/.ssh/config")"
check "a second apply is a no-op" bash -c "'$root/scripts/wire-in.sh' >/dev/null && [ '$after_z$after_t$after_s' = \"\$(sha256sum '$HOME/.zshrc' | cut -d' ' -f1)\$(sha256sum '$HOME/.tmux.conf' | cut -d' ' -f1)\$(sha256sum '$HOME/.ssh/config' | cut -d' ' -f1)\" ]"
check "ssh config keeps mode 600" test "$(stat -c %a "$HOME/.ssh/config")" = "600"
check "the Include line is the first non-comment line" bash -c "grep -v '^#' '$HOME/.ssh/config' | grep -v '^\$' | head -1 | grep -q '^Include'"
check "backups exist" test -e "$HOME/.zshrc.welleng-bak" -a -e "$HOME/.tmux.conf.welleng-bak"

snapshot "$work/after"
if [ "${WELLENG_DEBUG:-}" = "1" ]; then diff -ru "$work/before" "$work/after" || true; fi

echo "behaviour is unchanged"
check "ssh -G output is identical for every host" cmp -s "$work/before/ssh" "$work/after/ssh"
check "tmux prefix is unchanged" cmp -s "$work/before/tmux-prefix" "$work/after/tmux-prefix"
check "tmux gains no new errors" cmp -s "$work/before/tmux-err" "$work/after/tmux-err"
check "tmux status line keeps its original content" grep -qF "$(sed 's/^status-right //; s/^"//; s/"$//' "$work/before/tmux-status" | head -c 20)" "$work/after/tmux-status"
check "the agents segment is present in the status line" grep -q 'welleng agents' "$work/after/tmux-status"
check "zsh exit status is unchanged" cmp -s "$work/before/zsh-rc" "$work/after/zsh-rc"
check "zsh startup prints no new errors" bash -c "[ -z \"\$(comm -13 <(sort -u '$work/before/zsh-err') <(sort -u '$work/after/zsh-err'))\" ]"
removed="$(comm -23 "$work/before/zsh-out" "$work/after/zsh-out" | wc -l)"
check "no alias, variable or export was removed or changed" test "$removed" -eq 0
added="$(comm -13 "$work/before/zsh-out" "$work/after/zsh-out" | { grep -oE '^[A-Za-z_]+' || true; } | sort -u | tr '\n' ' ')"
check "init.zsh is really sourced (glm exists after, not before)" bash -c "! grep -qx glm '$work/before/zsh-out' && grep -qx glm '$work/after/zsh-out'"
echo "  info  names added to the shell: ${added:-none}"

echo "undo"
check "undo succeeds" "$root/scripts/wire-in.sh" --undo
check "undo restores the zsh file exactly" test "$orig_z" = "$(hashof "$HOME/.zshrc")"
check "undo restores the tmux file exactly" test "$orig_t" = "$(hashof "$HOME/.tmux.conf")"
check "undo restores the ssh config exactly" test "$orig_s" = "$(hashof "$HOME/.ssh/config")"

finish
