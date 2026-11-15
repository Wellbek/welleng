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

## Session state and the agents dashboard

1. In a throwaway repository run `claude`, send one short prompt, and let it finish.
2. In another terminal run `welleng agents`.
   Expected: your session has a model, effort level and subagent count (`sub`) filled in, and `ls ~/.local/state/welleng/sessions/` shows one mode-600 file for it.
3. Add the status line from the header of `claude-plugin/hooks/statusline.py` to a throwaway settings file, restart the session, send a prompt, and run `welleng agents` again.
   Expected: the `ctx` and `cost` columns are filled in, and the status line shows model, effort, context and cost.
4. Exit the session.
   Expected: its state file is gone.
5. Check that no prompt text appears in the state file: `grep -r "<a word from your prompt>" ~/.local/state/welleng/`.

## Contextual prompt keys

1. Start tmux, run `claude --ide` in one pane and `NVIM_APPNAME=welleng-nvim nvim somefile` in another.
2. Select a few lines and press `<leader>ae`.
   Expected: the selection is attached in Claude, the instruction is typed into the Claude input but not sent, and focus moves to the Claude pane.
3. Repeat in normal mode, which attaches the whole buffer, and with `<leader>af`, `<leader>at` and `<leader>ar`.
4. Close the Claude pane and press `<leader>ae` again.
   Expected: a warning, and the instruction is on the clipboard.

## Record

Update the plugin, hint, state writer, contextual prompt and `/harness` rows in `CHECKLIST.md` with the Claude Code version and the date.
