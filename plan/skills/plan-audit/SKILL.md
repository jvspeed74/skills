---
name: plan-audit
description: |
  Runs a plan document's pre-execute check: citation coverage, provenance markers, and the
  two section exemptions. Invoke directly to re-check a plan after revising it. Blocking —
  a finding is resolved by fixing the plan, never by waiving it. Not for authoring or
  revising a plan — that's plan's job; this skill changes nothing.
argument-hint: <nothing, or a task slug when more than one plan is present>
allowed-tools: [Read, Glob, Grep]
metadata:
  version: 0.1.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 0.1.0
---

# plan-audit

You are the practitioner's entry point for checking a plan against its own pre-execute rules. Report findings. Change nothing.

## Target

Glob the session scratchpad for `PLAN__*.md`. One match — use it. Several — ask which. None — say so and stop.

## Checks

Run all thirteen. Report every finding; never stop at the first.

| # | Finding when |
|---|---|
| 1 | `## Open Questions` has any row |
| 2 | A `PS-XX` or `INV-XX` appears in no Design Decision and no Failure Mode |
| 3 | An `FR-XX` or `NFR-XX` appears in no Design Decision's `Satisfies` |
| 4 | A Files Touched row's `Why` names no `DD-XX`, `FR-XX`, `NFR-XX`, `PS-XX` or `INV-XX` |
| 5 | A Failure Mode with `Accepted? = No` names no preventing row in `Behavior` |
| 6 | A Files Touched path appears in no step's `Files`, or a `DD-XX` in no step's `Implements` |
| 7 | A row's claim cell carries no marker, outside `## Open Questions` and `## Revision Log` |
| 8 | A `Threshold` or `Accepted?` cell carries no marker of its own |
| 9 | Any marker is `[A]` |
| 10 | A `[D]` names no source rows |
| 11 | A `Resolution` marked `[V]` has an `Alternatives Rejected` cell that establishes an alternative as less attractive rather than non-viable, or an `Accepted?` is not `[U]` |
| 12 | A Design Decision's `Satisfies` names nothing |
| 13 | A source of governing intent named in the investigation record is reflected in no Postulate and no Invariant, and is not noted there as bearing on nothing in this plan |

Check 11 is the one no search resolves: it is read, not matched. A passed-over alternative that was merely less attractive means the marker should have been `[U]`.

Check 13 runs in the opposite direction to check 2. Check 2 asks whether what was written is relevant; check 13 asks whether what mattered was written, and it is the only check that reads the investigation record rather than the plan.

## Report

One line per finding — the check number, the row it lands on, and what is missing. Then the tag.

- `PLAN_AUDIT_OK: <plan filename> — 13 checks, clean`
- `PLAN_AUDIT_BLOCKED: <plan filename> — <N> findings`

A finding is resolved by fixing the plan. There is no waiver, and a plan carrying findings does not go to the practitioner for an execute signal.
