# Verify hooks, hints and the harness skill in an interactive session

Status of what this covers: the hooks ran in a headless session only, see ADR 0016.
The plugin is installed from the local marketplace as `welleng@welleng-local`.

## Hook input

1. Start `claude` in a throwaway git repository with no `CLAUDE.md`.
2. Run `/effort high`, then send `rename foo to bar`.
3. Run `welleng hints report`.
   Expected, if the hook input carries an effort level: one recommendation logged, and a one-line hint shown to you.
   If instead "prompts that carried no effort level" grew, the field is not provided interactively either.
   Record that, because it means the hint design needs the status line as its source.

## Session start suggestion

1. Start a new session in a git repository with no `CLAUDE.md` and no `.claude/settings.json`.
2. Ask: "Is there anything you suggest for setting this project up?"
   Expected: the model mentions the `/harness` skill once, and does not start it on its own.

## The /harness skill

1. In the same throwaway repository, run `/harness`.
2. Answer two questions and skip the rest with `-`.
   Expected: one question at a time, the skip token accepted, and a plan with diffs shown before anything is written.
3. Answer `no` to the apply question.
   Expected: no file was created, check with `git status`.
4. Run `/harness` again and approve.
   Expected: files appear, `welleng harness check` reports ok, and a rerun reports "nothing to change".

## Record

Update the plugin, hint and `/harness` rows in `CHECKLIST.md` with the Claude Code version and the date.
