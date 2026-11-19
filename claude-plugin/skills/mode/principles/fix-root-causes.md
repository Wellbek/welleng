# Fix root causes

Apply when you debug.

Fix the fault, not the place where it surfaced.
The root cause is the first place the system did something it should not do, or failed to handle a state it should handle.

- Reproduce first, as close as possible to how a user meets the bug.
  Ask "why" until the answer is a wrong decision in the code, and instrument to read the actual state when you are stuck.
- Ask whether the state that triggered the symptom is legitimate.
  If it is, handle it where the code broke.
  If it should never exist, a check at the symptom hides the bug, so find what produced the state.
- Fix the pattern, not the instance, and find every place with the same fault.
- If the deciding fact took a deep dig, propose the cheap always-on signal that would have shown it at first look.
