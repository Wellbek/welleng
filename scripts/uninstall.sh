#!/usr/bin/env bash
# Remove what Well-Engineering added to a machine. Dry run unless --yes is given.
#   scripts/uninstall.sh            show what would be removed
#   scripts/uninstall.sh --yes      remove it
# Removes: the wired blocks (restoring your files), the files deployed under ~/.config/welleng and
# ~/.config/welleng-nvim, welleng state and Neovim caches, the uv tool and the Claude Code plugin
# when those commands exist.
# Never removes: secrets.env, files you created in those directories, ~/.ssh/config.d fragments,
# packages installed with your package manager, and the chezmoi binary and its config.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
yes=0
case "${1:-}" in
  "") ;;
  --yes) yes=1 ;;
  *) echo "usage: uninstall.sh [--yes]" >&2; exit 2 ;;
esac

act() {
  if [ "$yes" -eq 1 ]; then
    "$@"
  else
    printf 'would run:'
    printf ' %q' "$@"
    printf '\n'
  fi
}

# 1. Wired blocks, which also restore the original bytes of your files.
if [ "$yes" -eq 1 ]; then
  "$root/scripts/wire-in.sh" --undo
else
  for f in "$HOME/.zshrc" "$HOME/.tmux.conf" "$HOME/.ssh/config"; do
    if [ -f "$f" ] && grep -qxF "# >>> welleng >>>" "$f"; then echo "would remove the welleng block from $f"; fi
  done
fi

# 2. Files deployed from the source state. Only paths that exist in the source tree are removed, so secrets.env stays.
while IFS= read -r tracked; do
  target="$HOME/.config/${tracked#home/dot_config/}"
  [ -e "$target" ] || [ -L "$target" ] || continue
  act rm -f -- "$target"
done < <(cd "$root" && find home/dot_config/welleng home/dot_config/welleng-nvim -type f 2>/dev/null | sort)

# 3. State and caches created by this project.
for dir in "$HOME/.local/state/welleng" "$HOME/.local/share/welleng-nvim" "$HOME/.local/state/welleng-nvim" "$HOME/.cache/welleng-nvim"; do
  [ -d "$dir" ] && act rm -rf -- "$dir"
done

# 4. Empty directories left behind. rmdir refuses to remove a directory that still has files.
if [ "$yes" -eq 1 ]; then
  for dir in "$HOME/.config/welleng/shell" "$HOME/.config/welleng" "$HOME/.config/welleng-nvim/lua/config" "$HOME/.config/welleng-nvim/lua/plugins" "$HOME/.config/welleng-nvim/lua/user" "$HOME/.config/welleng-nvim/lua" "$HOME/.config/welleng-nvim"; do
    if [ -d "$dir" ] && ! rmdir "$dir" 2>/dev/null; then echo "kept (not empty): $dir"; fi
  done
fi

# 5. The command and the plugin.
if command -v uv >/dev/null 2>&1 && uv tool list 2>/dev/null | grep -q '^welleng '; then act uv tool uninstall welleng; fi
if command -v claude >/dev/null 2>&1; then
  if claude plugin list 2>/dev/null | grep -q 'welleng@welleng-local'; then act claude plugin uninstall welleng@welleng-local; fi
  if claude plugin marketplace list 2>/dev/null | grep -q 'welleng-local'; then act claude plugin marketplace remove welleng-local; fi
fi

[ "$yes" -eq 1 ] || echo "dry run: nothing was changed, rerun with --yes"
