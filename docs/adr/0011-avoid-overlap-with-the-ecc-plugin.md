# 0011 - Avoid overlap with the ecc plugin

Status: Accepted
Date: 2026-11-13

## Context

The `ecc` Claude Code plugin is already installed on the maintainer's machine `[verified: Arch]`.
It provides commands such as `/project-init`, `/model-route`, `configure-ecc` and `harness-audit`, a `token-budget-advisor` skill and a `GateGuard` hook that gates the first Bash and first file write of a session.
Parts of that overlap with the harness, model-hint and monitoring work in this project.

## Options considered

- Build everything here and ignore `ecc`: duplicate behaviour and conflicting hooks.
- Depend on `ecc` for everything: ties this project to a third-party plugin.
- Keep the non-conflicting parts of `ecc` and disable or avoid the conflicting ones.

## Decision

Where an `ecc` feature conflicts with a feature of this project, `ecc` is disabled or not used, and this project's version wins.
Non-conflicting `ecc` features stay.
Nothing in this repository may require `ecc` to be installed.

## Spike result

The spike read the plugin source, version 2.2.3, on the maintainer's machine `[verified: Arch]`.
A feature counts as a conflict when it meets at least one of these tests:

1. It duplicates a planned feature of this project.
2. It owns settings, state, tmux sessions or files that this project manages.
3. It adds gating friction, or per-edit work that `/harness` configures per project.

The full list, with a reason for each entry, is the machine-readable file `home/dot_config/welleng/ecc-overrides.json`.
In summary, 18 hooks and 18 commands and skills are disabled:

| Group | Disabled |
|---|---|
| Gating friction | the three GateGuard hooks and the `gateguard` skill, `config-protection`, `safety-guard`, `delivery-gate` |
| Harness overlap | `project-init`, `configure-ecc`, `harness-audit`, `agent-sort`, `workspace-surface-audit`, `config-gc`, the `hookify` family, and the global format, lint and typecheck hooks |
| Monitoring and cost | the cost tracker hooks, the metrics bridge, the context monitor, the session activity tracker, `cost-tracking`, `cost-report`, `dmux-workflows` |
| Safety and state | `auto-tmux-dev`, `command-log-audit` |
| Model hints | `model-route` |

Kept, because they do not conflict:

- `block-no-verify`, which protects this project's pre-commit hook from `--no-verify`.
- The session start and end hooks, continuous learning, the MCP health check, the pull request and build notices, and desktop notifications.
- `token-budget-advisor`, which controls answer length and not model choice, so it overlaps nothing.
- All language reviewers, build resolvers and pattern skills.

Findings worth knowing:

- `auto-tmux-dev` kills any existing tmux session whose name matches the project directory, which can destroy a welleng session.
- `command-log-audit` writes every Bash command to a log and redacts only `--token`, so an inline `NAME=secret` assignment would be stored in plain text.
- `model-route` is a three-line static heuristic with no signals, so there is nothing to reuse, and the scorer in ADR 0008 stands alone.

## Consequences

`scripts/apply-ecc-overrides.py` merges the list into the user's Claude Code settings.
It sets `env.ECC_DISABLED_HOOKS` and adds one `Skill(skill:ecc:<name>)` deny rule per skill.
It is idempotent, preserves every other key, and the bootstrap runs it after each plugin update, because a plugin update can add hooks or rename ids.
Nothing in this repository requires `ecc` to be installed.
The project's own hooks stay few and fast, so they do not add the friction that gating hooks cause.

Not yet verified `[spike]`:

- Whether a `Skill` deny rule also stops the user typing the slash command, or only model invocation.
- That the disabled hook ids take effect in a fresh session.
  The first session after applying the overrides confirms this, and the result belongs in `CHECKLIST.md`.
