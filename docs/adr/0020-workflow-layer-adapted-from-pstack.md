# 0020 - Workflow layer adapted from pstack

Status: Accepted
Date: 2026-11-19

## Context

Well-Engineering installs and connects the tools, but it says little about how an agent should work once a session starts.
The global instructions hold about ten lines of style and safety rules, and rules such as "reproduce a bug first" exist only as prose.
The `ecc` plugin offers hundreds of skills, which is breadth without one entry point.

pstack, an MIT-licensed plugin by Lauren Tan in the `cursor/plugins` repository, is a workflow layer: one entry skill, 22 playbooks, 24 principles, two subagents and about 30 standalone skills `[docs]`.
It is written for Cursor first, and its Claude Code support maps Cursor names at run time through an adapter file `[docs]`.
Several of its skills read Claude Code transcripts under `~/.claude/projects/`, which ADR 0005 forbids `[docs]`.
Four of its files contain the em dash character, which `scripts/check-hygiene.sh` rejects `[verified: Arch]`.

The studied upstream commit is `35a90942a7f02e1ebbc2443643179815f2147954`.

## Options considered

- Install upstream pstack and keep an overrides list, as ADR 0011 does for `ecc`: automatic updates, but another person's preferences, a run-time adapter, transcript reads and 53 menu entries.
- Copy pstack into the repository unchanged: fails the hygiene check and the house style, and the copy goes stale.
- Port every skill natively: no adapter, but principle skills clutter the menu and several playbooks have no use here yet.
- Port a curated set natively, in this project's voice, with Claude Code names and the existing rules built in.

## Decision

Port a curated set of pstack into the `welleng` plugin as native skills, and keep upstream as a reference, not a dependency.

- `/welleng:mode` is the single entry point.
  It holds the non-negotiables, the principles index, the routing to playbooks and the role table.
- The 24 principles are reference files under `skills/mode/principles/`, not skills, so they add no menu entries.
- 17 playbooks live under `skills/mode/playbooks/`.
- Standalone skills are user-invoked only through `disable-model-invocation: true`, so their descriptions cost no context until used `[docs]`.
  The mode skill reaches them by reading their files.
- The `welleng:worker` subagent carries the hard rules into every delegate.
- Roles map to a model and an effort level for subagents.
  ADR 0013 still governs the prompt hints, which recommend effort only.
- Nothing reads transcripts.
  Skills that relied on them use git history, review threads, the current conversation, or `claude -p --output-format stream-json` output, which is an official interface.
- Nothing in this repository requires pstack to be installed.

Excluded: `setup-pstack`, `automate-me`, `recall`, `ketchup-video`, `make-bot-ui`, the Cursor-only automations, `typescript-best-practices`, the formal verification and statechart skills, `poteto-help`, and the autopilot playbooks.
Running upstream pstack next to this layer is not supported, because the two would give conflicting instructions.

## Consequences

- `scripts/check-skills.py` enforces the structure: frontmatter, resolvable references, no Cursor names, no transcript paths, one sentence per line.
  It runs in the hygiene check, so the pre-commit hook and CI both run it.
- `claude-plugin/THIRD_PARTY_NOTICES.md` carries the MIT notice and the list of adapted files.
- `scripts/pstack-upstream-diff.py` lists upstream changes since the studied commit, so improvements are taken on purpose.
- `ecc` skills that duplicate a ported skill are disabled through `home/dot_config/welleng/ecc-overrides.json`, using the three tests of ADR 0011.
- Whether a skill changes agent behaviour can only be shown in a live session.
  Until then each skill is "implemented, verification pending" in `CHECKLIST.md`.
- Fan-out skills (`interrogate`, `swarm`, `arena`) multiply token use by the number of agents, and say so before they start.
