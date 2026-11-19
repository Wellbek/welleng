# Test behavior, not implementation

Apply when you write, change or keep a test.

A test is a claim about what users of the code can observe through its interface: return values, errors, state they can read back and effects on outside systems.

Judge each test against two imagined edits.

- Break the behavior.
  If the test still passes, it proves nothing.
  The usual causes are a loose assertion, an expected value computed by the code under test, and an assertion on data the test built itself.
- Change the internals and keep every observable result.
  If the test fails, it is pinned to the implementation.

Keep a test that catches the first edit and survives the second, and rewrite or delete the rest.
Derive the expected value from the requirement, and assert the error type that callers branch on, not the message.
