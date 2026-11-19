---
name: tdd
description: "Fix a bug test-first. Write a focused regression test that fails, then the fix that makes it pass. Use when the user asks for TDD, a failing test or a regression test, or when the bug has a cheap local test path. Use for /welleng:tdd."
disable-model-invocation: true
---

# TDD bug fix

When a bug has a clear, cheap test path, make the broken behavior executable before changing production code.
The goal is a focused regression test that fails before the fix and passes after it.

Do not force a test when it would be impractical.
If the test would need broad harness setup, brittle mocks, slow end-to-end infrastructure, production-only state or large unrelated fixture churn, use the closest useful check instead.

## Workflow

1. Understand the bug: the intended behavior, the current behavior, the affected path and the smallest observable reproduction.
2. Choose the narrowest executable check, preferably in the test suite that already covers that code path.
3. Write the failing test first.
   It encodes the intended behavior, per `../mode/principles/test-behavior-not-implementation.md`.
4. Run it before the fix and confirm that it fails for the intended reason.
   If it passes, or fails for another reason, fix the test before touching the implementation.
5. Make the smallest production change that gives the intended behavior and keeps nearby contracts.
6. Rerun the test and confirm that it passes, then run the nearby suite.
7. Commit the failing test before the fix, so the history proves the bug, per `../mode/principles/sequence-verifiable-units.md`.

## When a failing test is impractical

Use the closest executable check instead: a targeted script, a reproduction command, browser automation, a snapshot comparison or a log assertion.
Prefer no new test over a bad test.
A bad test mostly tests mocks, encodes implementation details, depends on timing, needs expensive infrastructure for a small fix, or would be deleted right after proving the fix.

## Guardrails

- Do not change a test to match a wrong implementation.
- Do not weaken an existing assertion unless the expected behavior has really changed, and say why.
- Keep the test focused on the bug.
- Make a flaky bug's test deterministic where possible, and name the signal it locks down.

## Reply

- The failing-before test or check, with the failure it produced.
- The passing-after run and any nearby validation.
- If you could not show a failure first, say why and name the closest check you used.
