#!/usr/bin/env bash
# Print " waiting:N" when Claude Code sessions wait for you, nothing otherwise.
# Lives in a script because a closing parenthesis inside a tmux #() command ends the command early.
set -euo pipefail

count="$(welleng agents --count 2>/dev/null || true)"
case "$count" in
  "" | 0 | "?") ;;
  *) printf ' waiting:%s' "$count" ;;
esac
