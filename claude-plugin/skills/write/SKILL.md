---
name: write
description: "Write or edit prose so a tired engineer understands it on the first read, and remove AI tells. Covers docs, ADRs, READMEs, skill files, PR descriptions and commit messages. Use for /welleng:write."
disable-model-invocation: true
---

# Write

Write so a tired engineer understands the text on the first read.
Every reply, document, commit message and PR description goes through this skill.

## House rules

These come from the Well-Engineering instructions and win over everything below.

- Never use the em dash character.
  A plain dash is allowed, but a period or a comma is usually better.
- In Markdown, put each full sentence on its own physical line.
  Keep normal Markdown structure, and continue a list item on an indented line.
- Label every claim about verification with the platform it ran on and an evidence tag where the repository uses them: `[verified: Arch]`, `[docs]`, `[search]`, `[spike]`.
  Container runs are "tested in container".
- Commit subjects use Conventional Commits, such as `feat(scope): subject`.
  A commit or PR describes the change only, with one concern per commit.
- Never mention an AI assistant, an agent session or co-authorship in commits, pull requests or files.
- Never edit `CHANGELOG.md` or a file marked as generated.

## Pick the mode first

One document has one mode.
Split and link instead of mixing them.

- Tutorial teaches by doing.
  Every step produces a visible result, and you say what the reader should see.
- How-to solves a task for a competent reader.
  Action only, named after the task.
- Reference describes facts for lookup.
  Keep it dry, complete and in the shape of the thing it describes.
- Explanation gives understanding and the reasons behind a design.
  Opinion belongs here and nowhere else.
  An ADR is an explanation.

## Sentences

- Talk to the reader as "you", in the present tense.
- Say who does what.
  Use the passive only when the actor is unknown or does not matter.
- Write instructions as commands, with the condition before the step it guards.
- One instruction per sentence and one thought per sentence elsewhere.
  Split an instruction longer than about 20 words and other sentences longer than about 25.
- Keep "the" and "a", and keep small words such as "that" when they show structure.
- Keep "only" and "not" next to the word they change.
- Make every "it", "they" and "this" point at one obvious thing.
- Call each thing by one name everywhere, and write the real symbol, file, flag or command name.
- Use the short, everyday word: "use", not "utilize" or "leverage".
- Mix sentence lengths, and be specific.
  Not "schema changes can cause issues" but "a column rename fails the build".
- Numbered lists for sequences, bullets for everything else.
  Introduce a list with a complete sentence and keep items parallel.
- Headings carry the point, in sentence case, with one h1 per page and no skipped levels.
- Code goes in code font, and links say where they go.

## Remove AI tells

Scan for these patterns, then rewrite.
Keep the meaning and the intended tone.

1. No trailing "-ing" phrase that adds no fact, such as "ensuring reliability".
2. No vague attributions such as "experts believe".
   Name the source or delete the claim.
3. No AI vocabulary: additionally, crucial, delve, enhance, foster, landscape, pivotal, showcase, testament, underscore, vibrant, robust, seamless.
4. Say "is" or "has", not "serves as", "stands as", "boasts" or "features".
5. No "not just X, but Y".
   State the point.
6. Do not force ideas into threes.
7. No "from X to Y" unless X and Y sit on a real scale.
8. A colon goes before a list or an example, never mid-sentence as a connector.
9. Do not bold every proper noun, and do not open a line with a bold label that restates it.
10. No decorative emojis, no curly quotes, no chatbot phrases such as "I hope this helps".
11. No praise or agreement openers.
    Answer directly.
12. Cut filler.
    "In order to" becomes "to", and "it is important to note that" disappears.
13. At most one hedge, and give the number instead of an adverb.
14. No generic conclusion.
    End on a specific plan or fact.
15. No abstract metaphor nouns such as substrate, wedge, nexus, paradigm, flywheel or north star.
    Product names such as `/welleng:harness` are fine.
16. Say what something does, not how it feels.
    Cut any sentence that could appear unchanged in another project's docs.
17. Write whole sentences, and spell out arrows and abbreviations.

## Commits and pull requests

- A PR body is a briefing a reviewer reads in under a minute, at most 40 lines long.
  Use these headings in this order and drop the empty ones: `## Why`, `## What changed`, `## Scope`, `## Tradeoffs`, `## Blast radius`, `## Verification`.
- Put logs, SHA lists and long tables in a linked file or comment, not in the body.
- Every count or tree claim must be true at the commit that lands it.
