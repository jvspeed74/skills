---
name: plan-investigate
description: |
  Bounds an investigation before conclusions rest on it: enumerates candidate sources
  before opening any of them, records what each established, and records what was never
  opened and why. Invoke directly before drawing findings from a body of material, or let
  the plan hub call it while authoring or revising. Not for deciding what the sources mean
  — that belongs to whoever called; this skill establishes only what was and was not read.
argument-hint: <the subject to investigate, or slug=<task-slug> when a plan is in flight>
allowed-tools: [Read, Glob, Grep, Bash, WebFetch, Write, Edit]
metadata:
  version: 0.1.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 1.4.0
---

# plan-investigate

You are the practitioner's entry point for bounding an investigation. Report what was covered and what was not. Draw no conclusions from either — that belongs to whoever called.

## Gate

| Gate | Trigger | Must verify | If it fails |
|---|---|---|---|
| Enumeration gate | Before any source is opened | A written candidate list exists, naming every source the subject plausibly rests on | Enumerate first. A list assembled after reading records what was recalled, not what was skipped |

## Candidates

Draw the list from the subject:

- Files, directories and URLs it names outright.
- What a grep for its identifiers returns.
- Documentation for any tool, API, format or flag it depends on.
- The neighbours of whatever is already listed — callers, callees, siblings in the same directory.

A candidate is anything the practitioner would be surprised to learn was skipped. Listing costs nothing and commits to nothing: an entry can move to `Not opened` with a reason.

## Read

Work the list. Record what each source established, stated in the subject's terms rather than as a summary of the file.

A source that established nothing still takes a row. A shallow investigation is characterised by the file it never opened, not by the file it read badly, so the absences are the part worth keeping.

Add candidates as reading surfaces them. Never drop one silently — an entry that will not be opened moves to `Not opened` carrying why.

## Record

Write to `INVESTIGATION__<slug>.md`: beside the plan when a slug was given, otherwise in the session scratchpad under a slug derived from the subject. On a revision, append under a dated heading rather than replacing — the record accretes across revisions, and an earlier pass's absences stay visible.

| Source | Established |
|---|---|
| `<path, URL, or command>` | `<what it settled, or "nothing">` |

| Not opened | Why |
|---|---|
| `<candidate>` | `<why it was set aside>` |

## Sufficiency

Close with a sufficiency claim, and qualify it. Name what the read set supports, then name every gap in it: a candidate left unopened that a conclusion may still rest on, a claim resting on documentation rather than observation, a neighbour never followed.

Never write the bare word sufficient. An unqualified claim reads identically whether the gaps were examined or never looked for, and the practitioner has no way to tell the two apart.

## Completion Tag

- `PLAN_INVESTIGATE_OK: <slug> — <N> consulted, <N> not opened, sufficiency qualified`
- `PLAN_INVESTIGATE_BLOCKED: <reason>` — only if the subject names no candidate source at all
