#!/usr/bin/env bash
# Full regression run: hygiene, secret scan, shell lint, security policy, Python tests and the
# end-to-end home test.
#   scripts/regression.sh              host stages, container stage when docker is available
#   scripts/regression.sh --quick      host stages only, no container
#   scripts/regression.sh --matrix     also run the slow container tests: bootstrap on Ubuntu, Fedora and Arch, and the Neovim configuration
#   scripts/regression.sh --strict     a skipped stage counts as a failure (use in CI and before release)
# Every stage ends as PASS, FAIL or SKIP, and the exit code is non-zero on any FAIL.
# The stage_* functions are called indirectly by run_stage, so ShellCheck cannot see the calls.
# shellcheck disable=SC2329
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

quick=0
strict=0
matrix=0
for arg in "$@"; do
  case "$arg" in
    --quick) quick=1 ;;
    --strict) strict=1 ;;
    --matrix) matrix=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

results=()
failed=0

run_stage() {
  local name="$1"
  shift
  printf '\n== %s\n' "$name"
  local rc=0
  "$@" || rc=$?
  case "$rc" in
    0) results+=("PASS  $name") ;;
    77) results+=("SKIP  $name"); [ "$strict" -eq 0 ] || failed=1 ;;
    *) results+=("FAIL  $name"); failed=1 ;;
  esac
}

need() { command -v "$1" >/dev/null 2>&1 || { echo "tool not found: $1"; return 77; }; }

stage_hygiene() { scripts/check-hygiene.sh; }
stage_secrets() {
  need gitleaks || return 77
  gitleaks dir --redact --no-banner --config .gitleaks.toml . 2>/dev/null \
    || gitleaks detect --no-git --redact --no-banner --config .gitleaks.toml --source .
}
stage_shell() {
  local files=()
  while IFS= read -r f; do files+=("$f"); done < <(git ls-files 'scripts/*.sh' '.githooks/*' 'tests/*.sh' 'tests/*/*.sh' 'bootstrap/*.sh' '.claude/skills/*/scripts/*.sh')
  for f in "${files[@]}"; do bash -n "$f"; done
  if command -v shellcheck >/dev/null 2>&1; then
    shellcheck -x "${files[@]}"
  elif [ "$quick" -eq 0 ] && docker info >/dev/null 2>&1; then
    scripts/chezmoi-container.sh shellcheck -x "${files[@]}"
  else
    echo "shellcheck is not installed and the container fallback is off"
    return 77
  fi
}
stage_security() { tests/security/static.sh; }
stage_python() {
  need uv || return 77
  (cd tools && uv run --quiet pytest -q)
}
stage_plugin() {
  need claude || return 77
  claude plugin validate claude-plugin
  claude plugin validate claude-plugin-hooks
  claude plugin validate .
}
stage_packages() { python3 -I -c "import tomllib,sys; d=tomllib.load(open('packages/packages.toml','rb')); sys.exit(0 if d['package'] else 1)"; }
stage_e2e() {
  if [ "$quick" -eq 1 ]; then echo "--quick given"; return 77; fi
  if command -v chezmoi >/dev/null 2>&1; then
    tests/e2e/home.sh
  elif docker info >/dev/null 2>&1; then
    scripts/chezmoi-container.sh tests/e2e/home.sh
  else
    echo "neither chezmoi nor docker is available"
    return 77
  fi
}

stage_powershell() {
  if [ "$quick" -eq 1 ]; then echo "--quick given"; return 77; fi
  # The test writes under $HOME, so it only ever runs in a container.
  if docker info >/dev/null 2>&1; then
    docker run --rm -e WELLENG_E2E_CONTAINER=1 -v "$root:/repo:ro" -w /repo mcr.microsoft.com/powershell:latest \
      pwsh -NoProfile -File tests/e2e/powershell-profile.ps1
  else
    echo "docker is not available"
    return 77
  fi
}

run_stage "repository hygiene" stage_hygiene
run_stage "secret scan of the working tree" stage_secrets
run_stage "shell syntax and ShellCheck" stage_shell
run_stage "security policy checks" stage_security
run_stage "package map parses" stage_packages
run_stage "Claude Code plugin validates" stage_plugin
run_stage "Python unit tests" stage_python
run_stage "end-to-end home test" stage_e2e
run_stage "PowerShell profile (container)" stage_powershell
if [ "$quick" -eq 0 ] && command -v docker >/dev/null 2>&1; then
  run_stage "wire-in end-to-end" scripts/chezmoi-container.sh tests/e2e/wire-in.sh
fi
if [ "$matrix" -eq 1 ]; then
  for distro in ubuntu fedora arch; do
    run_stage "bootstrap end-to-end on $distro" scripts/distro-container.sh "$distro" tests/e2e/bootstrap.sh
  done
  run_stage "Neovim configuration end-to-end" scripts/nvim-container.sh
fi

printf '\n== summary\n'
printf '%s\n' "${results[@]}"
exit "$failed"
