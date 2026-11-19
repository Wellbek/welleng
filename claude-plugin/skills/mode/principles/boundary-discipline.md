# Boundary discipline

Apply when you wire validation, error handling or framework adapters.

Validate, narrow types and handle errors where data crosses a system boundary: CLI arguments, config files, environment variables, network and external APIs.
Inside, trust the types, with no repeated validation and no redundant null checks.
Parse raw data into domain types at the boundary, and keep business logic in pure functions behind a thin shell.

Ask two questions.
Is this data crossing a boundary right now?
Can this be a pure function that the shell calls?
