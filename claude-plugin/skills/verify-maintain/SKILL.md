---
name: verify-maintain
description: "Keep a project's verification skill and feature map honest after the app changes, with one source pass and one live pass per feature and at most one PR of proven corrections. Use for /welleng:verify-maintain."
disable-model-invocation: true
---

# Verify maintain

A feature map rots when the app changes.
This is the upkeep loop for a skill made by `/welleng:verify-setup`, or any project-local verification skill with a feature map.
Cover every feature file from source and exercise every feature live.

## Outcomes

Pick one and say which:

- **clean**, every feature had source and live coverage and nothing needs to change.
  No branch and no PR.
- **changed**, one PR ships proven corrections to the docs, the harness or the map.
- **blocked**, coverage could not finish or a proven fix could not ship safely, with exactly what blocked it.

## Edit scope

Edit only the verification skill's own folder: its `SKILL.md`, `features/` and its scripts.
Never edit product code during this pass.
A behavior the map describes but the app no longer has is either drift in the map, which you fix, or a product regression, which you report.

## Pass

1. **Locate the target.**
   Find the project-local skill under `.claude/skills/verify-*/`.
   With several candidates, ask which one.
   With none, stop and point at `/welleng:verify-setup`.
2. **Index hygiene.**
   Read the map's `README.md` and its sibling files, and fix missing, extra, duplicate or dead entries.
3. **Source wave.**
   Spawn one read-only `Explore` subagent per feature file, all at once.
   Each explains from source how the feature works, flags likely drift with citations, and returns one live recipe.
   They never drive the app and never edit files.
4. **Reconcile.**
   Every feature file needs a returned summary.
   Merge overlapping recipes, spot-check cited drift, and look at recent commits for user-facing features missing from the map.
   Call a feature missing only with a concrete source path.
5. **Live pass.**
   Required even when the source looks clean, and you own all driving.
   Follow the skill's own launch model.
   Run the doctor before the first drive and after any failed drive, keep the evidence through every cleanup, and leave nothing running after the pass.
   A feature you cannot reach is unreachable only with the concrete prerequisite and the route you tried.
6. **Triage.**
   A wrong or missing description is drift, so fix it.
   Working behavior the harness cannot drive is a harness gap, so fix it and drive the fix live.
   Broken app behavior is a product gap, so report it and keep it out of this PR.
7. **Ship or stop.**
   For changed, open one PR of proven corrections after re-reading every changed file.
   For clean or blocked, report the outcome and the coverage honestly.

Keep short run notes in a scratch location and do not commit them.
