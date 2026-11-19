# Mode skill

`/welleng:mode` loads the workflow layer: the reply opens with the goal and the chosen playbook, and delegates run as `welleng:worker`.

## Sub-features

- `mode-visibility` keeps the user-invoked skills out of the model's skill list, only `welleng:harness` is visible.
- `mode-header` opens the first reply with `Goal:` and `Playbook:` after reading the playbook file.
- `mode-worker` spawns `welleng:worker` with the requested model and effort.

## How to get to it (user POV)

- Type `/welleng:mode <task>` in a session.

## Driving it with claude -p

This feature is driven headless, which costs less and records every tool call through the official stream output.
Run each command from the repository root.

Preconditions:

- `claude` is signed in.

- **Visibility.**
  Run `claude -p "Without using any tools, list the names of every skill in your available-skills list whose name starts with 'welleng:'. Output only the names, one per line, or the word NONE." --model sonnet --max-turns 2`.
  The output is `welleng:harness` only.
- **Header.**
  Run `claude -p "/welleng:mode What does scripts/check-hygiene.sh check? Keep the answer short." --model sonnet --max-turns 20 --allowedTools "Read Grep Glob" --output-format stream-json --verbose > "$EV/mode.ndjson"`.
  The first `tool_use` reads `claude-plugin/skills/mode/playbooks/investigation.md`, and the first text block starts with `Goal:` and has a `Playbook: investigation` line.
- **Worker.**
  Run `claude -p "Spawn one subagent with the Agent tool, subagent_type 'welleng:worker', model 'haiku', effort 'low'. Its brief: 'Count the .md files in claude-plugin/skills/mode/principles with the Glob tool and report only the number, and quote the first heading of your own instructions.' Then output exactly what the subagent reported." --model sonnet --max-turns 10 --allowedTools "Read Grep Glob Agent" --output-format stream-json --verbose > "$EV/worker.ndjson"`.
  The `Agent` call has `subagent_type` `welleng:worker`, and the result is `24` and `# Worker`.

## Gotchas

- `claude plugin details` counts user-invoked skills as always-on context, so its estimate is an upper bound.
- A sign-in that is about to expire prints a warning on stderr, which is not a failure.
