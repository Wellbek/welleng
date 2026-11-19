#!/usr/bin/env bash
# Check one commit message file, as the commit-msg hook does.
#   scripts/check-commit-msg.sh FILE
# Rules:
#   - the subject follows Conventional Commits: type(scope): subject, with an optional ! for a breaking change
#     (merge, revert, fixup! and squash! subjects that git writes are accepted)
#   - no attribution to an AI assistant: a Co-Authored-By trailer naming one, a session link trailer
#     or a "Generated with" line
# The words in a subject are never checked, because this project is about Claude Code.
set -euo pipefail

msg_file="${1:?usage: check-commit-msg.sh FILE}"
body="$(grep -v '^#' -- "$msg_file" || true)"
subject="$(printf '%s\n' "$body" | sed -n '/[^[:space:]]/{p;q;}')"

status=0
types='feat|fix|docs|chore|ci|test|refactor|perf|build|style|revert'
if ! printf '%s\n' "$subject" | grep -Eq "^(($types)(\([a-z0-9._/-]+\))?!?: [^ ].*|Merge .+|Revert \".+\"|(fixup|squash|amend)! .+)$"; then
  echo "commit-msg: the subject must look like 'type(scope): subject' with type one of ${types//|/, }" >&2
  echo "commit-msg: got: $subject" >&2
  status=1
fi

ai='claude|anthropic|openai|chatgpt|gpt-[0-9]|copilot|gemini|cursor|codex'
if printf '%s\n' "$body" | grep -Eiq "^co-authored-by:.*($ai)" \
  || printf '%s\n' "$body" | grep -Eiq '^claude-session:' \
  || printf '%s\n' "$body" | grep -Eiq 'generated (with|by) \[?(claude|chatgpt|copilot|cursor|codex)'; then
  echo "commit-msg: remove the AI attribution line, commit messages describe the change only" >&2
  status=1
fi

exit "$status"
