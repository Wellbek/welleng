#!/usr/bin/env bash
# Drive an interactive Claude Code session for verification, on a private tmux server.
#   drive.sh start PROJECT_DIR EVIDENCE_DIR [CLAUDE_ARGS...]  start claude in PROJECT_DIR, hook state in EVIDENCE_DIR/state
#   drive.sh doctor                                           read-only health check of the verification server
#   drive.sh trust [SECONDS]                                  answer the workspace trust dialog with "Yes", checked on screen
#   drive.sh send TEXT                                        type TEXT literally, then press Enter
#   drive.sh keys KEY...                                      send tmux key names, such as Enter or Escape
#   drive.sh wait REGEX [SECONDS]                             wait until the pane matches REGEX (default 60 s)
#   drive.sh capture FILE                                     save the visible pane and its scrollback to FILE
#   drive.sh stop                                             kill the verification server only
# The server socket is always "verify-welleng", so the user's own tmux server and welleng:* sessions are never touched.
set -euo pipefail

SOCKET="verify-welleng"
SESSION="verify"
t() { tmux -L "$SOCKET" "$@"; }

cmd="${1:-}"
shift || true
case "$cmd" in
  start)
    project="${1:?project dir}"; evidence="${2:?evidence dir}"; shift 2
    if t has-session -t "$SESSION" 2>/dev/null; then
      echo "drive: a verification session is already running, run drive.sh stop first" >&2
      exit 1
    fi
    mkdir -p "$evidence/state"
    printf -v args ' %q' "$@"
    t new-session -d -s "$SESSION" -x 200 -y 50 -c "$project" \
      "env XDG_STATE_HOME=$(printf '%q' "$evidence/state") claude${args}; sleep 600"
    ;;
  doctor)
    command -v claude >/dev/null || { echo "doctor: claude is not on PATH"; exit 1; }
    t has-session -t "$SESSION" 2>/dev/null || { echo "doctor: no verification session"; exit 1; }
    pane_cmd="$(t display-message -p -t "$SESSION" '#{pane_current_command}')"
    echo "doctor: session up, pane runs ${pane_cmd}, claude $(claude --version | head -1)"
    ;;
  trust)
    limit="${1:-30}"
    "$0" wait 'trust this folder' "$limit"
    for _ in $(seq 1 20); do
      sleep 0.5
      if t capture-pane -p -J -t "$SESSION" | grep -Eq '❯ +Yes, I trust this folder'; then
        t send-keys -t "$SESSION" Enter
        exit 0
      fi
      t send-keys -t "$SESSION" Down
    done
    echo "drive: could not select Yes in the trust dialog" >&2
    exit 1
    ;;
  send)
    t send-keys -t "$SESSION" -l -- "${1:?text}"
    sleep 0.3
    t send-keys -t "$SESSION" Enter
    ;;
  keys)
    t send-keys -t "$SESSION" "$@"
    ;;
  wait)
    pattern="${1:?regex}"; limit="${2:-60}"
    for _ in $(seq 1 "$((limit * 2))"); do
      if t capture-pane -p -J -S -200 -t "$SESSION" | grep -Eq -- "$pattern"; then exit 0; fi
      sleep 0.5
    done
    echo "drive: timed out after ${limit}s waiting for: $pattern" >&2
    exit 1
    ;;
  capture)
    out="${1:?file}"
    mkdir -p "$(dirname "$out")"
    t capture-pane -p -J -S -500 -t "$SESSION" > "$out"
    ;;
  stop)
    t kill-server 2>/dev/null || true
    ;;
  *)
    sed -n '2,11p' "$0" >&2
    exit 2
    ;;
esac
