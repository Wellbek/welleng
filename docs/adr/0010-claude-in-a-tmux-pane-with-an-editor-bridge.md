# 0010 - Claude in a tmux pane with an editor bridge

Status: Accepted
Date: 2026-11-13

## Context

Claude Code should work with the editor, with selection sharing and diff review, without being trapped inside it.
The session should be visible to monitoring and to Remote Control as an ordinary session.

## Options considered

- Run `claude` in a Neovim terminal buffer: the session dies when Neovim quits.
- Use only a terminal split with no bridge: loses selection and diff review.
- Run `claude` in a tmux pane and let claudecode.nvim provide only the bridge.

## Decision

`claude` runs in a persistent tmux pane.
claudecode.nvim provides the bridge only: selection, `@file` references and native diff review.

## Consequences

The session survives Neovim quitting, tmux navigation is uniform, and the dashboard and Remote Control see an ordinary session.
If the bridge cannot be used, fall back to an editor-hosted terminal.

## Spike result

Tested on Arch with Neovim 0.12.1 and claudecode.nvim at commit `bcf1f08`, in a throwaway home directory `[verified: Arch]`.
The plugin was configured with `terminal = { provider = "none" }`.

| Check | Result |
|---|---|
| The plugin loads and starts its server without any terminal management | Works |
| Lock file | Written to `~/.claude/ide/<port>.lock` with mode 600 inside a directory with mode 700 |
| Lock file fields | `pid`, `workspaceFolders`, `ideName` (`Neovim`), `transport` (`ws`) and an `authToken` |
| Listening address | `127.0.0.1` only, on the port named in the lock file |
| Cleanup | The lock file is removed when Neovim exits |
| `claude --ide` | The flag exists in the installed CLI, it connects "if exactly one valid IDE is available" |

From the plugin documentation `[docs]`:

- The `none` provider creates no buffers and leaves launching and connecting the CLI to the user, with `claude --ide` or `/ide`.
- `:ClaudeCodeSendText` works only with the in-editor providers, so contextual prompts must send selection and `@file` references through the bridge, and not by typing into the pane.
- To move focus after a send, hook the `User ClaudeCodeSendComplete` event and select the tmux pane.

Consequences:

- Run the CLI with `claude --ide` in the tmux pane, since the editor opens no terminal.
- "Exactly one valid IDE" means that several Neovim instances in one workspace make auto-connect ambiguous.
  The layout therefore runs one Neovim per project session, and the design falls back to `/ide` when more than one matches.
- The server is a local listener on `127.0.0.1`, authenticated by the token in the lock file.
  It is separate from Remote Control and is covered in `docs/security.md`.

Not yet verified `[spike]`:

- That a real `claude --ide` session connects to this server, and that diff accept and reject work end to end.
  This needs a signed-in session and belongs to Phase 4.
