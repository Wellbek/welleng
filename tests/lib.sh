#!/usr/bin/env bash
# Tiny assertion helpers shared by the shell test suites.
# Source this file, run checks, then call finish.
set -euo pipefail

PASSED=0
FAILED=0

pass() { PASSED=$((PASSED + 1)); printf '  ok    %s\n' "$1"; }
fail() { FAILED=$((FAILED + 1)); printf '  FAIL  %s\n' "$1" >&2; }

# check "description" command args...
check() {
  local desc="$1"
  shift
  if "$@" >/dev/null 2>&1; then pass "$desc"; else fail "$desc"; fi
}

# check_not "description" command args...  (passes when the command fails)
check_not() {
  local desc="$1"
  shift
  if "$@" >/dev/null 2>&1; then fail "$desc"; else pass "$desc"; fi
}

finish() {
  printf '%s passed, %s failed\n' "$PASSED" "$FAILED"
  [ "$FAILED" -eq 0 ]
}
