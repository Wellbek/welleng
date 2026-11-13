# Well-Engineering shell helpers for zsh.
# Source this file from ~/.zshrc:
#   [[ -r ~/.config/welleng/shell/welleng.zsh ]] && source ~/.config/welleng/shell/welleng.zsh
#
# Credentials stay in ~/.config/welleng/secrets.env (mode 600).
# They are read one name at a time, on demand, and are never exported into the interactive shell.

# Print the value of one secret, or return non-zero if it is missing or empty.
# The file is parsed, not sourced, so nothing inside it is ever executed.
_welleng_secret() {
  local name="$1"
  local file="${WELLENG_SECRETS_FILE:-$HOME/.config/welleng/secrets.env}"
  local line
  [[ -r "$file" ]] || return 1
  line=$(grep -E "^[[:space:]]*(export[[:space:]]+)?${name}=" "$file" | tail -n 1) || return 1
  line=${line#*=}
  line=${line#[\"\']}
  line=${line%[\"\']}
  [[ -n "$line" ]] || return 1
  print -r -- "$line"
}

# Run Claude Code against z.ai GLM models.
# Needs ZAI_API_KEY in secrets.env.
# Remote Control does not work in these sessions, because the API base URL is overridden.
glm() {
  local key
  key=$(_welleng_secret ZAI_API_KEY) || {
    print -u2 "glm: ZAI_API_KEY is not set. Run scripts/init-secrets.sh, then add it to ~/.config/welleng/secrets.env"
    return 1
  }
  ANTHROPIC_AUTH_TOKEN="$key" \
  ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
  API_TIMEOUT_MS="3000000" \
  ANTHROPIC_DEFAULT_OPUS_MODEL="glm-5.2[1m]" \
  ANTHROPIC_DEFAULT_SONNET_MODEL="glm-5.2[1m]" \
  ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.7" \
  CLAUDE_CODE_AUTO_COMPACT_WINDOW="1000000" \
    command claude "$@"
}
