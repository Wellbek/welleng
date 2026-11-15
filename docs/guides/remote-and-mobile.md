# Remote machines and mobile

## The machine registry

The OpenSSH config is the registry, see [ADR 0007](../adr/0007-openssh-config-as-machine-registry.md).
A host added here works with plain `ssh NAME` and with every other tool, with or without this project.
Hosts, addresses and usernames stay on your machine and are never tracked in this repository.

```sh
welleng ssh add devbox dev.example.org --user me --port 2222 --identity ~/.ssh/id_ed25519 --jump gate --description "build box"
welleng ssh ls
welleng ssh rm devbox
```

- Each host becomes one file, `~/.ssh/config.d/NAME.conf`, with mode 600 and a `# managed by welleng` first line.
- `ls` shows both managed hosts and hand-written ones from `~/.ssh/config`, marked `welleng` or `manual`.
- Hand-written entries are listed but never modified or removed.
  `rm` refuses any file it did not create.
- `--identity` stores only the path to a key, never the key.
- Names, hosts, users and paths are validated, so a newline, quote, space or comment cannot inject extra config lines.
- Adding a name that already exists is refused.
- There is no `edit` command: remove the host and add it again.

### One-time Include migration

OpenSSH only reads `~/.ssh/config.d/` if the main config includes it.
Preview, then apply:

```sh
welleng ssh migrate           # shows what would change
welleng ssh migrate --yes     # adds "Include config.d/*.conf" at the very top
welleng ssh migrate --undo --yes
```

- The line goes first because an `Include` inside a `Host` or `Match` block would only apply to that block.
- The previous file is kept as `config.welleng-backup`, and the new file has mode 600.
- It is idempotent and recognises an existing include.
- A symlinked config is followed, so the target is edited and the link stays.
- `--undo` removes exactly the block that was added.
- Tested on Arch with temporary directories, including a real `ssh -G` comparison before and after.
  It has not been run against your real `~/.ssh`.
  Run the dry run first.

## Remote Control from a phone

Remote Control lets the Claude app on a phone drive a session on your machine.
It is outbound-only according to the documentation `[docs]`, and this project checks that on your machine.

```sh
welleng rc --ports snapshot     # record listening sockets
welleng rc --name myproject     # inside tmux: starts Remote Control in a window named rc
welleng rc --ports diff         # compare
```

- `rc` starts `claude remote-control --permission-mode default` in a detached tmux window.
  It refuses `bypassPermissions` on purpose.
- The diff reports new loopback listeners as information, and any new listener on a non-loopback address as `NEW EXPOSED LISTENER` with exit code 1.
- The port check needs Linux with `ss`.
- Sessions started through `glm` cannot use Remote Control.
- Keep permission prompts on.
  Approvals are the safety boundary, see [security](../security.md).

Status: the tmux command and the port check are tested on Arch, and a live port snapshot and diff ran on the real machine.
No phone has ever connected.
Run the procedure in [docs/verification/phone.md](../verification/phone.md) before relying on it, and record the result in `CHECKLIST.md`.
