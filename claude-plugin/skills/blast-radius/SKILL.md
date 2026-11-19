---
name: blast-radius
description: "Find what a small-looking change could break somewhere else before it ships, and prove the one fact it is safe because of by running code. Use for /welleng:blast-radius and for diffs you do not trust yet."
disable-model-invocation: true
---

# Blast radius

Find what a change breaks somewhere else, before it ships.
Listing the callers is not the job, because grep does that in a second.
The job is the breakage grep will not show you.

## Do not trust your own writeup

A writeup that sounds right reads as convincing whether or not it is true.
Find the one or two facts the change's safety depends on and prove them by running code.

For each fact, get as far down this list as is cheap, and say where it stopped:

1. You said so, which is worthless on its own.
2. You pointed at the line, a real `file:line` or the library's own source.
3. You showed that the bad case cannot happen by walking the failure step by step.
4. You ran it, with a script or test that calls the real code and fails loudly if you are wrong.
5. You reproduced it in the running application.

## Steps

1. Read the change: the diff, the symbols it adds, changes and deletes, and what it now does differently, including the part the diff does not spell out.
2. Find the one fact it is safe because of, such as "this call only drops cache entries that are already dead".
   Spend your time here, not on a long list of maybes.
3. Look where grep stops.
   Read the source of the library you call at its pinned version.
   Work out when things run, such as at import, at teardown or in a hook.
   Follow what a symbol search misses: a JSON payload, a database column, a wire format, a config key, another language reading the same bytes, a feature flag.
4. Be honest about each risk, with a real chance and a real cost.
   Keep the confirmed risks, and list the ones you checked and cleared separately.
   Cite a real `file:line`, and never make up a caller or an API.
5. Prove the one fact with a script or test that runs the real code, and paste what happened.
6. For a big or wide change, run `../arena/SKILL.md` with the same question, because different models catch different real bugs.

## Reply

- **What it does**, including the part that is not obvious.
- **The one fact it is safe because of**, with the level it reached and the proof, or "unproven".
- **Risks**, each with how it breaks, the `file:line`, how likely and how bad, and how to check.
- **Cleared**, what you checked and why it is fine.
- **Before you merge**, the cheapest test or repro that catches the real bug, including the script you wrote.

Write it through `../write/SKILL.md`.
