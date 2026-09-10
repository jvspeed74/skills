---
name: plan-cascade
description: |
  Internal — invoked only by the plan hub skill and the four plan-update atomics. Never
  invoke directly; if invoked without that calling context, redirect the caller to plan.
  Walks forward from a mutated section through every section that cites it, and reports
  what it reached. Recording the change is the hub's job, not this skill's.
user-invocable: false
argument-hint: break_point=<Invariants|Requirements|Design Decisions|Files Touched> changed_item_id=<INV-XX|FR-XX|NFR-XX|DD-XX|path> change_type=<modification|deletion>
allowed-tools: [Read, Edit, Grep, Skill]
metadata:
  version: 0.2.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 1.3.3
---

# plan-cascade

## Guard Clause

If invoked with no `plan` or `plan-update-*` calling context, respond that this is internal, name `plan`, and stop.

## Args

- `break_point` — required. The section holding the mutated row.
- `changed_item_id` — required. `INV-XX`, `FR-XX`, `NFR-XX`, `DD-XX`, or the file path for a Files Touched row. Every check below keys on this string.
- `change_type` — required. `modification` or `deletion`.

The calling atomic has already written its row. Never rewrite that row here.

## Traversal

| `break_point` | Sections walked, in order |
|---|---|
| Invariants | Design Decisions → Files Touched → Failure Modes → Implementation Order |
| Requirements | Design Decisions → Files Touched → Failure Modes → Implementation Order |
| Design Decisions | Files Touched → Failure Modes → Implementation Order |
| Files Touched | Implementation Order |

Advance to the next section only once the current one is resolved with the practitioner. Precede each with its signpost:

```
Cascade — <section>, triggered by <changed_item_id> (<change_type>)
```

A section with no match is resolved by saying so. Silence is not a result.

## Checks

**Design Decisions** — search `Satisfies` for `changed_item_id`. On `modification`, confirm the decision still holds against the changed row. On `deletion`, the decision now satisfies nothing: it names a replacement, or it goes. Write through `plan-update-design-decision`.

**Files Touched** — search `Why` for `changed_item_id`. On `modification`, confirm the file still changes for that reason. On `deletion`, the row has no justification on record: it names another, or the file leaves the plan. Write through `plan-update-files-touched`.

**Failure Modes** — search `Behavior` for `changed_item_id`. A mode citing it as its preventer has lost that preventer, so its `Accepted?` verdict returns to the practitioner rather than carrying forward. Write inline — Failure Modes has no atomic.

**Implementation Order** — search `Files` and `Implements` for `changed_item_id`. On `modification`, confirm the step still carries it out. On `deletion`, drop the citation, and the step with it when nothing remains for that step to do. Write inline.

## Completion Tag

Name every row reached. The hub writes the Revision Log entry from this line, and can record only what this line reports.

- `PLAN_CASCADE_OK: <changed_item_id> — reached <row IDs, comma-separated, or "nothing">`
- `PLAN_CASCADE_BLOCKED: <reason>` — only if no `PLAN__*.md` is present to walk
