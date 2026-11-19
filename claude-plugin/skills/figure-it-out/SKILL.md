---
name: figure-it-out
description: "Design an auditable playbook when no narrower one fits, such as a large migration, an ambitious multi-part change or work that runs while the user is away. Use for /welleng:figure-it-out."
disable-model-invocation: true
---

# Figure it out

When the task matches no playbook, design one.
The deliverable before any code is the workflow itself: phases that scale rigor to the task, run the scientific method and leave a decision trail a person can audit after stepping away.

## Start

Open a todo list whose first item is reading the principles index in `../mode/SKILL.md`.
Then add the phases below as todos.

## Phase A: Frame

Ground yourself in the code first, then commit to:

- The definition of done as a falsifiable predicate, per `../mode/principles/prove-it-works.md`.
- The scope, quantified in rough units and effort, with the blockers that grounding found.
- The rigor level, biased high.
  One-way doors and a wide blast radius get more, and reversible low-stakes steps get less.
  Rigor means gates and artifacts, not trying harder.

Present the framing and tradeoffs before a long run.
Reversible work goes ahead, but a run of several hours earns one checkpoint with the user.

## Phase B: Design the workflow

Break the work into small units that each land on their own, riskiest unknown first.
Scaffolding and verification come before features, per `../mode/principles/foundational-thinking.md`.

- Build the verification harness before the work, with a baseline from the state before the change.
- For a one-way-door design decision, run `../architect/SKILL.md`.
  Skip it for mechanical work whose shape is already concrete.
- Decide what fans out.
  Parallelize only across real seams, and give each worker its own worktree or branch.
- Write the phase list down, because that list is what the user reviews.

Then add the designed steps to the todo list between Phase C and Phase D, and run each one under the Phase C discipline.

## Phase C: Run the loop

Each unit is an experiment: state the hypothesis, make the smallest change, measure against the predicate on the real artifact, keep it if it advanced and revert it if it did not.

- Verify by inspecting the artifact, never a self-report.
  When something passes too easily, suspect the observation method.
- Pair delegated work with a check.
  If a worker games the check, reset and tighten the contract.
  If the check itself is wrong, fix it in its own change.
- A verdict is VERIFIED, NOT VERIFIED or INCONCLUSIVE, and inconclusive is not a pass.

## Phase D: Keep the audit trail

Log the run with `../show-me-your-work/SKILL.md`, a row as each step lands.
Work of this size usually earns a committed trail, so the reviewer can read it next to the diff.

## Phase E: Verify and hand back

Check the whole against the Phase A predicate on the real product, not only the harness.
Encode any recurring correction as a check, per `../mode/principles/encode-lessons-in-structure.md`.

**Reply:** the playbook you designed, the rigor level and why, the decision log path, what is verified against the predicate and what is still open.
