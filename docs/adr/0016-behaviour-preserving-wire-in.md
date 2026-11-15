# 0016 - Wiring into an existing setup must preserve behaviour

Status: Accepted
Date: 2026-11-15

## Context

The maintainer already has a working zsh, tmux and OpenSSH setup.
Connecting this project to it must not change how that setup behaves, and the maintainer asked for that to be proven in an isolated container before anything touches the real home directory.

## Decision

`scripts/wire-in.sh` adds one delimited block to each of `~/.zshrc`, `~/.tmux.conf` and `~/.ssh/config`, backs each file up once, is idempotent, and `--undo` restores the original bytes.
The Include block goes at the top of the SSH config, the zsh and tmux blocks at the end.
`tests/e2e/wire-in.sh` runs it in an Arch container against a copy of the real files, and compares before and after: `ssh -G` for every host, the tmux prefix and errors and status line, the zsh exit status, error output, aliases, parameters, exports, key bindings, prompt and hook lists.
Only chezmoi's `~/.config/welleng` directory is deployed, never the whole source state.

## Findings from the first real run

- The test failed on the first full run `[verified: Arch]`.
  With starship installed but not configured in the maintainer's zshrc, sourcing `init.zsh` changed the prompt and `FZF_DEFAULT_COMMAND`.
  The visible integrations moved behind `WELLENG_SHELL_EXTRAS=1`, see ADR 0015, and the test passes without them.
- In a headless `claude -p` session the `UserPromptSubmit` hook input carried no `effort` field, even with `--effort high` `[verified: Arch]`, Claude Code 2.1.325.
  ADR 0012 expected `effort.level` in the common input, so that expectation is not confirmed.
  The hint hook stays silent without it, and `welleng hints report` counts the prompts that arrived without an effort level.
  Whether interactive sessions include the field is still open `[spike]`.
- The `SessionStart` hook of the plugin ran in a live headless session, produced the expected JSON and exited 0 `[verified: Arch]`.

## Consequences

Any future change to what the wiring adds must pass the same before and after comparison.
The comparison only sees what a non-interactive `zsh -i -c` and a bare tmux server show, so it cannot prove that an interactive session looks identical.
