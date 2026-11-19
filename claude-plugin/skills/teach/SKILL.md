---
name: teach
description: "Explain a change or a subsystem so a person understands it, not only a summary. Combines how and why into one plain account built up diagram by diagram. Use for /welleng:teach."
disable-model-invocation: true
---

# Teach

You explain what a thing is, how it works and why it is built that way, in one plain account at the person's pace.
The goal is understanding, not a change to the code.

1. Decide the few things the person should walk away understanding.
   Choose them from why they ask (about to change it, reviewing it, debugging it, new to it) and from what they already know, both read from the conversation.
   Skip what they plainly know, and put the depth where their question is.
2. Get oriented in the code yourself, then let the other skills do the digging.
   Read `../how/SKILL.md` and `../why/SKILL.md` and run both, in parallel, for a subsystem.
   One of them can be enough for a small change.
   Keep the confidence language of `why`, because its hedges are findings.
3. Start with a plain definition.
   Name the thing, with its common name if it has one, then tie it to the case at hand and build from there.
   For each part, explain the problem it solves and how it actually works.
   Give the smallest complete answer first, a sentence or two, then stop and add layers when asked.
4. Keep it a conversation.
   Offer to go deeper or to move on, and follow the person's lead.
   No quizzes, no "this is the tricky part", no "key insight" labels.
   Running without a live person, deliver it cleanly and put the offer to go deeper at the end.
5. Show the thing as well as telling it.
   Open the diff or the code when that lands fastest.
   For three or more moving parts, draw a short series of Mermaid diagrams where each one redraws the last and adds one part.
   A single all-at-once diagram is reference, not teaching.

Write every reply through `/welleng:write`, in plain spoken English.
State the concrete mechanism, not a metaphor.

**Reply:** the explanation itself, never a report about it.
