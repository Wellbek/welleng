#!/usr/bin/env bash
# Static security and policy checks over the tracked files. Needs only git, grep and python3.
#   tests/security/static.sh
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"
# shellcheck source=../lib.sh
. tests/lib.sh

tracked() { git ls-files -z; }

echo "credentials"
check_not "no tracked secrets.env or .env file" bash -c \
  "git ls-files | grep -E '(^|/)(secrets\.env|\.env)$'"
check "secrets.env is gitignored" git check-ignore -q home/dot_config/welleng/secrets.env
check "the example holds only empty placeholders" bash -c \
  "! grep -E '^[A-Z_]+=.+' home/dot_config/welleng/secrets.env.example | grep -v -E '=(\"\"|)\$' | grep -qv '^#'"
check_not "no private key block in tracked files" bash -c \
  "git grep -I -q -E -e '-----BEGIN [A-Z ]*PRIVATE KEY-----' -- . ':!tests/security/static.sh' ':!.gitleaks.toml' ':!scripts/scan-secrets-fallback.sh'"
check_not "no API key shaped token in tracked files" bash -c \
  "git grep -I -q -E 'sk-ant-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}' -- . ':!tests/security/static.sh' ':!.gitleaks.toml' ':!scripts/scan-secrets-fallback.sh'"

echo "privacy rules"
check_not "no host, IP or SSH fragment tracked in home/" bash -c \
  "git grep -I -q -E '([0-9]{1,3}\.){3}[0-9]{1,3}|^[[:space:]]*(HostName|IdentityFile)[[:space:]]' -- home"

echo "agent permission baseline"
check "settings deny reading secrets.env" python3 -I - <<'PY'
import json, sys
deny = json.load(open(".claude/settings.json"))["permissions"]["deny"]
need = {"Read(**/secrets.env)", "Read(**/.env)", "Read(~/.config/welleng/secrets.env)"}
sys.exit(0 if need <= set(deny) else 1)
PY

echo "shell script policy"
while IFS= read -r f; do
  check "strict mode: $f" grep -q '^set -euo pipefail' "$f"
  check_not "never sources a secrets file: $f" grep -E '^[^#]*(source|\.)[[:space:]]+[^ ]*secrets\.env' "$f"
  check_not "no pipe into a shell: $f" grep -E 'curl[^|]*\|[[:space:]]*(ba|z)?sh' "$f"
done < <(git ls-files 'scripts/*.sh' '.githooks/*' 'tests/*.sh' 'tests/*/*.sh' 'bootstrap/*.sh')

echo "workflow hardening"
check "CI uses least-privilege permissions" grep -q '^permissions:' .github/workflows/ci.yml
check_not "CI does not use pull_request_target" grep -q 'pull_request_target' .github/workflows/ci.yml

finish
