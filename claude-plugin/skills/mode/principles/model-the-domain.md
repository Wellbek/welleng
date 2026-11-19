# Model the domain

Apply when you write stateful logic, or code that branches a lot or repeats a shape assumption across files.

Encode the domain in a data structure instead of scattering it across conditionals.
The right structure makes invalid states unrepresentable and deletes branches.

Reach for a state machine instead of scattered booleans, a typed model instead of loose parameters, a table or registry instead of branching spread across files, and a reducer instead of ad hoc mutation.

Do not force it.
Keep boring code when the shape is clear, local and unlikely to grow.

You skipped this principle when a feature grows an if-else chain by one more branch, or when a second boolean must stay in sync with the first.
