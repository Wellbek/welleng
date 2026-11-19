---
name: architect
description: "Settle the types, signatures and module shape of a change before writing code that crosses a function boundary, then stay in the loop while the implementation fills it in. Use for /welleng:architect."
disable-model-invocation: true
---

# Architect

Before writing code, trace every system the change touches.
Then sketch two different shapes for it, each with its types, signatures and module boundaries, starting from how a caller would use it.

Pick the shape where each piece of state has one owner, each task has one way to do it, and callers need to know the least.
Name the data shape first, per `../mode/principles/foundational-thinking.md` and `../mode/principles/model-the-domain.md`.
If workarounds repeat in the current design, redesign instead of patching, per `../mode/principles/redesign-from-first-principles.md`.

For a large or contested design, run `../arena/SKILL.md` instead of sketching alone.

Stay in the loop while the implementation fills the shape in.
When the code drifts from the sketch, decide whether the sketch or the code is wrong, and fix that one.

**Reply:** both sketches as code signatures, the one you picked, and the reason in one or two sentences.
