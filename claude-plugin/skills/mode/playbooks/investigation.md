# Investigation

You own the answer.
An investigation is read-only and produces a cited explanation or a recommendation, not a code change.

1. Trace the code the question is about.
   For a question about motivation, also run `../why/SKILL.md`.
   Route bulk reading to `Explore` subagents, per `principles/guard-the-context-window.md`.
2. Write the output with these parts: overview, key concepts, how it works, where things live, gotchas.
   For a decision between alternatives, give a recommendation with a tradeoffs table instead.
3. Run the reply through `../write/SKILL.md`.

No pull request and no `architect` step, unless the investigation precedes a code change.
If it does, say so and continue with the bug fix or feature playbook.

**Reply:** the investigation output.
For an "are we sure?" question, give your real judgment with reasons, and push back if the premise is wrong.
