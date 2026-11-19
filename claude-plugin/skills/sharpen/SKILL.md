---
name: sharpen
description: "Make a task deeper, not bigger, then hand back a rewritten prompt without doing the task. Use for /welleng:sharpen."
disable-model-invocation: true
---

# Sharpen

The user wants a deeper version of their task, not a bigger one.
Before rewriting it, answer four questions:

1. What would a top professional in this field do here that the user did not ask for?
2. What is the rawest material they would start from, instead of what has already been digested?
3. Which specific methods and tools would they use?
4. What, other than you or the user, would show that the result is right?

Then rewrite the prompt to ask for exactly that.
The rewritten prompt asks the agent to prototype any choice an experiment can settle and to recommend an option from what it observed.
It leaves product and preference choices that no experiment can settle to the user.

Hand back the rewritten prompt only.
Do not do the task.
