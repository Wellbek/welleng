#!/usr/bin/env bash
# Connect an existing zsh, tmux and OpenSSH setup to Well-Engineering with one small managed
# block each. Idempotent and reversible: every file is backed up once, and --undo removes only
# the blocks this script added.
#   scripts/wire-in.sh --dry-run    show what would change
#   scripts/wire-in.sh              add the three blocks
#   scripts/wire-in.sh --undo       remove them again
# HOME is honoured, so the script can be tested against a copy of a real home directory.
set -euo pipefail

mode="apply"
case "${1:-}" in
  "") ;;
  --dry-run) mode="dry" ;;
  --undo) mode="undo" ;;
  *) echo "usage: wire-in.sh [--dry-run|--undo]" >&2; exit 2 ;;
esac

begin="# >>> welleng >>>"
end="# <<< welleng <<<"

has_block() { [ -f "$1" ] && grep -qxF "$begin" "$1"; }

backup_once() {
  [ -f "$1" ] && [ ! -e "$1.welleng-bak" ] && cp -p "$1" "$1.welleng-bak"
  return 0
}

remove_block() {
  local file="$1" tmp
  has_block "$file" || return 0
  tmp="$(mktemp)"
  # Drop the block and the single blank line this script put next to it.
  awk -v b="$begin" -v e="$end" '
    { line[NR] = $0 }
    END {
      for (i = 1; i <= NR; i++) { if (line[i] == b && !s) s = i; if (line[i] == e && s && !f) f = i }
      for (i = 1; i <= NR; i++) {
        if (i >= s && i <= f) continue
        if (i == s - 1 && line[i] == "") continue
        if (i == f + 1 && line[i] == "" && s == 1) continue
        print line[i]
      }
    }' "$file" >"$tmp"
  cat "$tmp" >"$file"
  rm -f "$tmp"
  echo "removed block from $file"
}

# add_block FILE POSITION BODY   POSITION is top or bottom
add_block() {
  local file="$1" where="$2" body="$3" tmp
  if has_block "$file"; then
    echo "already wired: $file"
    return 0
  fi
  if [ "$mode" = "dry" ]; then
    echo "would add to $file ($where):"
    printf '%s\n' "$body" | sed 's/^/    /'
    return 0
  fi
  backup_once "$file"
  tmp="$(mktemp)"
  {
    if [ "$where" = "bottom" ] && [ -f "$file" ]; then cat "$file"; fi
    if [ "$where" = "bottom" ]; then printf '\n'; fi
    printf '%s\n%s\n%s\n' "$begin" "$body" "$end"
    if [ "$where" = "top" ]; then
      printf '\n'
      if [ -f "$file" ]; then cat "$file"; fi
    fi
  } >"$tmp"
  if [ -f "$file" ]; then cat "$tmp" >"$file"; else mv "$tmp" "$file"; fi
  rm -f "$tmp"
  echo "wired: $file"
}

zshrc="$HOME/.zshrc"
tmuxconf="$HOME/.tmux.conf"
sshconf="$HOME/.ssh/config"

if [ "$mode" = "undo" ]; then
  remove_block "$zshrc"
  remove_block "$tmuxconf"
  remove_block "$sshconf"
  exit 0
fi

add_block "$zshrc" bottom '[[ -r ~/.config/welleng/shell/init.zsh ]] && source ~/.config/welleng/shell/init.zsh'
add_block "$tmuxconf" bottom 'source-file -q ~/.config/welleng/tmux-agents.conf'
if [ "$mode" != "dry" ]; then
  mkdir -p "$HOME/.ssh/config.d"
  chmod 700 "$HOME/.ssh" "$HOME/.ssh/config.d"
  [ -f "$sshconf" ] || { : >"$sshconf"; chmod 600 "$sshconf"; }
fi
add_block "$sshconf" top 'Include ~/.ssh/config.d/*.conf'
