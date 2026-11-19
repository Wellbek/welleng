# Build the lever

Apply when you do any non-trivial work: edits, migrations, analyses or checks.

Build the tool that does the work or proves it, such as a codemod, a script, a generator or a rerunnable check, instead of working by hand.
The bar is triviality, not repetition, so skip the tool only for a couple of obvious edits.

- Do the first unit by hand, then build the tool and prove it by rerunning it on that unit.
  Make it safe to rerun.
- A deterministic tool beats fan-out.
  When you do fan out, write the recipe, the verification contract and the limits as one file the delegates read.
- Applying this principle produces a file.
  Commit it when the work outlives the session.
- Build the smallest script that does the job, never a framework.
