---
name: verify-setup
description: "Generate a project-local verification skill that drives the app the way a user does and captures evidence, for any language or platform. Use for /welleng:verify-setup, or when a project has no scripted way to prove UI, CLI or service behavior."
disable-model-invocation: true
---

# Verify setup

Every serious project needs a scripted way to drive the real app and prove behavior: launch it, exercise a feature the way a user would, and capture evidence.
This skill generates that as a project-local skill at `.claude/skills/verify-<app>/`.
You write it for the next agent, who reads it cold, mid-task, and has never seen the app.

## 1. Interview the repository, not the user

Answer these from the code, and ask the user only what you cannot observe:

- **Surface.**
  What does a user touch: a web UI, a CLI or TUI, a desktop app, an API, a library?
  Pick the primary one and note the others.
- **Run.**
  How does the app start locally?
  Prefer the repository's own documented command, and note ports, environment variables, seed data and auth.
- **Drive.**
  How can an agent interact with it?
  Use existing harnesses first, such as Playwright specs, expect scripts or HTTP endpoints.
  Otherwise pick a recipe: a browser through the Chrome DevTools MCP server or Playwright for web apps, tmux on its own socket (`tmux -L verify-<app>`) with `send-keys` and `capture-pane -p` for a CLI or TUI, and `curl` for a service.
- **Observe.**
  Which evidence can be captured: screenshots, terminal transcripts, response bodies, logs, exit codes, database state?
- **Isolate.**
  Can two instances run side by side with their own ports, data directories and profiles?
  If not, say so in the generated skill, because refusing to drive a shared instance beats corrupting the user's session.

If the checkout does not build or start as it is, fix that first or report it precisely.
A skill written against a broken base teaches wrong steps.

## 2. Generate the skill

Write `.claude/skills/verify-<app>/SKILL.md` with frontmatter, a `name` of `verify-<app>` and a quoted `description` that names the app, the surface and when to use it.
Fill these sections with what the interview found, with no placeholders left:

- **Launch.**
  The exact command that starts the app for verification and how to tell that it is usable, not only that a process answers.
  Launch reaches a usable state from an empty data directory, including migrations and seed data.
  For a short-lived CLI, launch means building once, then starting each drive in its own isolated session.
- **Doctor.**
  One read-only check of whether this instance is worth driving: the process is up, the build is right, the port is ours, auth is valid.
- **Drive.**
  The recipe with real selectors, commands and prompt strings from this repository.
  Prefer stable handles such as ARIA labels, data attributes, prompt strings and route paths over coordinates.
- **Evidence.**
  What to capture and where it goes.
  Exercise the real user path, not internal setters or test-only endpoints.
  Capture the action and the resulting state, and check side effects such as files written or rows inserted.
  When the safe path is a dry run, check by observation what it actually skips.
- **Cleanup.**
  How to remove what the run created.
  Never kill by process name, kill only what you started.
  Cleanup never removes the evidence, which stays at a location the skill names.
- **Isolation from the user's session.**
  Never use the user's running instance, profile or tmux server.
  In a Well-Engineering setup, never touch tmux sessions named `welleng:*`.
- **Helpers.**
  Every script the skill ships is executable, and the skill shows how to call it.

## 3. Seed the feature map

Create `.claude/skills/verify-<app>/features/README.md` and one file per user-facing feature, starting with the top three to five from routes, commands, menus or docs.
Follow the shape in `references/feature-map-example.md`.
If the seed data lacks a precondition that a journey needs, the journey reports a failure and the reason goes into that feature's gotchas.
Never weaken a journey to make it pass.

## 4. Prove the generated skill before handing it over

Run its own instructions once, end to end: launch, doctor, drive one mapped feature, capture evidence, clean up.
After cleanup, confirm that the evidence still exists at the named location.
Fix what fails, and run the cleanup after every failed attempt so nothing strands processes or ports.
A generated skill that was never executed is a draft, not a deliverable.

If you proved it in a stand-in for the real target, such as a container instead of a fresh machine, list every setup step the stand-in did that the target will not.
Those steps stay unverified until a run on the real target covers them.

## 5. Hand over

Report the skill path, the features mapped, the proof run with its evidence path and the platform it ran on.
Point the user at `/welleng:verify-maintain` for keeping the map honest as the app changes.
