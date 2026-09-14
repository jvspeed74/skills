---
name: plan-update-files-touched
description: |
  Internal — invoked only by the plan hub skill and plan-cascade. Never invoke directly; if
  invoked without that calling context, redirect the caller to plan.
  Mutates or removes one Files Touched row, then invokes plan-cascade for the steps it
  invalidates.
user-invocable: false
argument-hint: mode=<update|remove> path=<file path> field=<File|Operation|What Changes|Why> new_value=<value> marker=<V|D|A> derived_from=<DD-XX, when marker=D>
allowed-tools: [Read, Edit, Skill]
metadata:
  version: 0.1.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 0.1.0
---

# plan-update-files-touched

## Guard Clause

If invoked with no `plan` or `plan-cascade` calling context, respond that this is internal, name `plan`, and stop.

## Args

- `mode` — required. `update` or `remove`. The caller selects it; this skill does not infer it.
- `path` — required. The row's current `File` value, which identifies the row; this table has no ID column.
- `field` — required for `update`. `File`, `Operation`, `What Changes`, or `Why`. `Operation` takes `Create`, `Modify`, `Delete` or `Rename`.
- `new_value` — required for `update`. Already confirmed with the practitioner by the calling hub.
- `marker` — required when `field` is `What Changes`. `V` where investigation established the change directly, `D` where it follows from a decision, `A` where neither.
- `derived_from` — required when `marker` is `D`. The `DD-XX` the change follows from, written into the cell as `[D::<derived_from>]`.

The investigation gate has already run upstream of this call. A path reaches this skill only once confirmed to exist.

## Write

**`update`:** in `## Files Touched`, find the row where `File` matches `path`. Set the `field` column to `new_value`. When `field` is `What Changes`, prefix the cell with `[<marker>]` or `[D::<derived_from>]`.

**`remove`:** delete the row.

Then, both modes:

`Skill(skill: "plan-cascade", args: "break_point=Files Touched changed_item_id=<path> change_type=<modification|deletion>")`

Implementation Order steps cite these paths in their `Files` column, so a change here never terminates at this row. A `File` rename is a modification, not a removal — the step citing the old path must move to the new one, not lose it.

## Completion Tag

Carry cascade's reached-row list through unchanged — the hub writes the Revision Log from it.

- `PLAN_UPDATE_FILES_TOUCHED_OK: <path> — <mode>, <field or "row removed">, cascade reached <rows or "nothing">`
- `PLAN_UPDATE_FILES_TOUCHED_BLOCKED: <reason>` — only if `path` has no matching row
