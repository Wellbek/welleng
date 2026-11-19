# Laziness protocol

Apply when you refactor, size a diff, or feel the pull to add an abstraction, a layer or another flag threaded through the code.

Bias toward deletion and the smallest change that solves the problem.

- Consolidate decisions.
  Do not repeat one choice in several places.
  Put it behind one source of truth and pass the result as a simple value.
- Minimize the diff.
  Fewer lines beat elegant boilerplate.
- Do not add a layer that has one caller, an option that nobody sets, or a guard for a state that cannot happen.
