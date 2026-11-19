# Separate before serializing shared state

Apply when concurrent actors might write the same file, branch, key or state object.

First ask whether the actors need one shared object or publish independent facts.
By default give each actor its own file, key, branch or state directory, and merge only where the state is read.
Two workers writing their own field into one `state.json` is still shared mutation.

Serialize access, with a lock file, a single writer or sequential phases, only when one shared target is a real invariant.
Instructions are not concurrency control.
