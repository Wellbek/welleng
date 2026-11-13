#!/usr/bin/env bash
# Minimal secret scan of staged files, used only when gitleaks is not installed.
# It prints file names, never the matching lines, so a secret cannot be echoed.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

patterns='(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(API_KEY|AUTH_TOKEN|SECRET|PASSWORD|TOKEN)[A-Z_]*[[:space:]]*[=:][[:space:]]*["'"'"']?[A-Za-z0-9_./+-]{20,})'

status=0
while IFS= read -r -d '' file; do
  if git show ":$file" | grep -IE -- "$patterns" >/dev/null; then
    echo "possible secret in staged file: $file" >&2
    status=1
  fi
done < <(git diff --cached --name-only --diff-filter=ACM -z)

if [ "$status" -ne 0 ]; then
  echo "Commit blocked. Remove the secret, or if it is a false positive adjust .gitleaks.toml." >&2
fi
exit "$status"
