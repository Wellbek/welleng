# Foundational thinking

Apply when you are about to write logic: choosing core types and data structures, ordering scaffold against feature work, or deciding what concurrent actors share.

Get the data shape right before writing logic.
Define the core types early, trace every access pattern, and choose structures that match the dominant paths.
Remove duplication in the structure, not in every line.

Before sharing state between actors, ask what happens if another actor changes it at the same time.
If the answer is not "nothing", isolate it.

Scaffold first.
Whatever helps every later phase, such as CI, tests and shared types, goes first, right after removing dead code.
Keep commits small and single-purpose.
