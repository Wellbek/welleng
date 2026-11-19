# Visual parity

You own pixel-exact equivalence.
The baseline is the specification, and you do not touch it.
Equivalence is shown by an image diff, not by eye.

1. Build the baseline before any migration: a harness that screenshots the current component in each of its states, and the target when you match two implementations.
   Drive the browser through the Chrome DevTools MCP server or Playwright.
   No baseline means no parity claim.
2. Hold these rules: no harness changes, no baseline edits, and no restructuring a component to make a diff pass.
   If the baseline looks wrong, stop and ask.
3. Migrate one component at a time, with shared primitives first as a blocking phase.
   Run independent components in parallel worktrees, one owner each.
4. Verify each component with an image diff, such as `compare -metric AE` from ImageMagick or Playwright's screenshot assertions.
   A nonzero diff is a failure, so investigate the pixel delta and iterate until it is zero.
5. Run `playbooks/opening-a-pr.md` per component or per safe batch.

**Reply:** the components migrated, the diff result for each, the harness location and what is left.
