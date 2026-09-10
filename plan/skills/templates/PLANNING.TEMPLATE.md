---
template_version: "1.4.0"
---

# Implementation Plan: [Task Name]
<!--
  PURPOSE:  The single pre-implementation record for one task. Establishes what
            must be true before code changes begin, locks the chosen approach
            against its alternatives, and enumerates the full blast radius —
            so that implementation is execution against a decided plan, not a
            second design pass in disguise.

  AUDIENCE: The implementing agent, and the reviewer who must issue the
            execute signal before implementation starts.

  WHEN TO WRITE:  Before any implementation action, once the task is judged to
                  warrant a plan (spans more than one file, involves a
                  non-trivial design decision, is irreversible, or has
                  ambiguously stated scope).

  WHEN TO UPDATE: If scope changes materially after the plan is approved and
                  before implementation completes, stop, revise the affected
                  sections, audit the entire plan for consistency, and obtain a new 
                  execute signal before continuing. Do not silently absorb 
                  scope changes into Implementation Order.

  DOES NOT CONTAIN: The implementation itself (code, diffs, commands run).
                    Tasks not in scope for this plan (see Non-goals — name
                    them, don't plan them). Narrative of how the plan was
                    discussed; this is the decided record, not the transcript.

  APPROVAL GATE: Implementation must not begin until this plan receives an
                 explicit execute signal from the reviewer — an unambiguous
                 instruction to proceed (e.g. "proceed", "implement this",
                 "go ahead"). Acknowledgment ("looks fine", "makes sense") and
                 silence are not execute signals.

  AUTHORING NOTE: Each section below carries its own guidance comment. Keep
                  guidance comments intact in the finished plan — do not
                  delete them once a section is filled in. Default to tables
                  for structured content; use prose only where the
                  information is genuinely narrative. Leave a section's
                  table present with zero rows (not deleted) if nothing
                  applies — an absent section is indistinguishable from a
                  skipped one.

  ID STABILITY:   Every ID (INV-XX, FR-XX, NFR-XX, NG-XX, DD-XX, FM-XX, RK-XX,
                  OQ-XX, S-XX) is permanent once assigned. Never renumber an
                  existing row to keep a series tidy — a later revision may
                  depend on that exact ID (e.g. Implementation Order cites
                  S-XX in Depends On). A new row takes the next unused
                  number in its series, regardless of where it lands in
                  the table.

  PROVENANCE:     Every row records where its content came from, as a marker
                  prefixing the row's claim cell — named per section below —
                  plus a second marker on any cell a section designates as
                  the reviewer's to decide:

                    [U] User      — the reviewer stated it, chose it, or
                                    accepted it
                    [V] Verified  — established against a source this plan
                                    can name: a file, a command's output, a
                                    document, a measurement
                    [D] Derived   — deduced from other rows in this plan;
                                    name them, as [D::DD-XX, FR-XX]
                    [A] Assumed   — none of the above

                  Nothing may be written from inference. If content is
                  neither the reviewer's, nor verifiable against a nameable
                  source, nor derived from rows already here, ask — do not
                  fill it in. An assumption is never a finished state: [A]
                  fails the PRE-EXECUTE CHECK, which is blocking and not
                  waivable. The value exists so a draft can be honest about
                  a gap, not so a gap can reach an execute signal.

                  Two sections are exempt and say so in their own guidance:
                  Open Questions, whose rows record what is not known and so
                  assert nothing, and Revision Log, whose rows record this
                  document's own history rather than claims about the design.
-->

---

## Problem Statement
<!-- One paragraph per distinct issue. Name what is broken, missing, or
     needed, and for whom or why now. Do not describe the solution here —
     that is what Design Decisions is for. If this section and Design
     Decisions end up saying the same thing, the problem statement has
     drifted into solutioning.

     Provenance: the marker prefixes the statement. The problem is the
     reviewer's to state — an agent may sharpen the wording, but cannot
     originate what the problem is. -->

[U] [Problem statement here]

---

## Invariants
<!-- Existing behavior, guarantees, or limits this task must not violate —
     not a description of current behavior for its own sake. A row belongs
     here only if it is cited by at least one Design Decision or Failure
     Mode below (see PRE-EXECUTE CHECK); an invariant nothing else cites is
     either irrelevant to this plan or a sign a Design Decision is missing.

     Provenance: the marker prefixes `Invariant`, and `Basis` names the
     source that establishes it. Where the reviewer asserts an invariant no
     available source can establish, `Basis` records that it rests on their
     assertion instead. An invariant describes what already holds, so it can
     never be deduced from other rows in this plan. -->

| # | Invariant | Basis |
|---|---|---|
| INV-01 | [U] / [V] / [A] [What must remain true — a guarantee, a behavior, a limit] | [What currently enforces or evidences it — code, contract, measurement] |

---

## Requirements

### Functional Requirements
<!-- What the result must do. One row per atomic, independently verifiable
     behavior. Use EARS (Easy Approach to Requirements Syntax):

       Pattern       Keyword(s)    Sentence structure
       ─────────────────────────────────────────────────────────────────
       Ubiquitous    (none)        The [system] shall [response]
       Event         WHEN          WHEN [trigger] the [system] shall [response]
       State         WHILE         WHILE [state] the [system] shall [response]
       Unwanted      IF / THEN     IF [precondition] THEN the [system] shall [response]
       Optional      WHERE         WHERE [feature included] the [system] shall [response]

     Use 'shall' — not 'should', 'will', or 'must'. Pattern keywords are
     ALL-CAPS. Patterns may combine: WHILE [state], WHEN [trigger] the
     [system] shall [response].

     Verification must name a concrete check — a test, a repro procedure, or
     an observable condition. "Code review" is not a verification method for
     a functional requirement; it is not a check against the requirement's
     own text.

     Provenance: the marker prefixes `Requirement`. A functional requirement
     is the reviewer's intent. Decomposing one aggregate ask into several
     atomic rows does not make those rows derived — their source is still
     what the reviewer said, not another row in this plan. -->

| # | Requirement | Verification |
|---|---|---|
| FR-01 | [U] [WHEN/WHILE/IF/WHERE ...] the [system] shall [response] | [Test name, repro steps, or observable condition] |

### Non-Functional Requirements
<!-- How the result must perform. "Measurable" is required — "fast" is not
     an NFR, "P99 latency ≤ 500ms" is. Same EARS syntax as above; the
     Threshold column carries the measurable target.

     Provenance: two markers. One prefixes `Requirement`, on the same basis
     as a functional requirement above. One prefixes `Threshold`: either the
     reviewer named the number, or it was measured and `Verification` names
     the measurement's source. A threshold that is neither is an assumption,
     and an assumption fails the check. -->

| # | Requirement | Threshold | Verification |
|---|---|---|---|
| NFR-01 | [U] WHILE [condition] the [system] shall [quality attribute] | [U] / [V] / [A] [Measurable target] | [How this is checked] |

---

## Non-goals
<!-- Capabilities adjacent to this task that this plan explicitly does not
     attempt. Naming them here catches scope creep during implementation and
     tells a reviewer that an omission was deliberate, not missed. If a
     capability belongs in scope, it's a Requirement above, not a non-goal.

     Provenance: the marker prefixes `Excluded Capability`. What is out of
     scope is the reviewer's call — an agent may propose candidates, but an
     exclusion is not recorded here until they confirm it. -->

| # | Excluded Capability | Reason |
|---|---|---|
| NG-01 | [U] [Capability name] | [Why it's excluded — out of scope, belongs to another task, deferred] |

---

## Design Decisions
<!-- One row per non-obvious choice — if a reviewer could reasonably ask "why
     not X instead?", it belongs here. Obvious choices given the constraints
     don't need a row.

     Satisfies: the Requirement, Non-goal, or Invariant # (FR-XX, NFR-XX,
     NG-XX, or INV-XX) that justifies the choice. A decision satisfying none
     of these is either unnecessary or the requirement/invariant it needs
     is missing above — fix whichever is true before proceeding.

     Alternatives Rejected: one clause per alternative with the specific
     reason it was not chosen — constraint, risk, complexity, or cost.
     Specific enough that the rejection is reproducible by someone who
     wasn't in the room. "Simpler" is not a reason; "avoids introducing a
     second persistence mechanism" is.

     Provenance: the marker prefixes `Resolution`, which is both this row's
     claim and the cell the reviewer owns. Where two or more alternatives
     were viable, the reviewer chose — selecting among viable options is
     never the agent's call. Recording the resolution as verified instead
     asserts that exactly one option was ever viable, and obliges
     `Alternatives Rejected` to show why each other option was non-viable
     rather than merely less attractive. A resolution is never derived and
     never assumed. -->

| # | Decision Point | Resolution | Satisfies | Alternatives Rejected |
|---|---|---|---|---|
| DD-01 | [The question being resolved] | [U] / [V] [The chosen answer, stated as fact] | [FR-01, NFR-01, INV-01, ...] | [Alternative — why rejected; Alternative — why rejected] |

---

## Files Touched
<!-- Full blast radius, enumerated before a line is written. One row per
     file. Why cites the Design Decision, Requirement, or Invariant #
     driving the change — a file with no citation is a change with no
     justification on record.

     Provenance: the marker prefixes `What Changes`. The file set is
     generally deduced from the decisions above, in which case the marker
     names the decision it follows from. Where investigation established the
     change directly — a path that must move regardless of which option was
     taken — the marker records it as verified against that source. -->

| File | Operation | What Changes | Why |
|---|---|---|---|
| [path] | Create / Modify / Delete / Rename | [V] / [D::DD-XX] / [A] [What changes in this file] | [DD-01 / FR-01 / NFR-01 / INV-01 / ...] |

---

## Failure Modes
<!-- Mechanistic, system-internal: a specific trigger produces a specific,
     deterministic outcome. If the concern is probabilistic, external, or
     about delivery rather than behavior, it belongs in Risks below, not here.

     Severity:
       Low      — recoverable; no output impact
       Medium   — degraded output; may need operator action
       High     — operation halts; no output produced; requires intervention
       Critical — silent wrong output; no automated detection

     Accepted?: Yes/No. If No, a Requirement, Design Decision, or Invariant
     above must prevent this mode — cite it (FR-#, NFR-#, DD-#, or INV-#) in
     Behavior. If Yes, state why the outcome is tolerable inline; an
     unexplained "Yes" is not a verdict.

     Provenance: two markers. One prefixes `Behavior`, recording whether the
     behavior was established from a named source or follows from rows
     above. One prefixes `Accepted?`, which is always the reviewer's —
     accepting a failure mode is accepting risk on their behalf, so the
     verdict is theirs every time, including when it looks obvious. -->

| # | Trigger | Behavior | Severity | Accepted? |
|---|---|---|---|---|
| FM-01 | [Specific input/state that causes this] | [V] / [D::DD-XX] / [A] [What happens — cite the preventing DD-# / FR-# / NFR-# / INV-# if Accepted = No] | Low / Medium / High / Critical | [U] Yes / No — [why] |

---

## Risks
<!-- Delivery- and execution-level uncertainty: external dependencies,
     estimation uncertainty, unfamiliar tooling, unknowns that affect
     whether or when this plan succeeds — not deterministic system behavior
     (that's Failure Modes above).

     Likelihood:
       Low    — unlikely under normal conditions
       Medium — plausible given known unknowns
       High   — expected to occur absent mitigation

     Impact:
       Cosmetic   — noticeable but no functional consequence
       Degraded   — reduced quality or performance, system still functions
       Breaking   — a requirement above is not met
       Irreversible — cannot be undone once it occurs

     Mitigation must be a concrete action, not a hope — "monitor and abort if
     X" is a mitigation; "be careful" is not.

     Provenance: the marker prefixes `Risk`, recording whether the agent
     identified it or the reviewer raised it. Likelihood and Impact are
     estimates covered by the row's own marker and take none of their own. A
     `Mitigation` that changes the approach or scope rather than operating
     within it carries its own marker, and that one is the reviewer's — a
     mitigation of that kind is a design decision in all but name. -->

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RK-01 | [U] / [V] / [D::DD-XX] / [A] [What could go wrong in delivering this] | Low / Medium / High | Cosmetic / Degraded / Breaking / Irreversible | [Concrete mitigating action] |

---

## Open Questions
<!-- Unresolved decisions and what they block. Delete a row once resolved —
     fold the answer into the relevant section above (Requirements, Design
     Decisions, etc.) rather than marking it answered in place. This plan is
     a one-shot pre-implementation record, not a persistent audit trail;
     unlike a living system-of-record document, there is no value in
     preserving resolved questions here once their answer lives elsewhere.

     Provenance: exempt, deliberately. These rows record what is not yet
     known, so they assert nothing and carry no marker. A missing marker
     here is correct rather than an omission — which is why the exemption is
     written down instead of left to inference. -->

| # | Question | Blocks |
|---|---|---|
| OQ-01 | [Unresolved question] | [Which Decision # or Requirement # this gates] |

---

## Implementation Order
<!-- Dependency-ordered execution sequence, one row per step. Row order IS
     execution order — Depends On is for a prerequisite other than the
     immediately preceding row.

     Files: bare file path(s) from Files Touched changed in this step. What
     changes in each file is Files Touched's job — do not restate it here.

     Implements: DD-XX this step carries out — or FR-XX / NFR-XX / INV-XX
     directly, when no Design Decision mediates the step. Use — for a
     purely mechanical step (scaffolding, config, rename) with nothing to
     cite.

     Depends On: S-XX of a non-adjacent prerequisite, plus a short reason —
     state the reason only when the dependency isn't obvious from the order
     itself ("S-02 depends on S-01" needs no explanation; "S-04 depends on
     S-01, not S-03 — reuses the schema S-01 creates" does). Use — when a
     step simply follows the row above with no dependency worth naming.

     Use — (not a blank cell) whenever a column has nothing to enter — a
     blank cell is indistinguishable from one that was missed.

     Provenance: the marker prefixes `Step`. The sequence is generally
     deduced from the decisions and file set above, in which case the marker
     names what each step carries out. Where the reviewer dictated an
     ordering this plan's own content does not imply, the marker records it
     as theirs instead. -->

| # | Step | Files | Implements | Depends On |
|---|---|---|---|---|
| S-01 | [U] / [D::DD-XX] / [A] [Imperative action] | [path, path] | [DD-01 / FR-01 / NFR-01 / INV-01 / —] | [S-XX — reason, or —] |

---

## Revision Log
<!-- Records only what cascade touched: a change made after this plan
     received an execute signal, together with the rows that change
     invalidated downstream. A direct edit that propagated nowhere is not
     recorded here — the plan's current state already reflects it.

     Append only. Never edit or delete an existing row. Adding a row means
     the plan no longer matches what was approved, so a new execute signal
     is required before implementation continues.

     Provenance: exempt. These rows record this document's own history
     rather than claims about the design, so they carry no marker. -->

| Date | Mutated Row | Propagated Into | Resolution |
|---|---|---|---|
| YYYY-MM-DD | [DD-XX / FR-XX / NFR-XX / INV-XX / file path] | [Every row cascade reached] | [What was done to each — updated, removed, or confirmed still valid] |

---

<!-- PRE-EXECUTE CHECK — verify before requesting the execute signal:
       - Open Questions has zero rows — an unresolved question is a reason
         to withhold the execute signal, not a footnote to note and proceed
         past.
       - Every Invariant # (INV-XX) is cited by at least one Design Decision
         or Failure Mode.
       - Every Requirement # (FR-XX, NFR-XX) appears in at least one Design
         Decision's Satisfies column.
       - Every Files Touched row cites a Design Decision, Requirement, or
         Invariant #.
       - Every Failure Mode with Accepted = No cites the Design Decision,
         Requirement, or Invariant that prevents it.
       - Every Files Touched path appears in at least one Implementation
         Order step's Files column, and every Design Decision # (DD-XX)
         appears in at least one step's Implements column.
       - Every row carries its provenance marker, and every cell this
         template designates as the reviewer's carries its own — excepting
         Open Questions and Revision Log, exempt by design.
       - No marker anywhere is [A].
       - Every [D] names the rows it was derived from.
       - Every Design Decisions `Resolution` marked [V] is backed by an
         `Alternatives Rejected` cell showing each alternative was
         non-viable, not merely less attractive. A viable alternative that
         was passed over means the marker should have been [U].
       - Every Failure Modes `Accepted?` is [U].
       - Every Design Decision's `Satisfies` names at least one Requirement,
         Non-goal or Invariant. A decision satisfying nothing is either
         unnecessary, or the row it needed is missing above.
     This check is blocking and not waivable. A finding is resolved by
     fixing the plan, never by noting it and proceeding — a gap here means
     the plan is incomplete, not that the check is too strict. -->
