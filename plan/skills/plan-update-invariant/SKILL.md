---
name: plan-update-invariant
description: |
  Internal — invoked only by the plan hub skill and plan-cascade. Never invoke directly; if
  invoked without that calling context, redirect the caller to plan.
  Mutates or removes one Invariants row, then invokes plan-cascade for the rows it invalidates.
user-invocable: false
argument-hint: mode=<update|remove> inv_id=<INV-XX> field=<Invariant|Basis> new_value=<value> marker=<U|V|A>
allowed-tools: [Read, Edit, Skill]
metadata:
  version: 0.1.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 0.1.0
---

# plan-update-invariant

## Guard Clause

If invoked with no `plan` or `plan-cascade` calling context, respond that this is internal, name `plan`, and stop.

## Args

- `mode` — required. `update` or `remove`. The caller selects it; this skill does not infer it.
- `inv_id` — required. Must match an existing `INV-XX` row.
- `field` — required for `update`. `Invariant` or `Basis`.
- `new_value` — required for `update`. Already confirmed with the practitioner by the calling hub.
- `marker` — required when `field` is `Invariant`. `U`, `V`, or `A`. Never `D` — an invariant describes what already holds, so it cannot be deduced from rows in this plan.

The investigation gate has already run upstream of this call. Write exactly what was confirmed; never re-verify the basis here.

## Write

**`update`:** in `## Invariants`, find the row where `#` matches `inv_id`. Set the `field` column to `new_value`. When `field` is `Invariant`, prefix the cell with `[<marker>]`.

**`remove`:** delete the row. Its `INV-XX` is retired, never reissued — a later row takes the next unused number.

Then, both modes:

`Skill(skill: "plan-cascade", args: "break_point=Invariants changed_item_id=<inv_id> change_type=<modification|deletion>")`

An Invariants row is cited by Design Decisions, Failure Modes, Files Touched and Implementation Order, so a change here never terminates at this row.

## Completion Tag

Carry cascade's reached-row list through unchanged — the hub writes the Revision Log from it.

- `PLAN_UPDATE_INVARIANT_OK: <inv_id> — <mode>, <field or "row removed">, cascade reached <rows or "nothing">`
- `PLAN_UPDATE_INVARIANT_BLOCKED: <reason>` — only if `inv_id` has no matching row
