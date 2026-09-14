---
name: plan-update-postulate
description: |
  Internal — invoked only by the plan hub skill and plan-cascade. Never invoke directly; if
  invoked without that calling context, redirect the caller to plan.
  Mutates or removes one Postulates row, then invokes plan-cascade for the rows it invalidates.
user-invocable: false
argument-hint: mode=<update|remove> ps_id=<PS-XX> field=<Postulate|Basis|Cost|Detected> new_value=<value> marker=<U|V|A>
allowed-tools: [Read, Edit, Skill]
metadata:
  version: 0.1.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 0.1.0
---

# plan-update-postulate

## Guard Clause

If invoked with no `plan` or `plan-cascade` calling context, respond that this is internal, name `plan`, and stop.

## Args

- `mode` — required. `update` or `remove`. The caller selects it; this skill does not infer it.
- `ps_id` — required. Must match an existing `PS-XX` row.
- `field` — required for `update`. `Postulate`, `Basis`, `Cost` or `Detected`.
- `new_value` — required for `update`. Already confirmed with the practitioner by the calling hub.
- `marker` — required when `field` is `Postulate`. `U`, `V`, or `A`. Never `D` — a Postulate is external to the thing it governs, so it cannot be deduced from rows in this plan.

The Postulate gate has already run upstream of this call: the four mechanisms were run, the four negative tests applied, and the result confirmed with the practitioner. Write exactly what was confirmed. Do not re-run a mechanism here.

A change to `Cost` carries the same obligation the gate does — "unestablished" is a permitted value and is not the same as none.

## Write

**`update`:** in `## Postulates`, find the row where `#` matches `ps_id`. Set the `field` column to `new_value`. When `field` is `Postulate`, prefix the cell with `[<marker>]`.

**`remove`:** delete the row. Its `PS-XX` is retired, never reissued — a later row takes the next unused number.

Then, both modes:

`Skill(skill: "plan-cascade", args: "break_point=Postulates changed_item_id=<ps_id> change_type=<modification|deletion>")`

A Postulate is upstream of everything the plan holds: every aspect of the thing's shape traces to it, so a change here reaches Invariants, Design Decisions, Files Touched, Failure Modes and Implementation Order in turn. This is the widest traversal in cascade's table, and a change here never terminates at this row.

## Completion Tag

Carry cascade's reached-row list through unchanged — the hub writes the Revision Log from it.

- `PLAN_UPDATE_POSTULATE_OK: <ps_id> — <mode>, <field or "row removed">, cascade reached <rows or "nothing">`
- `PLAN_UPDATE_POSTULATE_BLOCKED: <reason>` — only if `ps_id` has no matching row
