#!/usr/bin/env bash
# Create the credentials file from the example, with mode 600, and report which variables are set.
#   scripts/init-secrets.sh            create the file if it is missing, then show status
#   scripts/init-secrets.sh --status   only show status
# An existing file is never overwritten, and values are never printed.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
example="$repo/home/dot_config/welleng/secrets.env.example"
target="${WELLENG_SECRETS_FILE:-$HOME/.config/welleng/secrets.env}"
mode="${1:-init}"

if [ "$mode" != "--status" ]; then
  if [ -e "$target" ]; then
    echo "exists, left untouched: $target"
  else
    mkdir -p "$(dirname "$target")"
    (umask 077 && cp "$example" "$target")
    chmod 600 "$target"
    echo "created: $target (mode 600)"
  fi
fi

if [ ! -e "$target" ]; then
  echo "missing: $target" >&2
  exit 1
fi

perm="$(stat -c '%a' "$target" 2>/dev/null || stat -f '%Lp' "$target" 2>/dev/null || echo '?')"
if [ "$perm" != "600" ]; then
  echo "warning: $target has mode $perm, expected 600 (run: chmod 600 \"$target\")" >&2
fi

echo
echo "Required: none (Claude Code uses /login, GitHub uses gh auth login)."
echo "Optional variables in $target:"
while IFS= read -r name; do
  if grep -E "^${name}=.+" "$target" >/dev/null; then
    state="set"
  else
    state="empty"
  fi
  printf '  %-20s %s\n' "$name" "$state"
done < <(grep -oE '^[A-Z][A-Z0-9_]*=' "$example" | tr -d '=')
