#!/usr/bin/env bash
# Repository hygiene checks, shared by the pre-commit hook and CI.
#   scripts/check-hygiene.sh            check every tracked file
#   scripts/check-hygiene.sh --staged   check only staged content
# Checks:
#   - no em dash character in any text file (use a plain dash)
#   - no secrets.env or .env style file is tracked
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

mode="${1:-all}"
emdash=$'\xe2\x80\x94'

if [ "$mode" = "--staged" ]; then
  list_files() { git diff --cached --name-only --diff-filter=ACM -z; }
  show_file() { git show ":$1"; }
else
  list_files() { git ls-files -z; }
  show_file() { cat -- "$1"; }
fi

status=0
while IFS= read -r -d '' file; do
  [ "$mode" = "--staged" ] || [ -e "$file" ] || continue

  case "$file" in
    *.example) ;;
    secrets.env|*/secrets.env|.env|*/.env|.env.*|*/.env.*)
      echo "forbidden file is tracked: $file" >&2
      status=1
      ;;
  esac

  if show_file "$file" | grep -I -- "$emdash" >/dev/null; then
    echo "em dash found, use a plain dash: $file" >&2
    status=1
  fi
done < <(list_files)

exit "$status"
