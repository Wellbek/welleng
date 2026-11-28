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

## Working from a phone

There are two ways in, and both work from an iPhone and from Android.

| Way | What the phone gets | Needs on the machine | Needs on the phone |
|---|---|---|---|
| A. Remote Control | The Claude conversation of one session: prompts, answers, permission approvals | Nothing new, Claude Code signed in with a claude.ai plan | The Claude app |
| B. Tailscale SSH and tmux | The whole terminal: the same tmux session, Claude, the shell, Neovim | Tailscale, see `scripts/phone-ssh.sh` | The Tailscale app and an SSH client |

Start with A.
Use B when you need the shell itself or want to see the exact panes you left.

The machine must stay awake and online in both cases.
On WSL2 that means Windows must not sleep, so set "When plugged in, put my device to sleep" to "Never" in the Windows power settings while you work remotely.

### A. Remote Control

Requirements `[docs]`: a Pro, Max, Ultra, Team or Enterprise plan, Claude Code signed in with `/login` and not with an API key, and no custom `ANTHROPIC_BASE_URL`.
On Team and Enterprise an Owner must first enable Remote Control in the admin settings.
Sessions started through `glm` cannot be remote controlled.

On the phone, once:

| Step | iPhone | Android |
|---|---|---|
| Install the app | "Claude" by Anthropic from the App Store | "Claude" by Anthropic from Google Play |
| Sign in | The same account as Claude Code on the machine | The same account as Claude Code on the machine |
| Allow notifications | Accept the prompt, or Settings, Claude, Notifications | Accept the prompt, or Settings, Apps, Claude, Notifications |

Without the app at hand, run `/mobile` in Claude Code for a QR code that leads to it.

To continue the session you are in right now:

1. In that session, type `/remote-control`, or `/rc` for short, optionally with a title such as `/rc welleng`.
   The first time, confirm the "Enable Remote Control" dialog.
   The conversation so far comes along.
2. A URL and a QR code appear.
   Scan the QR code with the phone camera, or open the Claude app, tap **Code**, and pick the session with the computer icon and the green dot.
3. Type prompts on the phone as you would in the terminal.
   Permission requests show up on the phone and wait until you answer, they do not time out.
4. For a push when Claude needs you, run `/config` on the machine and turn on **Push when actions required**.
5. To stop, run `/remote-control` again and choose disconnect.
   The terminal session keeps running.

To start a fresh session meant for the phone, run `welleng rc --name myproject` inside tmux.
It starts `claude remote-control --permission-mode default` in a background window named `rc`, so the session survives a closed terminal, and it refuses `bypassPermissions`.
`claude --rc "My Project"` does the same for one interactive session without the tmux window.

Good to know `[docs]`:

- Only one device is connected to a session at a time, a second one takes it over.
- After a network drop or sleep the session reconnects when the machine is back.
- After `claude remote-control` stops, its sessions can be resumed for about four hours with `claude remote-control --continue`.
- Terminal-only commands such as `/plugin` and `/resume` do not work from the phone.
- `remoteControlAtStartup` stays off in this project, so a session is reachable only after you type `/rc`.

The local machine makes outbound connections only `[docs]`.
Check it yourself, before and after starting Remote Control:

```sh
welleng rc --ports snapshot     # record listening sockets
welleng rc --ports diff         # compare, exit code 1 on any new non-loopback listener
```

The port check needs Linux with `ss`.
Keep permission prompts on, approvals are the safety boundary, see [security](../security.md).

### B. Tailscale SSH into tmux

Tailscale puts the machine and the phone in one private network, the tailnet.
Tailscale SSH answers on that network only, needs no OpenSSH server, and signs you in with your Tailscale account instead of keys or passwords `[docs]`, see [ADR 0023](../adr/0023-tailscale-ssh-for-phone-terminal-access.md).

On the machine, once:

```sh
scripts/phone-ssh.sh                 # status, changes nothing
scripts/phone-ssh.sh install         # prints the install commands and starts nothing
scripts/phone-ssh.sh install --yes
scripts/phone-ssh.sh on --yes        # sign in through the printed URL, then enable Tailscale SSH
scripts/phone-ssh.sh                 # shows the line to type on the phone, such as ssh you@laptop.tailnet-name.ts.net
```

- `install` uses the Arch package, or on Ubuntu and Debian adds Tailscale's own apt repository the way Tailscale documents it, without piping a script into `sh`.
  On other distributions it points to the official instructions, rerun `install` afterwards to start the service.
- On WSL2, `tailscaled` needs systemd, enable it with `[boot] systemd=true` in `/etc/wsl.conf` and `wsl --shutdown` in Windows.
  The status line of the script tells you whether that is needed.
- On WSL2, run Tailscale inside WSL2 and not also on the Windows host, because running both breaks traffic `[docs]`.
  Tailscale SSH has no server on Windows, so for this route Tailscale belongs inside WSL2.
- The new machine may appear under a duplicate name, rename it on the Machines page of the Tailscale admin console.

On the phone, once:

| Step | iPhone | Android |
|---|---|---|
| Join the tailnet | Install "Tailscale" from the App Store, sign in with the same account, allow the VPN profile | Install "Tailscale" from Google Play, sign in with the same account, allow the VPN connection |
| Install an SSH client | Termius or Blink Shell | Termius, or Termux and then `pkg install openssh` |
| Add the host | Host: the MagicDNS name from `phone-ssh.sh`, user: your Linux user, port 22, no key and no password | Same |

Each time:

1. Turn Tailscale on in its app.
2. Connect to the host in the SSH client.
   With the default tailnet policy, the first connection in each 12 hours prints a sign-in URL, open it on the phone and confirm `[docs]`.
3. Attach to the exact console you left: `tmux ls` lists the sessions, `tmux attach -t welleng` joins one, or `welleng up` in a project.
   Your laptop and your phone now see the same panes, and typing on either shows up on both.
   Since tmux 3.1 the window takes the size of the screen you typed on last, so it fits the phone while you use it, and `tmux attach -d -t welleng` detaches the laptop instead.
4. Detach with the prefix and then `d`.
   The prefix in this setup is `Alt-o`, so tap `Alt` in the client's extra key row and then `o`, which is untested on a phone `[spike]`.
   Typing `tmux detach` in a shell pane works in any client.
   The session keeps running on the laptop.

Some clients refuse a server that asks for no authentication.
If yours does, enter any password, Tailscale ignores it `[docs]`.
A phone keyboard lacks `Ctrl`, `Alt` and `Esc`, Termius and Blink have them in the extra key row, Termux in its extra keys bar.

To switch it off, run `scripts/phone-ssh.sh off --yes`, and `sudo tailscale down` to leave the tailnet.

### Status

- `welleng rc` and the port check are tested on Arch, and a live port snapshot and diff ran on the real machine.
- `scripts/phone-ssh.sh` ran its status and dry runs on WSL2 Ubuntu without Tailscale installed, nothing more.
- No phone has ever connected by either way.

Run [docs/verification/phone.md](../verification/phone.md) before relying on either, and record the result in `CHECKLIST.md`.
