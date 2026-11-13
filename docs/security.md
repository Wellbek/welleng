# Security

This document describes how Well-Engineering handles secrets and remote access.
It is written before the features exist, so every statement about behaviour is a design rule or a claim from upstream documentation, tagged with the evidence tags from `docs/adr/README.md`.

## Principles

- No credential is ever stored in this repository, in a shell startup file or in an editor config.
- Credentials live in one mode-600 file outside any repository, see ADR 0009.
- A secret scanner runs before every commit and in CI, so a mistake is caught at the earliest point.
- Remote access is opt-in per session, never a standing internet-facing service.

## Credential classes

| Credential | Where it lives | Who may use it |
|---|---|---|
| Claude subscription login | Managed by the Claude Code CLI | Claude Code only, never handed to other tools |
| Third-party API keys | `~/.config/welleng/secrets.env`, mode 600 | Shell aliases and editor provider modules that read the file |
| SSH private keys | `~/.ssh`, never copied | OpenSSH and the ssh-agent |
| GitHub token | The `gh` credential store | `gh` and git |

On Windows the secrets file is protected with an NTFS ACL instead of `chmod`.
On WSL the file must be on the ext4 filesystem, because `chmod 600` has no effect under `/mnt/c`.

## Setting up credentials

Credentials are kept in one file, `~/.config/welleng/secrets.env`, with mode 600.
The format is `NAME=value`, one per line, with no `export`, no spaces around `=` and no quotes needed.

1. Run `scripts/init-secrets.sh`.
   It creates the file from `home/dot_config/welleng/secrets.env.example` with mode 600, never overwrites an existing file, and lists which variables are set without printing values.
2. Open the file and fill in only the variables you need.
3. Run `scripts/init-secrets.sh --status` at any time to see what is set.

| Variable | Needed | Used by |
|---|---|---|
| None | **Required** | Nothing in this project needs a credential file entry to work. Claude Code signs in with `claude` then `/login`, and GitHub with `gh auth login`, and neither stores anything here |
| `ZAI_API_KEY` | Optional | The `glm` shell function, which runs Claude Code against z.ai GLM models. Sessions started this way cannot use Remote Control |
| `ANTHROPIC_API_KEY` | Optional | Editor providers that use API keys, not Claude Code itself. Do not export it from shell startup files, it can take precedence over your subscription login |
| `OPENAI_API_KEY` | Optional | Optional editor providers |

How the values are read:

- `home/dot_config/welleng/shell/welleng.zsh` provides the helpers.
  Source it from `~/.zshrc` with `[[ -r ~/.config/welleng/shell/welleng.zsh ]] && source ~/.config/welleng/shell/welleng.zsh`.
- The helper parses the file, it never sources it, so nothing in the file can execute.
- A secret is read one name at a time, only when a command needs it, and is passed to that one process.
  Nothing is exported into your interactive shell.
- Set `WELLENG_SECRETS_FILE` to use a different location.

Until the chezmoi bootstrap exists, link the helper into place by hand:
`mkdir -p ~/.config/welleng/shell && ln -sfn "$PWD/home/dot_config/welleng/shell/welleng.zsh" ~/.config/welleng/shell/welleng.zsh`.

If a key was ever stored in a shell startup file, an editor config or a command line, treat it as exposed, revoke it at the provider and create a new one.
Also check places that keep copies, such as editor local history and shell or tool history files.

## Secret scanning

- `.githooks/pre-commit` runs `gitleaks` on staged changes, using `.gitleaks.toml`.
- `scripts/install-gitleaks.sh` installs a pinned, checksum-verified release into `~/.local/bin` without root, and CI installs the same version with the same script.
- When `gitleaks` is not installed, a built-in fallback scan of staged files runs instead, and it prints file names only so a secret is never echoed.
- The fallback is a safety net with a short pattern list, it does not replace `gitleaks`.
- CI runs the real scanner on every push and pull request.
- Enable the hook once per clone with `git config core.hooksPath .githooks`.

## If a secret is committed

1. Revoke and recreate the credential at the provider first, because anything pushed must be treated as public.
2. Remove it from the working tree and from history only after rotation.
3. Check whether the credential also appears in editor history, shell history and logs on the machines involved.

## Remote access

### Default: Claude Code Remote Control

The statements below come from the Claude Code documentation page "Continue local sessions from any device with Remote Control" `[docs]`.

- The local session makes outbound HTTPS requests only and never opens inbound ports.
- It registers with the Anthropic API and polls for work, and traffic is routed through the Anthropic API over TLS.
- Execution and filesystem access stay on the local machine.
- While connected, the session transcript is stored on Anthropic servers so devices stay in sync and the session can reconnect.
- It needs a claude.ai subscription login, API keys are not supported.
- It is unavailable when `ANTHROPIC_BASE_URL` points at a host other than `api.anthropic.com`, so sessions routed to another provider cannot be remote controlled.
- It is unavailable through Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry or an enterprise Claude apps gateway.
- It can be switched off with the `disableRemoteControl` setting, and organisations with Zero Data Retention or the HIPAA configuration cannot enable it.

Project defaults, which are design rules and not yet implemented:

- `remoteControlAtStartup` stays off, so a session is exposed only when you opt in, for example with `/rc`.
- Server mode uses `--spawn worktree` so parallel sessions do not share one working tree.
- Sessions started from a phone use the permission mode `default`, which asks, and never a bypass mode.

Approvals from a phone `[docs]`:

- Permission prompts and questions stay open until you answer them, they do not time out.
- A session can be started with `--permission-mode` in server mode, so the project default of `default` is enforceable and does not rely on a setting in each project.
- A phone can change the model and the effort level of the running session, which the effort hint feature treats as an ordinary change, so an accepted hint is recognised from either device.
- Commands that only make sense in a terminal, such as `/plugin` and `/resume`, stay local-only.
- Push notifications for permission prompts are optional and are enabled in `/config`.

`[spike]` The "no inbound ports" claim is documented upstream, but it is not yet verified on a real machine.
Acceptance test 9b will compare listening ports before and after enabling Remote Control.

### The editor bridge is a local listener

This is separate from Remote Control, and it does open a port.
The claudecode.nvim bridge starts a WebSocket server inside Neovim `[verified: Arch]`.

- It listens on `127.0.0.1` only, so it is not reachable from the network.
- Connections must present the token from the lock file, which is `~/.claude/ide/<port>.lock` with mode 600 inside a directory with mode 700.
- The lock file is removed when Neovim exits.
- Any process running as the same user can read the lock file, so the bridge protects against other users and other machines, not against malware running as you.

Acceptance test 9b therefore filters by process, so that the Neovim listener is not mistaken for a Remote Control listener.

### Optional: Tailscale, SSH and tmux

For attaching to real tmux panes from a phone SSH client.
It is off by default because it duplicates Remote Control for most uses.

- No public ports: the machine joins a tailnet and SSH is reachable only on that network.
- Authentication is Tailscale device identity plus SSH keys, with password login disabled.
- Traffic is encrypted by WireGuard.

### Rejected

Web terminals such as ttyd, gotty and code-server exposed through port forwarding or a tunnel.
They create a standing internet-facing shell, which this project does not accept.

## Threat summary

| Question | Answer |
|---|---|
| What is exposed? | Only the Claude sessions you opted in |
| Are inbound ports opened? | None expected `[docs]`, to be verified `[spike]` |
| Who can reach a session? | Only the account signed in to Claude on both ends |
| What if the phone is lost? | Revoke the session from claude.ai and sign the phone out, no local rotation needed |
| What can the phone do? | Whatever the session's permission mode allows, so the default mode keeps approvals interactive |
| What is not covered? | Plain terminal access, Neovim and other tools, which stay local |
| What does the transcript leak? | Messages, responses and tool activity are stored by Anthropic while connected `[docs]` |

## Limits

- Reaching a session from a phone needs the laptop awake and online.
- Remote Control approvals depend on the session running in a mode that prompts, which the manual verification procedure checks.
- None of this protects a machine that is already compromised.
