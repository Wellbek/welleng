---
name: ketchup
description: "Catch the user up on what changed in this conversation since their last message, in plain words, and list every decision waiting on them so they can make it from the reply alone. Use for /welleng:ketchup."
disable-model-invocation: true
---

# Ketchup

Catch the user up on what changed since the last message they wrote before typing this command.
Notifications and subagent results are not their messages.
Assume the user remembers their last message and nothing after it.

Use the voice of `../bro/SKILL.md`: plain words, short sentences, no jargon.
Say what changed for the user, not how you did it, such as "the tests pass" rather than "CI is green".
Leave out hashes, paths, commands and counts unless the user needs one to act.

## Gather

Keep this turn read-only.
Collect your own work since that message, the subagent reports and anything else said in the conversation.
Check the current state of every pull request, CI run or agent the conversation touched, and check each number against its source.

An action item is a call or step only the user can take, such as a product choice, an approval, an irreversible action or access you lack.
Work you can still do yourself is not an action item, and never make one up to fill the reply.
For each item, collect its link, what it changes for users, the evidence behind your pick, its risk and your pick.
Write "unknown" for a fact you do not have.

## Write the reply

1. Open with one sentence that names what waits on the user, or says that nothing does.
2. Say what happened in under 100 words, with pictures first: screenshots the work produced, then a Mermaid diagram when it explains a change faster than words.
   Keep a diagram to at most six boxes of at most eight words each.
3. Give one short line per thing the user asked for: what came of it, and whether it is done, still running, failed or not checked.
   Never mark something done that still waits on the user.
4. List the action items, about 30 words each.
   Ask the call the user owns and give your pick, with what it changes for users, the evidence and the risk, even when the risk is low.
   For a call between options, give every option with what it gets and what it costs.
   Never cut items to stay short.
