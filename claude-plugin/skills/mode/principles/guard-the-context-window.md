# Guard the context window

Apply when the context fills up: large outputs, long files, repeated reads or fan-out planning.

Context overflow degrades reasoning and halts progress.

- Route bulk reading and parsing to subagents, and keep their summaries, not the raw payloads, in the main thread.
- Read files in ranges when you know which part you need.
- Size phases and cap the scope of each one.
