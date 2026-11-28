# Well-Engineering - agent instructions

Well-Engineering is a cross-platform terminal and AI-native development environment, installed with chezmoi and driven by a small `welleng` CLI.
The project is in a pre-implementation phase.
Read `README.md` for the architecture and `docs/adr/` for the reasons behind each decision before changing anything structural.

## Hard rules

- Never print, copy, log or commit a credential.
  Credentials live in `~/.config/welleng/secrets.env` with mode 600, outside any repository.
- Never install packages, modify files under `$HOME`, or change a machine's configuration unless the maintainer has explicitly approved that action in the current conversation.
- Never track host names, IP addresses, usernames, SSH fragments or `secrets.env`.
- Never use the em dash character in any file.
  Use a plain dash.
- Never edit `CHANGELOG.md` by hand or any file marked as auto-generated.
- Never mention an AI assistant, an agent session or co-authorship in commit messages, pull requests or files.

## Truthfulness about verification

- Anything verified only on the maintainer's Arch Linux machine must be labelled as such.
- Use the evidence tags defined in `docs/adr/README.md`: `[verified: Arch]`, `[docs]`, `[search]`, `[spike]`.
- Never claim a feature is tested on a platform where it was not run.
  Container runs are labelled "tested in container", and WSL2 is never called verified without a WSL2 run.
- Record test results in `CHECKLIST.md` together with the platform they ran on.

## Conventions

- Write Markdown with one full sentence per line.
- Record each significant decision as a new numbered file in `docs/adr/`, and supersede old records instead of editing history.
- Official Claude Code interfaces only: CLI JSON output, hooks, the status line, settings and plugins.
  Never parse files under `~/.claude/`.
- Shell scripts use `bash` with `set -euo pipefail`, quote every expansion, and stay idempotent.
- Custom tooling is Python 3.11+, run through `uv`.
- Prefer quality, simplicity and long-term maintainability over development cost.
- Use `/welleng:mode` for non-trivial work in this repository, and `verify-welleng` to prove a change to the plugin, its hooks or the CLI.
- Run `python3 -I scripts/check-skills.py` after editing a skill, and keep `claude-plugin/pstack-upstream.json` in step with adapted files.

## Git

- One concern per commit, with a Conventional Commits style subject such as `feat:`, `fix:`, `docs:`, `chore:` or `ci:`.
- Enable the hooks once per clone with `git config core.hooksPath .githooks`.
- Run `scripts/check-hygiene.sh` before pushing.
- Run `scripts/regression.sh --strict` after every significant change, it needs Docker for the container stages.
- Local planning notes live in `docs/architecture.md` and `docs/research/`, both gitignored.
  Do not commit them.

## Layout

Existing today:

- `docs/adr/` decision records, `docs/security.md`, `docs/platforms.md`
- `scripts/` repository hygiene, secret scanning, `install-gitleaks.sh`, `check-packages.py`, `init-secrets.sh`, `phone-ssh.sh`, `enable-statusline.py`, `apply-ecc-overrides.py`, `check-skills.py`, `check-commit-msg.sh` and `pstack-upstream-diff.py`
- `.githooks/` pre-commit and commit-msg gates
- `packages/packages.toml` the package map, checked against pacman, apt and dnf in CI
- `bootstrap/` installer and pinned releases, `claude-plugin/` the `welleng` plugin with `/welleng:harness`, `/welleng:mode`, the workflow skills and the `worker` and `comment-reviewer` subagents and no hooks, `claude-plugin-hooks/` the `welleng-hooks` plugin with every hook and the status line script, `tools/` the `welleng` Python package
- `.chezmoiroot` and `home/` the chezmoi source state: tmux and git config, the tpm external, `dot_config/welleng/` (credentials example, shell helpers, starship, lazygit, kitty, yazi, global Claude instructions, tmux segment, `ecc` overrides), `dot_config/welleng-nvim/`, and the Windows-only `Documents/PowerShell/` and `dot_config/wezterm/`
- `scripts/wire-in.sh`, `scripts/uninstall.sh`, `docs/verification/` and `docs/troubleshooting.md`
- `.claude/skills/verify-welleng/` the project verification skill, which drives a live Claude Code session on a private tmux server

Planned, not created yet:

- everything in `docs/verification/` that needs a device, and a live check of the editor bridge
