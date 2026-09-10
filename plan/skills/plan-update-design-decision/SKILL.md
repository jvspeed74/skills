---
name: plan-update-design-decision
description: |
  Internal — invoked only by the plan hub skill and plan-cascade. Never invoke directly; if
  invoked without that calling context, redirect the caller to plan.
  Writes one Design Decisions row — on initial authoring as well as on mutation — and
  invokes plan-cascade for the rows a mutation invalidates.
user-invocable: false
argument-hint: mode=<create|update|remove> dd_id=<DD-XX, omit for create> decision_point=<text> resolution=<text> marker=<U|V> satisfies=<ID list> alternatives=<one clause per rejected option> field=<Decision Point|Resolution|Satisfies|Alternatives Rejected> new_value=<value>
allowed-tools: [Read, Edit, Skill]
metadata:
  version: 0.2.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 1.3.3
---

# plan-update-design-decision

## Guard Clause

If invoked with no `plan` or `plan-cascade` calling context, respond that this is internal, name `plan`, and stop.

## Args

- `mode` — required. `create`, `update`, or `remove`. This is the one atomic that fires on initial authoring, because the failure it guards against — a resolution written before the alternatives were weighed — happens on the first write.
- `dd_id` — required for `update` and `remove`. Omit for `create`; this skill assigns it.
- `decision_point`, `resolution`, `satisfies`, `alternatives` — required for `create`. All four already confirmed with the practitioner by the calling hub.
- `field`, `new_value` — required for `update`.
- `marker` — required whenever `resolution` is written, on `create` or `update`. `U` or `V` only; never `D`, never `A`. `V` asserts that exactly one option was ever viable, which obliges `alternatives` to establish each other option as non-viable rather than less attractive. Where two or more were viable, the practitioner chose and the marker is `U`.

The design decision gate has already run upstream of this call: alternatives identified from investigation, and the choice taken from the practitioner.

## Write

**`create`:** read `## Design Decisions`, take the highest existing `DD-XX`, add one. Append:

| # | Decision Point | Resolution | Satisfies | Alternatives Rejected |
|---|---|---|---|---|
| `<new id>` | `<decision_point>` | `[<marker>] <resolution>` | `<satisfies>` | `<alternatives>` |

No cascade call. Nothing cites a decision that did not exist a moment ago.

**`update`:** find the row where `#` matches `dd_id`. Set the `field` column to `new_value`. When `field` is `Resolution`, prefix the cell with `[<marker>]`.

**`remove`:** delete the row. Its `DD-XX` is retired, never reissued.

Then, `update` and `remove` only:

`Skill(skill: "plan-cascade", args: "break_point=Design Decisions changed_item_id=<dd_id> change_type=<modification|deletion>")`

A decision is cited by Files Touched, Failure Modes and Implementation Order, so a change here never terminates at this row.

## Completion Tag

Carry cascade's reached-row list through unchanged — the hub writes the Revision Log from it.

- `PLAN_UPDATE_DESIGN_DECISION_OK: <dd_id> — <mode>, <field or "row created" or "row removed">, cascade reached <rows or "not called">`
- `PLAN_UPDATE_DESIGN_DECISION_BLOCKED: <reason>` — only if `dd_id` has no matching row, or `marker=V` was passed with no `alternatives` content establishing non-viability
