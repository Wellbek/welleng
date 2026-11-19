---
name: verify-welleng
description: "Drive Well-Engineering the way its user does and capture evidence: the welleng plugin inside a live interactive Claude Code session (effort hints, status line, /welleng:mode) and the welleng CLI in a throwaway project. Use to verify a change to the plugin, its hooks or the CLI before calling it done."
---

# Verify welleng

This skill proves Well-Engineering behavior on the real surface: an interactive Claude Code session in tmux, and the `welleng` command line.
It runs on the maintainer's Arch Linux machine, because a live session needs a signed-in `claude`.
Label every result `[verified: Arch]` with the Claude Code version, and never claim another platform.

## Isolation

- Every drive runs on the private tmux server `verify-welleng`, through `scripts/drive.sh`.
  Never touch the user's tmux server or any session named `welleng:*`.
- Every run uses a throwaway git project in a scratch folder, never a real repository.
- Hook and status line state go to `<evidence>/state`, through `XDG_STATE_HOME`, so the user's hint cooldown and dashboard state stay untouched.
- A live session spends real usage.
  Ask the user before a run, unless they asked for verification in this conversation.
  Use `--model sonnet` unless the feature needs another model.

## Launch

From the repository root:

```
D=.claude/skills/verify-welleng/scripts/drive.sh
RUN="$(date +%Y%m%dT%H%M%S)-<feature>"
EV="$PWD/.git/verify-welleng/$RUN"
P="$(mktemp -d)"; git -C "$P" init -q
$D start "$P" "$EV" --model sonnet --effort high
$D trust
$D wait '\| high \|' 30
```

Ready means the status line shows the model and the effort level.
`drive.sh trust` answers the workspace trust dialog and checks on screen that "Yes" is selected before it presses Enter, because the dialog starts on "No, exit".

## Doctor

Run `$D doctor` before the first drive and after any failed drive.
It fails when `claude` is missing or the verification session is not running.
If a drive timed out, capture the pane with `$D capture "$EV/failed.txt"` and read it before retrying, because the session may have exited.

## Drive

- `$D send "<text>"` types a prompt and presses Enter.
- `$D keys <tmux key names>` sends raw keys, such as `Escape` or `Down`.
- `$D wait '<regex>' <seconds>` waits for the pane to match, and fails with a timeout message otherwise.
- `$D capture "$EV/<step>.txt"` saves the pane with its scrollback.

The feature map in `features/README.md` lists each feature with its recipe.

## Evidence

Evidence lives in `.git/verify-welleng/<run-id>/`, inside the repository's git folder, so it survives cleanup and is never committed.
A proof holds the pane capture of the action and its result, and the state files under `state/welleng/` when the feature writes any.
Record the Claude Code version from `claude --version` with every result.

## Cleanup

```
$D stop
rm -rf "$P"
```

`drive.sh stop` kills only the `verify-welleng` server.
Never remove `.git/verify-welleng/`, which holds the evidence.

## Helpers

`scripts/drive.sh` is the only helper.
Run it without arguments to print its usage.
