# 0001 - Record architecture decisions

Status: Accepted
Date: 2026-11-13

## Context

This project makes many tool choices that interact, and the reasons behind them are easy to lose.
A future contributor, or the maintainer on a new machine, needs to know why a choice was made and what was rejected.

## Options considered

- Keep reasoning in commit messages only, which scatters it and hides rejected options.
- Keep one large design document, which drifts out of date.
- One short numbered record per decision, which can be superseded individually.

## Decision

Record each significant decision as one numbered Markdown file in `docs/adr/`, using `0000-template.md`.

## Consequences

Decisions stay reviewable and cheap to revisit.
Every record must carry evidence tags so unverified claims are never presented as facts.
