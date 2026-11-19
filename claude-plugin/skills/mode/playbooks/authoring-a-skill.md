# Authoring a skill

You own the skill's voice.

1. Write the `SKILL.md` with frontmatter: a `name` that matches its folder and a quoted `description` that says what it does and when to use it.
   Set `disable-model-invocation: true` unless the model must be able to start it on its own.
2. Keep only prose that changes a decision.
   Tell the agent to do the thing and skip the reason, unless the rule is confusing without one.
   Point at structural sources such as types, READMEs and config, per `principles/encode-lessons-in-structure.md`.
   Delegate to other skills by path instead of restating them.
3. Validate it.
   In the Well-Engineering repository, run `python3 -I scripts/check-skills.py`.
   Elsewhere, check that the frontmatter parses, that referenced files exist and that cross-skill links resolve.
4. When the change is meant to alter agent behavior, test it with the eval below.
   Skip the eval for a subjective wording change.
5. Run `playbooks/opening-a-pr.md`.

When in doubt, delete.
A workflow you keep hitting that no skill captures is a candidate for a new skill.

## Eval

Test how a skill or prompt change affects agent behavior, blinded.

- No word such as eval, test, judge, rubric, score, compare or benchmark appears in any folder, file or prompt the candidate sees.
- The candidate prompt reads like an organic user request, with no cue to list the skills or principles it applied.
- Candidates do not know that other candidates exist.
- The judge sees outputs by neutral label only, never by model or variant.

1. State the variant under test and what behavior counts as success.
   Write a rubric of three to six criteria for the judge only.
2. Prepare one neutral working folder per candidate with the variant in place.
3. Run each candidate headless and record its tool calls through the official CLI output: `claude -p "<prompt>" --output-format stream-json --verbose > <scratch>/<label>.ndjson`.
   Load the variant plugin with `--plugin-dir <path>` where `claude --help` lists that flag.
4. Grade which files each candidate opened from the `tool_use` events in that stream and from the shape of its output, never from its own claims.
5. Spawn one blinded judge on a different model family, then read every output yourself and compare with the judge.

**Reply:** a summary of the skill, the key design decisions and the validation output, plus for an eval the rubric, per-candidate notes, the judge's verdict and whether to promote the variant.
