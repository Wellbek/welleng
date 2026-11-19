# Feature map example

A feature map is a `features/` folder inside the verification skill.
It holds a `README.md` index and one file per user-facing feature.
This example is for a command-line notes app driven through tmux.

## The index, `features/README.md`

```
# Notes verification map

This folder is the maintained source for verifying what Notes does for a user.
Read the index before driving the app, then use the matching feature file as the recipe.

## Baseline preconditions

- Build once with `make build`, which puts `bin/notes` in the checkout.
- Set `NOTES_DATA_DIR=<scratch>/notes-verify-$RUN_ID` so runs never share state.
- Seed two notes titled `Quarterly plan` and `Grocery list` with `bin/notes import fixtures/seed.json`.
- Run `bin/notes doctor` and require the expected data directory and build revision.

## Driving conventions

- Start every recipe from the baseline state unless it says otherwise.
- Drive in `tmux -L verify-notes`, never in the user's tmux server.
- Treat every command as literal.

## Proof

- Terminal proof is the command, stdout, stderr and the exit code.
- A change is proven by a second, read-only view of the stored value.
- Report an unreachable path with the attempted command and the unmet precondition.

## Features

- [Search notes](search.md) covers matching, the empty result and JSON output.
```

## One feature, `features/search.md`

Each feature file starts with a title and one paragraph about the user-visible behavior.
It then has exactly four sections in this order.

```
# Search notes

Search finds notes by title or body text, and tells no matches apart from an error.

## Sub-features

- `search-match` returns title and body matches without changing data.
- `search-empty` prints a clear message when nothing matches.
- `search-json` returns the same matches as JSON.

## How to get to it (user POV)

- Run `notes search <query>` in a terminal.
- Press `/` in `notes browse`.

## Driving it with tmux

Preconditions:

- The baseline data directory holds `Quarterly plan` with body text `Draft budget`.

- **Title match.**
  Run `bin/notes search quarterly`.
  Exit code 0, and stdout lists `Quarterly plan` and not `Grocery list`.
- **Body match.**
  Run `bin/notes search budget`.
  Stdout lists `Quarterly plan` with a body excerpt.
- **Empty result.**
  Run `bin/notes search volcano`.
  Exit code 0, and stdout is `No matching notes`.
- **JSON.**
  Run `bin/notes search quarterly --format json`.
  Stdout is one object whose title is `Quarterly plan`.

## Gotchas

- Archived notes are excluded unless `--archived` is given.
- The default output is for humans, so use `--format json` for assertions.
```
