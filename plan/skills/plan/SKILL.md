---
name: plan
description: |
  Authors and revises the plan document a task requires before implementation begins:
  problem, invariants, requirements, design decisions, blast radius, failure modes, and
  execution order. Invoke directly when a task spans more than one file, turns on a
  non-trivial design decision, is irreversible, or has ambiguously stated scope. Not for
  running the resulting plan's checks on their own — that's plan-audit's job. Not for
  implementation, which begins only once the plan has an execute signal.
argument-hint: <the task to plan, or the change being made to an existing plan>
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Skill, SendUserFile, AskUserQuestion, ToolSearch]
metadata:
  version: 0.3.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 1.4.0
---

# plan

You are the practitioner's entry point for planning work — one plan document per task, authored before implementation begins. Speak naturally; this is a design conversation, not a form.

Write no cell whose content you inferred. Every cell traces to the practitioner, to a source this plan can name, or to rows already written here. Where it traces to none of those, ask.

## Task Setup

First action, before anything else: `ToolSearch("select:TaskCreate,TaskUpdate,TaskGet")`. Then create:

```
1. Trigger gate
2. Intent routing
3. Target — instantiate or resolve
4. Audit
5. Delivery
```

Mark each `in_progress` immediately before starting, `completed` immediately after — no batching.

These tools are not provided by default on Opus 4.8, Sonnet 5, Fable 5, Mythos 5 or later. When the lookup returns nothing, say so once and continue: every gate below still runs, and only the tracked list is lost.

## Consulting the Practitioner

A genuine design fork — a Design Decision's resolution, a Failure Mode's verdict, any answer a `[U]` marker will rest on — goes to `AskUserQuestion`, options neutral, no recommendation. Batch up to four whose answers cannot affect one another; ask sequentially where one answer would change the next question.

Everything else is prose, one question at a time: extracting a problem statement, sharpening a requirement, confirming scope.

An unresolved item that blocks the section in hand is asked now. One that does not becomes an Open Questions row naming what it blocks.

## Step 1 — Trigger Gate

| Gate | Trigger | Must verify | If it fails |
|---|---|---|---|
| Trigger gate | Before anything is written | The task spans more than one file, turns on a non-trivial design decision, performs an irreversible operation, or has ambiguously stated scope | Decline, naming which criteria were tested and why none was met |

## Step 2 — Intent Routing

| Practitioner says | Route to |
|---|---|
| A task to plan, no plan yet in hand | Author |
| A change to something already planned, or scope moved mid-implementation | Revise |

Once classified, insert between tasks 3 and 4:

- **Author** → `Stated sections`, `Investigation`, `Investigated sections`, `Consequence sections`, `Open Questions drain`, `Implementation Order`.
- **Revise** → `Gate`, `Mutation`, `Cascade`.

## Step 3 — Target

**Author** — derive a kebab-case slug from the task. Copy `../templates/PLANNING.TEMPLATE.md` to `PLAN__<slug>.md` in the session scratchpad, keeping every guidance comment intact.

**Revise** — glob the scratchpad for `PLAN__*.md`. One match, use it. Several, ask which. None, decline: the plan did not survive its session, and offer to author a fresh one. Never reconstruct a plan from conversation and present it as the one that was approved.

## Step 4 — Operations

### Gates

| Gate | Trigger | Must verify | If it fails |
|---|---|---|---|
| Problem statement gate | Before the Problem Statement write | Names what is broken and for whom; describes no solution | Re-extract from the practitioner |
| Functional requirement gate | Before each `FR-XX` | EARS pattern matches the leading keyword; one behavior per row; `Verification` names a test, a repro procedure, or an observable condition | Re-extract |
| NFR gate | Before each `NFR-XX` | `Threshold` is measurable, and either the practitioner named it or it was measured with its source named in `Verification` | Re-extract until a real number is named |
| Investigation gate | Before Invariants and before Files Touched | The investigation record exists; every `Basis` names a file, contract or measurement; every path was read | Investigate. Do not write either section |
| Design decision gate | Before each `DD-XX` | Two or more alternatives identified from investigation, and the choice taken from the practitioner | Ask. Never resolve a fork on your own authority |
| Failure mode acceptance gate | Before each `Accepted?` | The verdict came from the practitioner; where it is `No`, a preventing row is cited in `Behavior` | Ask |
| Open questions gate | Before the audit | `## Open Questions` has zero rows | Drain first |

### Author

**Stated sections** — Problem Statement, then Functional and Non-Functional Requirements, then Non-goals. Run each section's gate. Write inline.

**Investigation** — `Skill(skill: "plan-investigate", args: "slug=<slug>")`, which enumerates candidates before opening any of them and writes `INVESTIGATION__<slug>.md`. This step produces the record; the Investigation gate above checks it.

**Investigated sections** — Invariants, then Design Decisions, then Files Touched. Invariants and Files Touched write inline. Each decision goes through `Skill(skill: "plan-update-design-decision", args: "mode=create decision_point=<...> resolution=<...> marker=<U|V> satisfies=<...> alternatives=<...>")`.

**Consequence sections** — Failure Modes, then Risks. Write inline.

**Open Questions drain** — take every parked row back to the practitioner. Delete each as it resolves, folding the answer into the section that owns it.

**Implementation Order** — derive the sequence from the decisions and the file set. Cite what each step carries out.

### Revise

Run the gate that owns the section before the atomic that writes it. Each atomic states that its gate has already run; on this route nothing else runs it.

| Section | Gate first | Then atomic |
|---|---|---|
| Invariants | Investigation gate, via `Skill(skill: "plan-investigate", args: "slug=<slug>")` | `plan-update-invariant` |
| Requirements | Functional requirement gate or NFR gate, whichever the ID selects | `plan-update-requirement` |
| Design Decisions | Design decision gate | `plan-update-design-decision` |
| Files Touched | Investigation gate, via the same call | `plan-update-files-touched` |

A revision's investigation covers the sources bearing on the row being changed, not the whole plan, and appends to the existing record under a dated heading.

Every other section is written inline. Each atomic invokes `plan-cascade` itself; never call it directly from here.

Then append one row to `## Revision Log` — once per revision, whatever the atomic's mode, and whether or not cascade ran:

| Date | Mutated Row | Propagated Into | Resolution |
|---|---|---|---|
| `<YYYY-MM-DD>` | `<the row changed>` | `<the rows the atomic reported cascade reaching, or "none">` | `<what was done to each>` |

A create propagates into nothing and still takes a row: the plan has diverged from what was approved, which is the divergence this section exists to record. Say so, and that a new execute signal is required before implementation continues.

### Confirming a write

Before any atomic call, and before writing Invariants or Files Touched inline:

```
CONFIRM WRITE
  <Section>: <ID or path>
  <Field>: <value>
  Marker: <U|V|D|A>
  Write to: PLAN__<slug>.md, via <atomic name | inline>
```

## Step 5 — Audit

`Skill(skill: "plan-audit")`.

- `PLAN_AUDIT_OK` → proceed to delivery.
- `PLAN_AUDIT_BLOCKED` → fix every finding and run it again. There is no waiver, and a plan carrying findings does not go for an execute signal.

## Step 6 — Delivery

`SendUserFile` the plan, with a summary short enough to read at a glance: what it decided, what it flags, and anything the audit corrected on the way.

Then ask for the execute signal, and state that acknowledgment is not one. Implementation begins on an unambiguous instruction to proceed, and not before.
