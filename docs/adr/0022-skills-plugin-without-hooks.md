# 0022 - The skills plugin carries no hooks

Status: Accepted
Date: 2026-11-28

## Context

People who do not use the terminal setup want the `/welleng:` skills on their own.
The single `welleng` plugin also carried six hook commands that run `python3` on every prompt, stop and subagent event.
On a machine without `python3`, or without the `welleng` command and status line, those hooks either fail or write state that nothing reads.
The skill prefix comes from the plugin name, so the skills must stay in a plugin called `welleng` `[docs]`.

## Options considered

- Keep one plugin and document the hooks as harmless, which leaves every skills-only user running hooks they cannot use.
- Copy the skills into `~/.claude/skills`, which drops the `welleng:` prefix and breaks every `/welleng:` cross-reference between skills.
- Split into two plugins in the same marketplace: `welleng` with the skills and subagents, `welleng-hooks` with every hook and the status line script.

## Decision

The `welleng` plugin holds skills and subagents only and never gains a hook, an MCP server or an LSP server.
Hooks live in the `welleng-hooks` plugin in `claude-plugin-hooks/`, which the full setup installs next to it.

## Consequences

- The skills install with `claude plugin marketplace add Wellbek/welleng` and `claude plugin install welleng@welleng-local`, without cloning or running anything else.
- An isolated install from a local clone loaded 24 skills, 2 subagents and no hooks on WSL2 Ubuntu.
  It is not labelled `[verified: Arch]`, and the install from GitHub has not been run.
- A test fails if `claude-plugin/` gains a `hooks` folder or a hook, MCP or LSP entry in its manifest.
- The status line path moved from `claude-plugin/hooks/statusline.py` to `claude-plugin-hooks/hooks/statusline.py`, so a status line configured with the old path must be updated by hand.
- Existing installs must add the second plugin with `claude plugin install welleng-hooks@welleng-local` after `claude plugin marketplace update welleng-local`, and `welleng doctor --claude` says so when it is missing.
- `/welleng:harness` keeps needing the `welleng` command, which installs with `uv tool install` from the `tools/` subdirectory.
