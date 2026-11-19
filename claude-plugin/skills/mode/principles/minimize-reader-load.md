# Minimize reader load

Apply when you review or shape code that is hard to trace.

Reader load is the work a reader does to understand code.
It has two axes: the layers to trace between the question and the answer, and the hidden or mutable state to hold in mind.

- Collapse layers that only forward: wrappers with one caller, adapters with no second implementation, pass-through methods.
- Shrink state scope.
  Prefer returns to mutations, locals to fields, fields to module state, and module state to globals.
  Derive a value instead of keeping two copies in sync.
- Name an invariant once, at the boundary, not in every consumer.

The test is whether a new reader can answer "where does X come from?" and "what can change X?" in under 30 seconds.
