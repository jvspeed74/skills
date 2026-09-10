---
name: plan-update-requirement
description: |
  Internal — invoked only by the plan hub skill and plan-cascade. Never invoke directly; if
  invoked without that calling context, redirect the caller to plan.
  Adds, mutates or removes one Functional or Non-Functional Requirements row, then invokes
  plan-cascade for the rows a mutation invalidates.
user-invocable: false
argument-hint: mode=<create|update|remove> table=<FR|NFR, for create> req_id=<FR-XX|NFR-XX, for update and remove> requirement=<text> threshold=<text, NFR only> verification=<text> threshold_marker=<U|V|A> field=<Requirement|Threshold|Verification> new_value=<value>
allowed-tools: [Read, Edit, Skill]
metadata:
  version: 0.3.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 1.3.3
---

# plan-update-requirement

## Guard Clause

If invoked with no `plan` or `plan-cascade` calling context, respond that this is internal, name `plan`, and stop.

## Args

- `mode` — required. `create`, `update`, or `remove`. The caller selects it; this skill does not infer it.
- `table` — required for `create`. `FR` or `NFR`. On `update` and `remove` the `req_id` prefix selects the table instead, and this argument is absent.
- `req_id` — required for `update` and `remove`. `FR-XX` selects `## Functional Requirements`, `NFR-XX` selects `## Non-Functional Requirements`. Omit for `create`; this skill assigns it.
- `requirement`, `verification` — required for `create`. Already confirmed with the practitioner by the calling hub.
- `threshold` — required for `create` when `table` is `NFR`. That table alone carries the column.
- `field` — required for `update`. `Requirement` or `Verification` for either table; `Threshold` only for an `NFR-XX`.
- `new_value` — required for `update`.
- `threshold_marker` — required whenever a `Threshold` cell is written. `U` when the practitioner named the number, `V` when it was measured, `A` when neither. A `Requirement` cell is always `[U]` and takes no argument — a requirement is the practitioner's intent, and decomposing one aggregate ask into several rows does not change whose it is.

The matching requirement gate has already run upstream of this call — EARS pattern for a functional row, a measurable target for a threshold.

## Write

**`create`:** read the table `table` names, take the highest existing ID in that series, add one. Append, `[U]` prefixing `Requirement` in both shapes:

`FR` —

| # | Requirement | Verification |
|---|---|---|
| `<new id>` | `[U] <requirement>` | `<verification>` |

`NFR` —

| # | Requirement | Threshold | Verification |
|---|---|---|---|
| `<new id>` | `[U] <requirement>` | `[<threshold_marker>] <threshold>` | `<verification>` |

No cascade call. Nothing cites a requirement that did not exist a moment ago.

**`update`:** in the table `req_id` selects, find the row where `#` matches. Set the `field` column to `new_value`. Prefix a `Requirement` cell with `[U]`, a `Threshold` cell with `[<threshold_marker>]`.

**`remove`:** delete the row. Its ID is retired, never reissued.

Then, `update` and `remove` only:

`Skill(skill: "plan-cascade", args: "break_point=Requirements changed_item_id=<req_id> change_type=<modification|deletion>")`

A requirement is cited by Design Decisions, Failure Modes, Files Touched and Implementation Order, so a change here never terminates at this row.

## Completion Tag

Carry cascade's reached-row list through unchanged — the hub writes the Revision Log from it.

- `PLAN_UPDATE_REQUIREMENT_OK: <req_id> — <mode>, <field or "row created" or "row removed">, cascade reached <rows or "not called">`
- `PLAN_UPDATE_REQUIREMENT_BLOCKED: <reason>` — only if `req_id` has no matching row, or `Threshold` was named against an `FR-XX`
