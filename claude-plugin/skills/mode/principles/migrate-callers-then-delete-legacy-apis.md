# Migrate callers, then delete legacy APIs

Apply when you introduce a new internal API while old callers still exist.

Migrate every caller and delete the old API in the same wave, instead of keeping a compatibility layer.

- Update the tests to assert the new contract, and delete tests that only protect the old implementation.
- Spot-check every rename against the files, because strings, prose and back-references escape a symbol search.

This applies when no external user depends on backward compatibility and the project can absorb a coordinated change.
