# 0011 - Avoid overlap with the ecc plugin

Status: Accepted, details pending a spike
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

## Consequences

Phase 0 reads the relevant `ecc` commands and hooks, then records exactly which are disabled.
If `ecc:model-route` already provides complexity scoring, this project adds only the status line delivery and cooldown logic around it.
The project's own hooks stay few and fast, so they do not add the friction that gating hooks cause.
