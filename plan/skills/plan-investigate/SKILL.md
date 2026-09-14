---
name: plan-investigate
description: |
  Bounds an investigation before conclusions rest on it: enumerates candidate sources
  before opening any of them, establishes the rules the subject was built inside, records
  what each source settled and what was never opened, and holds the disagreements between
  them. Invoke directly before drawing findings from a body of material, or let the plan
  hub call it while authoring or revising. Not for deciding what the sources mean — that
  belongs to whoever called; this skill establishes only what governs, what was read, and
  what was not.
argument-hint: <the subject to investigate, or slug=<task-slug> when a plan is in flight>
allowed-tools: [Read, Glob, Grep, Bash, WebFetch, Write, Edit]
metadata:
  version: 0.1.0
  templates_referenced:
    PLANNING.TEMPLATE.md: 0.1.0
---

# plan-investigate

You are the practitioner's entry point for bounding an investigation. Report what governs the subject, what was covered, and what was not. Draw no conclusions from any of it — that belongs to whoever called.

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

List separately the sources that state what governs the subject rather than what it does: a philosophy or rationale document, a stated convention, an `AGENTS.md` or `CLAUDE.md`, a declared invariant register, the specification of a framework the project adopted. These are the candidates a Postulate can come from, and they are the ones an investigation drawn only from identifiers will miss — nothing in the code greps for the reason the code is shaped that way.

A candidate is anything the practitioner would be surprised to learn was skipped. Listing costs nothing and commits to nothing: an entry can move to `Not opened` with a reason.

## Read

Work the list. Record what each source established, stated in the subject's terms rather than as a summary of the file.

A source that established nothing still takes a row. A shallow investigation is characterised by the file it never opened, not by the file it read badly, so the absences are the part worth keeping.

Add candidates as reading surfaces them. Never drop one silently — an entry that will not be opened moves to `Not opened` carrying why.

Where a claim rests on exactly one source, say so in the same cell. A claim standing on one source is not thereby wrong, but a reader cannot tell one source from four unless the cell says which.

## Establishing what governs

Run all four mechanisms against every candidate rule, and record what each returned:

| Mechanism | What it asks |
|---|---|
| Stated rationale | Does any source say why this rule exists? Quote it |
| Consumer chain | What consumes the artifact this rule shapes, and what changes for that consumer if the rule is broken? Follow the chain past the immediate consumer — one hop understates the cost, because at one hop the effect is always small |
| Regularity | In how many places does the rule hold, out of how many it could? Count both |
| Reasons to change | Collect the reasons this thing would have to change. If they all trace to one assumption, that assumption is the rule. If they trace to several, there is more than one rule here and they must be separated |

Then apply the four tests. None of these is a governing rule: a stakeholder or team decision, which is a proxy for the assumption behind it; a technology, which is a choice made inside a rule's space rather than the rule; a list of change scenarios, which are the rule's dimensions rather than the rule; anything internal to the thing, which cannot author what governs it.

Record for each surviving rule what violating it would cost, how that cost was established, and what — if anything — would detect the violation. Where no mechanism settles the cost, record it as **unestablished**. That is a different answer from *nothing*, and writing *nothing* where *unestablished* is true is the failure this step exists to prevent: prose with no failing test reads as costless to anything that only looks for a failing test.

State which mechanisms were independent of the stated rationale. Four mechanisms that all observe consequences of one root cause are one source counted four times, and a corroboration claim that does not separate those cases carries no information.

## Record

Write to `INVESTIGATION__<slug>.md`: beside the plan when a slug was given, otherwise in the session scratchpad under a slug derived from the subject. On a revision, append under a dated heading rather than replacing — the record accretes across revisions, and an earlier pass's absences stay visible.

| Source | Established |
|---|---|
| `<path, URL, or command>` | `<what it settled, or "nothing"; whether it stands alone>` |

| Governing rule | Basis | Cost | Detected |
|---|---|---|---|
| `<the rule the subject has no authority over>` | `<which mechanisms returned what, and which were independent>` | `<what violating it costs, and how established — or "unestablished">` | `<what would catch a violation, or "nothing">` |

| Conflict | What each states |
|---|---|
| `<the two sources that disagree>` | `<what each says, and on what the plan depends>` |

| Not opened | Why |
|---|---|
| `<candidate>` | `<why it was set aside>` |

A conflict is a finding, not a problem to resolve here. Where a document and an implementation disagree, both readings are recorded and neither is silently preferred — including where the project states which source wins, since a stated precedence rule can be declared and still be wrong in practice.

Where no source of governing intent exists, say so, name what was searched for it, and record that the subject's rules are unstated. Do not infer them from the code alone: code shows what was done, never what was intended.

## Sufficiency

Close with a sufficiency claim, and qualify it. Name what the read set supports, then name every gap in it: a candidate left unopened that a conclusion may still rest on, a claim resting on documentation rather than observation, a neighbour never followed, a rule whose cost stayed unestablished.

Never write the bare word sufficient. An unqualified claim reads identically whether the gaps were examined or never looked for, and the practitioner has no way to tell the two apart.

## Completion Tag

- `PLAN_INVESTIGATE_OK: <slug> — <N> consulted, <N> not opened, <N> governing rules, <N> conflicts, sufficiency qualified`
- `PLAN_INVESTIGATE_BLOCKED: <reason>` — only if the subject names no candidate source at all
