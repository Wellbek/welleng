# Well-Engineering verification map

This folder is the maintained source for verifying what Well-Engineering does for its user.
Read the index before driving, then use the matching feature file as the recipe.

## Baseline preconditions

- `claude` is signed in, and the `welleng@welleng-local` plugin is enabled and read from this repository.
  `welleng doctor --claude` shows the version sessions load.
- The opt-in status line script from `claude-plugin-hooks/hooks/statusline.py` is configured in the user's settings.
- Every live drive follows the Launch section of the skill's `SKILL.md`.

## Driving conventions

- Start every live recipe from a fresh throwaway project.
- Treat every command as literal.
- One feature per run id, so evidence folders stay readable.

## Proof

- Live proof is a pane capture that shows the action and its result.
- A feature that writes state is also proven by the file under `state/welleng/`.
- CLI proof is the command, its output and its exit code.
- Report an unreachable path with the attempted command and the unmet precondition.

## Features

- [Effort hint](effort-hint.md) covers the hint after a light prompt at high effort.
- [Status line](status-line.md) covers the model, effort, context and cost segment.
- [Mode skill](mode-skill.md) covers `/welleng:mode` loading, its goal and playbook header and the worker subagent.
- [Harness CLI](harness-cli.md) covers `welleng harness plan`, `apply` and `check` in a throwaway project.
