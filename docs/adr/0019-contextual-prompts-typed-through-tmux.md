# 0019 - Contextual prompts are typed into the Claude pane through tmux

Status: Accepted
Date: 2026-11-15
Builds on: [0010](0010-claude-in-a-tmux-pane-with-an-editor-bridge.md)

## Context

ADR 0010 runs Claude Code in a tmux pane and uses claudecode.nvim only as a bridge, with the `none` terminal provider.
`:ClaudeCodeSendText` works only with the in-editor terminal providers, so the plugin cannot type an instruction into a pane it does not own.
Keys such as "explain this selection" need both the code reference and an instruction.

## Decision

A contextual key does two things.
It sends the selection, or the current buffer as an `@file` reference, through the bridge with `:ClaudeCodeSend` or `:ClaudeCodeAdd %`.
It then types a fixed instruction into the Claude pane with `tmux send-keys -l`, and moves focus there.
It never presses Enter, so the user always reads the instruction and sends it.

The pane is the first other pane in the current tmux window whose command is `claude` or a bare version number, because native installs run a versioned executable.
`vim.g.welleng_claude_pane` overrides the detection.
When no pane is found, the instruction goes to the clipboard and a warning explains it.

## Consequences

- No new dependency and nothing sent without the user pressing Enter.
- The pane detection depends on how tmux reports the command name, which differs between installs.
  The matching logic is unit tested, and a real `claude` pane has been seen as `claude` on Arch `[verified: Arch]`.
  The full flow with a live Claude Code session is a manual check, see `docs/verification/interactive.md`.
- Several Claude panes in one window make the choice ambiguous, and the override variable is the escape hatch.
