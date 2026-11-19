# Claude Code

Well-Engineering works with Claude Code only through its official interfaces: the CLI JSON output, hooks, the status line, settings and plugins.
It never parses files under `~/.claude/`, see [ADR 0005](../adr/0005-official-claude-code-interfaces-only.md).

Verification status: the plugin validates, its hooks ran headless on Claude Code 2.1.325, and effort hints, the status line and the state writer ran in a live interactive session on Claude Code 2.1.328, all on Arch.
The `/welleng:mode` skill and the `welleng:worker` subagent ran headless on 2.1.328 on Arch.
The `/harness` questionnaire ran in a live interactive session on 2.1.328 on Arch.
The editor bridge has not been verified interactively, see [docs/verification/interactive.md](../verification/interactive.md).

## Install the plugin

The repository is also a plugin marketplace named `welleng-local`.

```sh
claude plugin marketplace add <path to the repository>
claude plugin install welleng@welleng-local
claude plugin list
```

The `/harness` skill needs the `welleng` command on `PATH`, see [installation](installation.md#3-install-the-welleng-command).
Validate the plugin yourself with `claude plugin validate claude-plugin`.

The plugin contains:

| Part | What it does |
|---|---|
| `/harness` skill | Questionnaire that sets up a project's Claude Code configuration |
| `/welleng:mode` and the workflow skills | Playbooks, principles and subagent roles for rigorous engineering work, see [the workflow guide](workflow.md) |
| `welleng:worker` and `welleng:comment-reviewer` subagents | Delegates that carry the Well-Engineering rules, used by the workflow skills |
| `SessionStart` hook | Suggests `/harness` once in a git repository that has no `CLAUDE.md` and no `.claude/settings.json` |
| `UserPromptSubmit` hook | Effort hints |
| State writer hooks | Record per-session model, effort and subagents for the dashboard |

All hooks print nothing except one JSON object when they have something to say, and never raise, so they cannot disturb a session.
Each runs as a direct `python3 -I` call, not through your shell.

## The harness skill

Run `/harness` in a project.
It asks one short question at a time and accepts `-`, `skip` or `s` to skip.
It never writes anything before you have seen a plan with diffs and said yes.
It never asks for or writes a credential: for a service it asks for the name of the environment variable and writes a `${NAME}` reference.

Questions, asked only where they apply:

1. Coding conventions to always follow.
2. A formatter or linter to run after every edit.
3. A command that must pass before finishing.
4. Files that must never be read or changed.
5. Actions that need confirmation first.
6. A database or service the agent should query.
7. Rules that only apply to some paths.

The skill writes its answers as a spec, and the `welleng` CLI does the work.
You can drive the CLI yourself without the skill:

```sh
welleng harness plan spec.json      # shows diffs, writes nothing
welleng harness apply spec.json --yes
welleng harness check               # validates the existing configuration
```

Spec format:

```json
{"intents": [
  {"kind": "claude_md", "name": "conventions", "text": "Use type hints.\nRun tests before finishing."},
  {"kind": "rule_file", "name": "tests", "paths": ["tests/**"], "text": "Tests use pytest."},
  {"kind": "deny", "rules": ["Read(**/.env)"]},
  {"kind": "ask", "rules": ["Bash(git push:*)"]},
  {"kind": "hook", "event": "PostToolUse", "matcher": "Edit|Write", "command": "ruff format ."},
  {"kind": "mcp", "name": "db", "config": {"command": "db-mcp", "env": {"URL": "${DB_URL}"}}},
  {"kind": "local_setting", "key": "model", "value": "sonnet"}
]}
```

| Kind | Written to |
|---|---|
| `claude_md` | A delimited block in `CLAUDE.md` |
| `rule_file` | `.claude/rules/NAME.md`, with a `paths` list when given |
| `deny`, `ask` | `permissions` in `.claude/settings.json` |
| `hook` | `hooks` in `.claude/settings.json` |
| `mcp` | `.mcp.json` |
| `local_setting` | `.claude/settings.local.json`, for personal preferences |

Safety properties, all covered by unit tests on Arch:

- Existing JSON and Markdown are preserved, generated Markdown lives in `<!-- welleng:begin NAME -->` blocks that a rerun replaces, and a rerun changes nothing.
- Invalid JSON is never overwritten.
- A credential-like string, or an MCP `env` value that is not a `${NAME}` reference, is refused.
- `apply` needs `--yes`.
- `check` flags empty files, credential-like strings, invalid JSON and hook commands that do not exist or are not executable.
  It does not run the hooks.

## Session state and the dashboard

`welleng agents` joins the official `claude agents --json` output with small state files that the plugin's hooks write, one per live session, see [ADR 0018](../adr/0018-per-session-state-files.md).

- Files: `~/.local/state/welleng/sessions/<session id>.json`, mode 600.
- Contents: working directory, last event, permission mode, model, effort level, context percentage, cost and the ids of active subagents.
- Never stored: prompt text, assistant messages, the transcript path.
- A session file is deleted when the session ends, and files older than seven days are pruned.

The hooks alone give model, effort and subagent count.
Context use and cost come only from the status line, which the plugin does not set because it would replace yours.
To opt in, put this in your own Claude Code settings, with the real path:

```json
"statusLine": {"type": "command", "command": "python3 -I /path/to/welleng/claude-plugin/hooks/statusline.py"}
```

It prints a compact line such as `model | high | ctx 42% | $1.23` and records the same values.
If you already have a status line, call `statusline.py` from your own script instead.

Tested with synthetic events in subprocess tests on Arch.
No live session has produced these files yet.

Waiting for input is always taken from `claude agents --json`, because notification hooks fire late.
The tmux status line shows `waiting:N` through `welleng agents --count`, see [configuration](configuration.md#tmux).

## Effort hints

The `UserPromptSubmit` hook gives a quiet, local recommendation when your current `/effort` level is far from what the prompt looks like, see [ADR 0013](../adr/0013-effort-only-hints.md).

- A small keyword and length scorer classifies the prompt as light, standard or heavy.
  No model call, no network.
- It recommends `low`, `medium` or `high`.
- A hint appears only when the recommendation is two or more levels away from your current level, confidence is at least 0.6, and the last hint was more than 30 minutes ago.
- The hint is a message shown to you only, which the hooks documentation says does not enter the model context `[docs]`.
  It never changes anything for you.
- Including `ultrathink` in a prompt suppresses the hint.

Controls:

```sh
welleng hints snooze --hours 8
welleng hints off
welleng hints on
welleng hints report
```

The log in `~/.local/state/welleng/hints.log` holds the estimate and the levels only, never the prompt text.
`welleng hints report` also counts prompts that arrived without an effort level.
Claude Code 2.1.328 sends the prompt event without an effort level, so the hook reads the level that the status line script recorded for the session, see [ADR 0021](../adr/0021-effort-level-from-the-status-line-state.md).
Hints therefore need the opt-in status line from the section above, and without it they stay silent.
In a live interactive session on Arch, a light prompt at `high` effort showed `hint: this looks light, consider /effort low (now high)` under the prompt, and a second light prompt within 30 minutes stayed silent `[verified: Arch]`.
The keyword lists are a first guess to tune from the log.

## Editor bridge

Claude Code runs in a tmux pane and Neovim connects through claudecode.nvim, see [ADR 0010](../adr/0010-claude-in-a-tmux-pane-with-an-editor-bridge.md).

1. Open Neovim with the project configuration: `NVIM_APPNAME=welleng-nvim nvim`.
2. In a tmux pane in the same project, start `claude --ide`.
   Several Neovim instances in one workspace make the auto-connect ambiguous, use `/ide` to choose.
3. Use the keys below.

| Key | Mode | Action |
|---|---|---|
| `<leader>as` | visual | Send the selection to Claude |
| `<leader>ab` | normal | Add the current buffer as an `@file` reference |
| `<leader>aa` | normal | Accept the diff Claude proposes |
| `<leader>ad` | normal | Reject the diff |
| `<leader>ae` | normal, visual | Attach the buffer or selection and type "explain" |
| `<leader>af` | normal, visual | Same, with "find and fix the bug" |
| `<leader>at` | normal, visual | Same, with "write tests" |
| `<leader>ar` | normal, visual | Same, with "review" |

The four contextual keys type their instruction into the Claude pane and move focus there, but never press Enter, so you read and send it yourself, see [ADR 0019](../adr/0019-contextual-prompts-typed-through-tmux.md).
The pane is the first other pane in the window running `claude` or a bare version number.
Pin a pane with `vim.g.welleng_claude_pane = "%3"` if detection picks the wrong one.
With no Claude pane found, the instruction goes to the clipboard.
The keys and the pane matching are tested in a container, the full flow with a live session is not.

## glm

`glm` runs Claude Code against z.ai GLM models.
It needs `ZAI_API_KEY` in `~/.config/welleng/secrets.env`.
The key is read on demand and passed only to that one process.
Remote Control does not work in `glm` sessions.

## Global instructions

`~/.config/welleng/claude/CLAUDE.md` holds general agent rules: safety, an autonomy policy, working style, writing conventions and a pointer to `/welleng:mode`.
To use it, add this line to your own `~/.claude/CLAUDE.md`:

```
@~/.config/welleng/claude/CLAUDE.md
```

Nothing replaces your file.
A live session on Claude Code 2.1.328 loaded it through that import line `[verified: Arch]`.

## The ecc plugin

If you use the `ecc` plugin, some of its hooks conflict with this project, for example gating every first write and duplicating cost tracking, see [ADR 0011](../adr/0011-avoid-overlap-with-the-ecc-plugin.md).

```sh
python3 scripts/apply-ecc-overrides.py --dry-run
python3 scripts/apply-ecc-overrides.py
```

It disables the listed features in your Claude Code settings, keeps every other key, and is idempotent.
The list also disables seven `ecc` skills that duplicate the workflow layer, such as `tdd-workflow` and `santa-method`, see [ADR 0020](../adr/0020-workflow-layer-adapted-from-pstack.md).
