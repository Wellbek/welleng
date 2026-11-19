# Prototype

You own the design decision, not the code.
The prototype is a throwaway instrument, and the real build follows the feature playbook.

Speed beats polish here.
The rigor is in picking the right design cheaply, so propose variations the user did not ask for.

1. Name the decision the prototype exists to make, such as a layout, an interaction, a density, or for an empirical fork a behavior, a timing or an approach.
   No decision means no prototype.
2. When the design space is open, gather prior art and let the user pick directions before you build.
3. Build in a scratch directory outside the production source.
   For a visual decision, use plain HTML, CSS and JavaScript or the lightest stack that renders the idea.
   For a behavioral or timing decision, write the smallest script that exercises the question.
   No production framework, no tests, no abstractions.
4. Put alternatives behind one switcher, such as buttons or a key press, with each variant labelled, per `principles/exhaust-the-design-space.md`.
5. Observe the thing you are deciding.
   Screenshot each visual variant and drive the interaction, or log the timing and the output.
6. Present the alternatives, the tradeoffs and a recommendation, then hand the chosen direction to `playbooks/feature.md`.

**Reply:** the variants, the evidence, the tradeoffs, your recommendation and the scratch path.
Say plainly that the prototype is throwaway.
