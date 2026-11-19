# Type system discipline

Apply when you design types or a signature, or write code in a typed language.

Make the type checker reject impossible states, mismatched primitives and unhandled variants.

- Give two arguments that share a primitive type but mean different things their own types, and validate once at creation.
- Treat external data as untyped until a parse function at the boundary returns the typed model.
- Handle every variant of a union exhaustively.
- Derive types from the authoritative schema instead of keeping a parallel copy.
