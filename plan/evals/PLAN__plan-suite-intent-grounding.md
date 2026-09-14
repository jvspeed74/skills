---
template_version: "1.4.0"
---

# Implementation Plan: Plan Suite Intent Grounding
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

[U] The suite forbids the agent from contributing engineering judgment to any decision it records. Four instructions combine to that effect: the hub routes every genuine design fork to a question card with "options neutral, no recommendation"; its design decision gate ends "Ask. Never resolve a fork on your own authority"; its preamble states "Write no cell whose content you inferred"; and the template's Design Decisions guidance reads "selecting among viable options is never the agent's call." The provenance marker set leaves nowhere else to go — `[U]` is the reviewer's choice, `[V]` asserts that exactly one option was ever viable, `[D]` is mechanical deduction from other rows, and `[A]` fails the blocking pre-execute check. No marker exists for a resolution the agent reasoned about, recommended, and the reviewer then ratified. In the LogWatcher plan, nine of ten Design Decisions and all nineteen Functional Requirements carry `[U]`. The reviewer supplies every element of design judgment in the document, and a reviewer less acclimated to the codebase gets a plan that follows their reading of the problem wherever it goes, with nothing in the process positioned to push back.

[U] This is not a limit on the agent's analytic capacity, which the same artifacts show operating at full strength on questions of fact. Unprompted, the LogWatcher investigation measured one option's cost at fifteen construction sites against another's one; identified the only downstream assertion in `HostLifecycleTests.cs` at line 100 as a tautology on a `long` that cannot fail; and found that `invariant_definition.md` lines 370–406 walk a nine-gate worked example against text the change deletes. The agent reasons hard about what is true, and is silenced at precisely the point where those truths would bear on a choice.

[U] More fundamentally, the agent is never required to establish the governing intent of the thing it modifies, so it has nothing against which to hold a choice. The Invariants section asks for "existing behavior, guarantees, or limits" and states that "an invariant describes what already holds"; the Investigation gate requires every `Basis` to name "a file, contract or measurement." Together these ground an invariant in observable properties rather than in the intentions those properties serve, and all six invariants in the LogWatcher plan are behavioral or structural facts about the code. Nor does anything verify that the invariants found were the ones that mattered: the pre-execute check confirms every listed invariant is cited by a Design Decision or Failure Mode, which tests the relevance of what was written and is silent about what was missed. An invariant never written down passes every check.

[U] Nor does the suite corroborate its sources against one another. `plan-investigate` bounds coverage — a candidate is "anything the practitioner would be surprised to learn was skipped" — and its sufficiency claim discloses "a claim resting on documentation rather than observation." Disclosure is not corroboration. A document that is inaccurate, or an implementation that has quietly drifted from the intent it was written to serve, can establish an invariant unchallenged; and where a document and the code disagree, the record has nowhere to put that disagreement, which is the finding most worth having.

[U] The prohibition earns its keep in one respect, and that must survive: it stops the agent biasing the reviewer toward an approach on grounds that would not hold under scrutiny. An agent's judgment is a function of pre-training and probability, which is why the provenance markers separate the reviewer's choices from the agent's findings at all. The defect is not that the agent defers. It is that deferring is the only thing permitted, so it never reasons to a position — and alternatives assembled by an agent that knows it may not hold one are enumerated rather than synthesized.

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
| INV-01 | [V] Altitude defines a **Postulate** as an external, foundational assumption or rule taken for granted by the thing built inside it, over which that thing has no authority — it can neither negotiate, alter nor debate it. It is inward-facing, exclusive (any change untraceable to it is misplaced or reveals the Postulate was stated too loosely), sufficient on its own to explain the thing's shape, and external to it. | Two independent sources. `altitude-framework/L5__Framework_Philosophy.md`, "The Postulate" and "What a Postulate Is Not"; corroborated by `altitude-framework/L5__Core_Concepts.md:154–166`, which names the four properties directly. |
| INV-02 | [V] Altitude defines an **Invariant** as a typed, machine-enforced guarantee about behavior crossing a module boundary, and machine-enforceability is definitional: "An architectural guarantee that cannot be machine-enforced is not an invariant — it is documentation." Its qualification test has two conditions — the behavior crosses a boundary or degrades the shared runtime, and a violation is deterministically testable without relying on OS behavior, timing or probabilistic conditions. | Two independent sources. `altitude-framework/invariant_definition.md` §1–§2; corroborated verbatim at `altitude-framework/L5__Core_Concepts.md:225–245`, which adds the two-condition qualification test and three exclusions. |
| INV-03 | [V] Altitude's enforcement against the practitioner is two-tier. Absence of an upstream document is advisory: say which is missing and why, ask whether to proceed, record the answer, "a normal conversational exchange — no fixed block." Contradiction is hard: halt immediately, no partial writes, under a fixed `UPSTREAM CONTRADICTION — HALT` block naming level, issue and the hub that fixes it. | `design-templates/.claude/skills/hub-preamble/SKILL.md:85–99`, which also enumerates the three contradiction kinds watched for: a referenced ID absent upstream, a `Deprecated`/`Retired` status treated as `Active`, and a contract or schema mismatch in field type, format or threshold. |
| INV-04 | [V] The plan suite carries no contradiction check of any kind. Its eight gates fail in seven ways — decline, re-extract three times, investigate, ask twice, drain — and every one addresses the form or completeness of what the practitioner supplied. | `plan/skills/plan/SKILL.md`, the two gate tables at Step 1 and Step 4, read in full; corroborated by a grep for `push back\|halt\|contradic\|decline\|redirect` across all eight skills, whose only hits are five atomics redirecting a mis-invoking caller and the hub declining a Revise when no plan file matches. |
| INV-05 | [V] The suite's entire vocabulary for preference is the clause forbidding it. "Recommend" appears once across all eight skills — in `plan/skills/plan/SKILL.md:42`, "options neutral, no recommendation" — and "optimal" appears zero times. | `grep 'optimal\|recommend\|better than\|prefer'` across `plan/skills/*/SKILL.md`, 950 lines, one hit. |
| INV-06 | [V] The plan template admits into Invariants only what already holds, grounded in an artifact: "existing behavior, guarantees, or limits this task must not violate", "an invariant describes what already holds", and every `Basis` must name "a file, contract or measurement". Intent, rationale and philosophy appear on neither list. | `plan/skills/templates/PLANNING.TEMPLATE.md`, the Invariants guidance block; `plan/skills/plan/SKILL.md:81`, the Investigation gate. |
| INV-07 | [V] `plan-audit`'s check 2 verifies that every listed `INV-XX` appears in some Design Decision or Failure Mode. No check in the twelve tests whether a relevant invariant was omitted. | `plan/skills/plan-audit/SKILL.md`, the twelve-row check table. |
| INV-08 | [V] A project may state both its governing rules and a precedence rule for resolving conflicts between sources, and such a precedence rule can be declared and still be wrong in practice. | `LogWatcher/AGENTS.md:11` states "If agent assumptions conflict with `docs/`, the documentation is correct." Read against `plan/evals/INVESTIGATION__ingestioneventfiltering.md`, which found three documentation sites in that same repository stale or about to go stale — `invariant_definition.md` Example C, `system_diagram.md:156`, `concurrency_model.md:142`. |
| INV-09 | [V] A governing-intent document may be wholly unenforceable by any test and still be load-bearing, such that violating it silently destroys the thing's purpose. | `Repos/skills/CLAUDE.md`, which governs `mcq-probe`: it states one prose invariant, names the failure mode it exists to prevent, declares its own standing against the specification it summarises ("This file is the mental model; those files are the contract"), and defines what counts as a regression. Nothing in it is machine-enforced, so by INV-02 none of it is an Altitude invariant. |
| INV-10 | [V] `[U]` already covers a resolution the agent argued for and the reviewer then ratified, so recording agent reasoning requires no new provenance marker. The marker is defined as "the reviewer stated it, chose it, or accepted it" — acceptance is sufficient. | `plan/skills/templates/PLANNING.TEMPLATE.md`, the PROVENANCE block's definition of `[U]`. |

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
| FR-01 | [U] WHILE investigating, the `plan` skill shall identify the sources stating the subject's governing intent — its philosophy, rationale, conventions, or declared invariants — and shall record them distinctly from sources establishing observable behavior. | Invoke `plan` on a task in a repository carrying a conventions or philosophy document; observe that document named in the investigation record as a source of intent, recorded separately from the code that was read. |
| FR-02 | [U] IF the investigation establishes no source of governing intent, THEN the `plan` skill shall state that none was found and shall not present the resulting invariants as grounded in intent. | Invoke `plan` in a repository carrying no conventions, philosophy or invariants document; observe an explicit statement that no intent source exists, rather than silence. |
| FR-03 | [U] WHERE a claim rests on exactly one source, the investigation record shall mark that claim uncorroborated. | Investigate a subject where one load-bearing fact appears in a single file; observe that claim's row marked uncorroborated in the record. |
| FR-04 | [U] WHEN a document and an implementation disagree on a fact this plan depends on, the investigation record shall record the disagreement as a finding rather than selecting one side silently. | Investigate a subject where a document states a threshold the code contradicts; observe both readings recorded and the conflict named as a finding. |
| FR-05 | [U] WHEN a proposed resolution contradicts an Invariant, a Non-goal, or an earlier Design Decision in this plan, the `plan` skill shall state the contradiction and shall withhold the write until it is resolved. | Propose a resolution that re-enters a recorded Non-goal; observe the contradiction stated by ID and no row written. |
| FR-06 | [U] WHEN a proposed resolution deviates from a governing intent the investigation established, the `plan` skill shall state the deviation alongside the tradeoffs, naming the source of that intent. | Propose a choice conflicting with a documented convention; observe the deviation stated with its source named, before any selection is captured. |
| FR-07 | [U] WHERE the `plan` skill states a preference for an option, it shall name the basis for that preference and mark that basis as established or novel; a novel basis is permitted, and shall be identified as novel rather than presented as precedent. | Plan a task whose best approach has no precedent in the repository; observe the preference stated with its reasoning and explicitly marked novel. |
| FR-08 | [U] WHEN the pre-execute check runs, it shall verify that every source of governing intent identified during investigation is reflected in at least one Postulate or Invariant, or explicitly noted as bearing on nothing in this plan. | Author a plan whose investigation names a conventions document that no Postulate and no Invariant reflects; observe a blocking finding naming that document. |
| FR-09 | [U] WHEN recording a source of governing intent, the `plan` skill shall state what violating it would cost, how that cost was established, and whether anything would detect the violation. WHERE the cost cannot be established from a stated rationale or from what consumes the artifact, directly or transitively, it shall be recorded as unestablished rather than as nil, and only a cost established as nil shall exclude the source from governing intent. | Investigate a repository carrying a convention that is consistently observed but whose rationale is stated nowhere; observe its cost recorded as unestablished, naming what was consulted, rather than the convention dropped as costless. |
| FR-10 | [U] WHEN recording a Postulate, the investigation record shall state whether any mechanism that established it was independent of the stated rationale, and name which. | Investigate a subject whose stated rationale the codebase consistently follows; observe the record naming which mechanisms were independent of that rationale, or stating that none was. |
| FR-11 | [U] The plan skill suite shall be distributed as a self-hosted marketplace plugin, and shall not be installed by any other mechanism. | Install the plugin from the local marketplace; observe all nine skills discoverable, and no skill resolving through `~/.claude/skills/`. |
| FR-12 | [U] Every versioned artifact in the suite shall begin at `0.1.0` and shall increment only its patch field, only when that artifact itself changes. | Change one skill; observe that skill's patch incremented and every other version — including the plugin manifest's and the template's — unchanged. |

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

<!-- Zero rows: no measurable threshold was named by the reviewer for this task, and none
     was measured. Every requirement above is a behavior the suite must exhibit, verifiable
     by observing one run. FR-09's regularity signal — a convention held in 40 of 40 places
     versus 12 of 30 — is countable, but no threshold separating the two has been named, so
     it is not an NFR. -->


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
| NG-01 | [U] Implementing, superseding or absorbing the collaboration-interface revision | `PLAN__plan-suite-collaboration-revision.md` is authored, audited and unimplemented, and it edits the same hub this plan edits. This plan neither carries it out nor reverses it. Where the two touch the same instruction the collision is recorded as a risk, not resolved here, and whichever lands second must be reconciled against whichever landed first. |
| NG-02 | [U] An external CLI validator or linter | Excluded at the suite's inception and still excluded. FR-08 adds a check to `plan-audit`, which is a skill the agent runs, not a program invoked outside the session. Nothing here introduces a build-time or CI-time artifact. |
| NG-03 | [U] Mechanically detecting violations of a governing intent | FR-06 has the agent state a deviation it has reasoned about. That is not detection: no analyzer, no rule engine, and nothing that scans a codebase for conformance. The capability being built is the agent noticing and saying so, which is why FR-09 turns on cost and detectability rather than on a pattern a scanner could match. |
| NG-04 | [U] Transferring any decision right from the reviewer to the agent | The agent gains a duty to state contradictions, name the basis of a preference, and mark a basis novel where it is. It gains no authority to choose. `[U]` keeps its meaning exactly — the reviewer stated it, chose it, or accepted it — and a resolution the agent argued for and the reviewer ratified is still the reviewer's. This is the protection the existing prohibition earns, and it survives intact. |

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
| DD-01 | Does the plan suite adopt Altitude's Postulate concept, and under what name? | [U] Adopted by name, with Altitude's definition intact: a Postulate is the external, foundational rule the thing has no authority over, carrying the four properties of INV-01 — no authority, exclusive, sufficient, external — together with the four negative tests (not a stakeholder or team, not a technology, not a list of change scenarios, not internal to the thing) and the diagnostic that traces a set of reasons-to-change back to the single assumption they share. The reviewer's original instruction to skip L5 as undercooked is recorded here as applying to its templates, not to its conceptual layer. | FR-01, FR-09, INV-01, INV-02, INV-06 | Adopting the inward/outward distinction under a lighter term of the suite's own coinage — keeps the separation without importing L5's apparatus or its status, rejected because it puts two names on one concept across frameworks the reviewer uses side by side, and forces the definition work — the four properties, the four negative tests, the diagnostic — to be redone rather than cited. Widening the existing Invariants section to admit rules no test can catch — the simplest option and the only one adding no new category, rejected because it conflates the inward rule with the outward guarantee that Altitude separates deliberately, and because it deepens an existing divergence in which the suite's `INV-XX` already means something looser than Altitude's `invariant`, making one word mean two things across two frameworks in daily joint use. |
| DD-02 | Where do Postulates live in the plan document? | [U] A `## Postulates` section of its own, carrying the ID series `PS-XX`, placed between Problem Statement and Invariants — the order Altitude's own dependency implies, since the Postulate determines the shape the Invariant then promises. Cited by Design Decisions and Failure Modes exactly as Invariants are, and reached by the pre-execute check on the same footing. | FR-01, FR-08, INV-01, INV-07 | A second table beneath the existing `## Invariants` heading — adds no section and no series, rejected because the heading would name only one of the two things sitting under it. Recording Postulates in the investigation record alone and citing them from an Invariant's `Basis` — leaves the plan's shape wholly untouched and avoids re-deriving them per plan, rejected because that record carries no ID series, so FR-08's check cannot reach them and no Design Decision can cite one directly. A `Type` column on the existing Invariants table — cheapest structurally, rejected for re-merging into one table the inward rule and the outward guarantee DD-01 had just separated. |
| DD-03 | How does the agent establish a Postulate? | [U] Every candidate runs all four mechanisms before it is recorded: the stated rationale where one exists; the consumer chain, traced directly and transitively; regularity measured across the codebase; and Altitude's own diagnostic, tracing a set of reasons-to-change back to the single assumption they share. Altitude's four negative tests then filter what survives. Corroboration falls out by construction — four mechanisms are four sources — so FR-03's uncorroborated marking becomes the exception rather than the norm, and FR-09's cost figure rests on the consumer chain rather than on an impression. The record additionally states which of the four were independent of the stated rationale (FR-10), because four mechanisms all observing consequences of one root cause are a single source counted four times, and a corroboration claim that does not distinguish the two cases is worthless. | FR-01, FR-03, FR-09, FR-10, INV-01, INV-09 | An ordered fallback running the cheapest mechanism first and stopping at whichever returns a result — efficient, and trivial on an obvious candidate; rejected because it permits the agent to stop at a stated rationale that is shallow or stale, which INV-08 establishes does happen, and stopping at the first available answer is the under-reasoning this plan exists to prevent. Requiring the stated rationale alone and naming the other three as available techniques — rejected as materially the behavior the suite already has for investigation breadth, which is what produced the defect. |
| DD-04 | How are a contradiction and a deviation surfaced to the practitioner? | [U] A contradiction emits a fixed block — `PLAN CONTRADICTION — HALT` — naming the row contradicted, what specifically conflicts, and what would resolve it, with the write withheld and no partial write made. A deviation stays conversational, stated alongside the tradeoffs in prose. The block is admitted on Altitude's own criterion rather than by exception: a withheld write is the one moment where silence could be mistaken for progress, so the cost of ambiguity there is high. | FR-05, FR-06, INV-03, INV-04 | Prose for both, with the write simply not happening — spends no new fixed moment and matches the collaboration plan's choice to keep boundary statements conversational; rejected because a withheld write is not a routine exchange and nothing in prose would distinguish it from one. Carrying the deviation as a named column inside the fork's comparative table — puts it literally alongside the tradeoffs as FR-06 requires; rejected because that table is introduced by the collaboration plan's `DD-03`, which NG-01 excludes this plan from implementing, so the requirement would rest on a plan that may never land. |
| DD-05 | How are corroboration and source disagreement recorded? | [U] A new `Conflicts` table in the investigation record holds each disagreement between sources — what each source states, and that they disagree — because a conflict is a relation between two sources and has no home in a row about either one. Corroboration status is stated inline within the `Established` cell it qualifies, since it is a property of that claim and travels with it. | FR-03, FR-04, INV-08 | A dedicated `Corroboration` column on the Consulted table alongside a `Conflicts` table — the most structured option, rejected for making two shape changes to the record format where one suffices, and for separating a claim's corroboration status from the claim it qualifies. Handling both as prose in the closing Sufficiency section — no shape change at all, rejected because Sufficiency is already the record's catch-all, and a conflict placed in a closing paragraph is the one most likely to be skimmed past. Weak supporting evidence for the chosen shape: both investigation records written before this decision put doc-versus-code findings inside `Established` cells unprompted, reserving Sufficiency for the ones left unresolved. |
| DD-06 | Does the plan record that the agent held a preference, and where? | [U] A new `Agent Position` column on Design Decisions records which option the agent recommended and the basis for it, marked established or novel per FR-07, or `—` where the agent held no view. The reviewer's `Resolution` keeps `[U]` unchanged, so the two claims stay separable on the page: what the agent argued, and what the reviewer decided. | FR-07, INV-05, INV-10 | Recording it inside the `Resolution` cell adjacent to its marker — no schema change at all, rejected for mixing two distinct claims in one cell and for lengthening a cell already carrying the decision itself, where the LogWatcher plan's equivalents already run past ninety words. Leaving it in conversation only — satisfies FR-07 literally, since the requirement governs what the agent says rather than what it writes; rejected because the finished plan then cannot distinguish a resolution the reviewer originated from one they ratified, and that distinction is the whole of the auditability the bias protection depends on. |
| DD-07 | What happens when no source of governing intent exists? | [U] Advisory, matching Altitude's soft existence check: state that none was found, name what was searched, ask whether to proceed, and record the answer before the section continues. Planning is not blocked, and the resulting Invariants are not presented as grounded in intent. | FR-02, INV-03 | Proceeding with a recorded caveat and no question — cheapest, rejected because the practitioner never sees the gap before the plan's Invariants rest on it, and a caveat noticed only at delivery is a caveat noticed too late. Declining to author until an intent source exists — the strongest guarantee, rejected on two grounds: it makes the suite unusable against any repository that has never written its rules down, which is most of them; and it would push a practitioner to author a philosophy document to satisfy a gate, which produces exactly the shallow, unenforced, nobody-believes-it convention FR-09 exists to detect. |
| DD-08 | Do Postulates get their own atomic and cascade break point? | [U] A ninth skill, `plan-update-postulate`, mirroring `plan-update-invariant` exactly — Postulates written inline on the Author route, mutated through the atomic on Revise. `plan-cascade` gains a `Postulates` break point walking Invariants → Design Decisions → Files Touched → Failure Modes → Implementation Order, the widest traversal in its table, because INV-01's exclusive property puts a Postulate upstream of everything the plan holds. | FR-05, INV-01 | Extending `plan-update-invariant` to write both sections, selected by argument — adds no ninth skill, rejected because a skill named for one section that writes two blurs its own guard clause and completion tag, and the suite's naming decision (`DD-12` of the shipped plan) chose verb-first atomics carrying full section names for exactly that reason. Revising Postulates inline with the hub invoking `plan-cascade` directly — cheapest, rejected on two counts: it leaves the suite's most load-bearing section as the only one without a reasoning checkpoint, against the stated criterion that atomics exist where bad reasoning invalidates a substantial part of the plan; and it would have the hub call `plan-cascade` directly, which every atomic's contract and the hub's own instruction currently forbid. |
| DD-09 | How is the suite installed and versioned? | [U] As a self-hosted marketplace plugin, following the structure `mcq-probe` already uses in this repository: a `.claude-plugin/` directory holding `plugin.json` and `marketplace.json` beside the existing `skills/` tree, which is already the correct shape. The nine Windows junctions at `~/.claude/skills/` are removed, leaving the plugin as the single discovery path. Every versioned artifact — the plugin manifest, all nine skills, and the template — resets to `0.1.0` and thereafter increments only its patch field, only when that artifact itself changes; the major and minor fields never move, and versions never move together. | FR-11, FR-12 | Keeping the junctions alongside the plugin — useful for local development against the working tree, rejected because every skill name would then be discoverable twice from two paths into the same files. Retaining the existing per-artifact version lines — `plan` at `0.3.0`, `plan-audit` at `0.2.0`, the template at `1.4.0` — rejected in favour of one starting point, since three unrelated scales across a single bundle carry no information a reader can use. Versioning the bundle alone and dropping per-skill versions entirely — rejected because a change to one skill would then be indistinguishable from a change to any other. |

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
| `plan/skills/plan/SKILL.md` | Modify | [D::DD-02, DD-03, DD-04, DD-06, DD-07, DD-08] The Author route gains a Grounding step running DD-03's four mechanisms and writing Postulates inline, plus a Postulate gate ahead of it. Add the DD-07 advisory exchange for when no intent source is found. Add the DD-04 contradiction check emitting `PLAN CONTRADICTION — HALT` with the write withheld, and the deviation statement in prose alongside the tradeoffs. Add the `Agent Position` write on each Design Decision, with its basis marked established or novel. The Revise table gains a Postulates row routing to `plan-update-postulate`. Bump `metadata.version`. | DD-02, DD-03, DD-04, DD-06, DD-07, DD-08, FR-01, FR-02, FR-05, FR-06, FR-07 |
| `plan/skills/templates/PLANNING.TEMPLATE.md` | Modify | [D::DD-01, DD-02, DD-06] Add a `## Postulates` section carrying the `PS-XX` series between Problem Statement and Invariants, with Altitude's definition, the four properties and the four negative tests as its guidance. Add the `Agent Position` column to Design Decisions. Add `PS-XX` to the ID STABILITY list. Extend the PRE-EXECUTE CHECK: the invariant-citation check reaches `PS-XX`, and a new check implements FR-08. Bump `template_version` from `1.4.0`. | DD-01, DD-02, DD-06, FR-07, FR-08, INV-01, INV-06 |
| `plan/skills/plan-investigate/SKILL.md` | Modify | [D::DD-03, DD-05] Candidates gains the intent-source category, recorded distinctly from behavioral sources. The Read step runs DD-03's four mechanisms against each candidate and applies the four negative tests. Add the `Conflicts` table. State corroboration inline within `Established`. Record cost and detection per FR-09, with `unestablished` kept distinct from nil. | DD-03, DD-05, FR-01, FR-03, FR-04, FR-09 |
| `plan/skills/plan-audit/SKILL.md` | Modify | [D::DD-02] Extend check 2 to `PS-XX`, and add a thirteenth check implementing FR-08 — every intent source named in the investigation record is reflected in a Postulate or an Invariant, or explicitly noted as bearing on nothing. | DD-02, FR-08, INV-07 |
| `plan/skills/plan-cascade/SKILL.md` | Modify | [D::DD-08] The traversal table gains a `Postulates` break point walking Invariants → Design Decisions → Files Touched → Failure Modes → Implementation Order — the widest row in the table, because INV-01's exclusive property puts a Postulate upstream of everything. | DD-08, INV-01 |
| `plan/skills/plan-update-postulate/SKILL.md` | Create | [D::DD-08] The ninth skill, in the four-section atomic shape mirroring `plan-update-invariant`: guard clause, args, write, completion tag. `user-invocable: false`. Invokes `plan-cascade` with `break_point=Postulates` on mutation and removal, never on create. | DD-08, FR-05 |
| `plan/.claude-plugin/plugin.json` | Create | [D::DD-09] The plugin manifest, following the schema `mcq-probe/.claude-plugin/plugin.json` already uses in this repository: `name`, `version` at `0.1.0`, `description`, `author`. | DD-09, FR-11, FR-12 |
| `plan/.claude-plugin/marketplace.json` | Create | [D::DD-09] The self-hosted marketplace manifest, following `mcq-probe`'s: `$schema`, `name`, `description`, `owner`, and one `plugins` entry whose `source` is `.`. | DD-09, FR-11 |
| `plan/skills/plan-update-invariant/SKILL.md`, `plan-update-requirement/SKILL.md`, `plan-update-design-decision/SKILL.md`, `plan-update-files-touched/SKILL.md` | Modify | [D::DD-06, DD-09] Version reset on all four. `plan-update-design-decision` additionally gains the `agent_position` argument, the `Agent Position` column in the row it writes, and that field in its `update` list — DD-06 adds a column to the table this atomic owns, so the hub's call would otherwise pass an argument nothing writes. The other three carry no practitioner-facing instruction, no gate and no Postulate reference, and take the version reset alone. | DD-06, DD-09, FR-07, FR-12 |

<!-- FR-12's reset reaches every row above, not only the grouped row: each of the five
     modified skills, the newly created ninth skill, and the template all set their
     version to 0.1.0 in the same change. Their content edits and their version reset
     are the same write, so they are not listed twice.

     The nine junctions at ~/.claude/skills/ are removed as part of DD-09, but they are
     filesystem links outside this repository rather than files it holds, so they appear
     in Implementation Order rather than here. -->


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
| FM-01 | A subject carrying many candidate sources of governing intent. | [D::DD-03] DD-03 runs all four mechanisms against every candidate, and investigation is already the longest phase of authoring. Cost scales as candidates × 4, so the pressure is either to skip planning entirely or to run the mechanisms shallowly enough to finish — which returns the under-reasoning DD-03 exists to prevent. | Medium | [U] Yes — depth is the deliverable here, and every cheaper procedure considered under DD-03 was rejected precisely because it permits stopping early. A first-pass filter would reintroduce the judgment call the four mechanisms replace. |
| FM-02 | A stated rationale that is itself wrong, in a codebase that consistently follows it. | [D::DD-03, INV-08] The four mechanisms are not independent in this case. Regularity corroborates the wrong rule because the code obeys it; the consumer chain traces to consumers built on the same mistake; the reasons-to-change diagnostic converges on the wrong assumption because that is what everything was built around. Four mechanisms return one piece of evidence propagated four ways, the Postulate is recorded as corroborated, and FR-06 thereafter flags deviations from the wrong rule — steering the practitioner away from the correct choice with four mechanisms' apparent backing. | Medium | [U] Yes — accepted on the basis that FR-10 makes the correlation visible: the record must state which mechanisms were independent of the stated rationale, so a reader weighs a corroboration claim rather than trusting its count. Requiring genuine independence was rejected because a Postulate may originate inside the system by construction, per INV-01, leaving the obligation unsatisfiable and `unestablished` routine. |
| FM-03 | The agent misreads a Postulate as contradicted when it is not. | [D::DD-04] `PLAN CONTRADICTION — HALT` fires and the write is withheld. DD-04 defines no override, so the practitioner must argue the agent out of a false positive with no mechanism for directing the write to proceed. | Medium | [U] Yes — the halt block states which row it believes contradicts what and what would resolve it, so a false positive is visible and arguable in conversation. A formal override would weaken the halt for the true positives it exists to catch. |
| FM-04 | Two plans authored against the same project. | [D::DD-02] DD-02 places Postulates in the plan rather than in a durable project-level document, so the same Postulates are established twice — through four mechanisms each time — and possibly differently. Nothing reconciles the two derivations, and nothing notices when they disagree. | Medium | [U] Yes — re-deriving is wasteful but self-correcting, since each derivation runs all four mechanisms afresh rather than inheriting a stale conclusion. |
| FM-05 | The suite is installed by any path other than the plugin. | [D::DD-09] Two discovery paths reach the same files, so every skill name resolves twice and which copy loads is undefined. Prevented by DD-09 via FR-11: the nine junctions are removed as part of implementation, leaving the plugin as the single path. | Medium | [U] No — prevented by DD-09 via FR-11. |

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
| RK-01 | [V] Two unimplemented plans edit the same file. `PLAN__plan-suite-collaboration-revision.md` is authored, audited and unimplemented, and its Files Touched names `plan/skills/plan/SKILL.md` — the same hub this plan rewrites in S-05. NG-01 states this plan does not reconcile them, and neither plan records what a merged hub looks like. | High | Degraded | Land one plan completely, then re-read the resulting hub and revise the other plan's Files Touched against what is actually on disk before implementing it. Do not implement both from their current text. |
| RK-02 | [V] Plugin installation has never been performed for this suite, and removing the nine junctions is only manually reversible. If the plugin fails to load, the suite becomes undiscoverable with no fallback. | Medium | Breaking | Install the plugin and confirm all nine skills load **before** removing any junction, never after. Implementation Order sequences S-09 ahead of S-10 for this reason alone. |
| RK-03 | [V] The suite has still never been executed under representative conditions. Both of its runs to date — the collaboration plan and this one — were plans about the suite, authored by the suite, in the repository that holds it. Every verification procedure across both plans is written and unexecuted. | High | Degraded | Run `plan` against a small task in an unrelated repository after implementation, and walk the `Verification` column of all twelve requirements rather than sampling it. |
| RK-04 | [V] DD-01 adopts the Postulate concept from L5, whose templates the reviewer excluded at this project's inception as undercooked. The investigation established the concept is well-specified across two mutually corroborating documents, but left unverified whether Altitude practises it — its L5 templates and `l5` skill have been excluded from every investigation in this project. | Medium | Degraded | Read `altitude-framework/templates/L5__*` before writing DD-01's guidance text into the template, to see whether the concept survives contact with the templates meant to use it. If it does not, the guidance should teach the concept rather than cite it. |
| RK-05 | [V] DD-03's cost is unmeasured. Four mechanisms per candidate has never been run, so FM-01's Medium severity is an estimate rather than an observation, and no figure exists for how grounding compares to the rest of authoring. | Medium | Degraded | On the first real run, record grounding's duration against total authoring duration, so FM-01 can be reassessed against a number. |

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

<!-- Zero rows. Every question raised during authoring was resolved before the section it
     gated was written: scope absorption of NG-02, the Problem Statement across two
     revisions, the FR-07 split and three revisions of FR-09, the Non-goal set, nine design
     forks, five failure-mode verdicts, and the packaging and versioning directives. Nothing
     was parked. -->


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
| S-00 | [D::RK-01] Decide the ordering against `PLAN__plan-suite-collaboration-revision.md`, which is unimplemented and edits the same hub. Do not begin S-05 until that plan has either landed or been set aside. | — | — | — |
| S-01 | [D::DD-01, DD-02, DD-06] Add the `## Postulates` section between Problem Statement and Invariants with the `PS-XX` series, carrying Altitude's definition, the four properties and the four negative tests as guidance. Add the `Agent Position` column to Design Decisions. Add `PS-XX` to ID STABILITY. Extend the PRE-EXECUTE CHECK to reach `PS-XX` and to implement FR-08. Set `template_version` to `0.1.0`. | `plan/skills/templates/PLANNING.TEMPLATE.md` | DD-01, DD-02, DD-06, FR-07, FR-08 | S-00 |
| S-02 | [D::DD-08] Create the ninth skill in the four-section atomic shape, `user-invocable: false`, version `0.1.0`, invoking `plan-cascade` with `break_point=Postulates` on mutation and removal only. | `plan/skills/plan-update-postulate/SKILL.md` | DD-08 | S-01 — the atomic writes rows into a section that must exist first. |
| S-03 | [D::DD-08] Add the `Postulates` break point to the traversal table, walking Invariants → Design Decisions → Files Touched → Failure Modes → Implementation Order. | `plan/skills/plan-cascade/SKILL.md` | DD-08 | S-02 — the atomic and the break point it calls land together. |
| S-04 | [D::DD-03, DD-05] Rewrite the investigation skill: the intent-source candidate category recorded distinctly; the four mechanisms run against every candidate with the four negative tests as filter; the `Conflicts` table; corroboration stated inline in `Established`; cost and detection recorded with `unestablished` distinct from nil; the independence statement. | `plan/skills/plan-investigate/SKILL.md` | DD-03, DD-05, FR-01, FR-03, FR-04, FR-09, FR-10 | S-01 — the record feeds a section that must exist. |
| S-05 | [D::DD-02, DD-03, DD-04, DD-06, DD-07] Rewrite the hub: the Grounding step and Postulate gate; the DD-07 advisory exchange; the contradiction check emitting `PLAN CONTRADICTION — HALT` with the write withheld; the deviation statement in prose; the `Agent Position` write; the Revise table's Postulates row. | `plan/skills/plan/SKILL.md` | DD-02, DD-03, DD-04, DD-06, DD-07, FR-02, FR-05, FR-06, FR-07 | S-04 — the hub calls the investigation skill and must match what it now produces. |
| S-06 | [D::DD-02] Extend check 2 to `PS-XX` and add the thirteenth check implementing FR-08. | `plan/skills/plan-audit/SKILL.md` | DD-02, FR-08 | S-01 — the checks test structure the template must already define. |
| S-07 | [D::DD-06, DD-09] Set every skill's `metadata.version` to `0.1.0`. In the same pass, add the `agent_position` argument to `plan-update-design-decision`, the `Agent Position` column to the row it writes, and that field to its `update` list. | `plan/skills/plan-update-invariant/SKILL.md`, `plan/skills/plan-update-requirement/SKILL.md`, `plan/skills/plan-update-design-decision/SKILL.md`, `plan/skills/plan-update-files-touched/SKILL.md` | DD-09, FR-12 | S-06 — every content edit lands first, so no version is set on a file about to change again. |
| S-08 | [D::DD-09] Create the plugin and marketplace manifests against the schema `mcq-probe/.claude-plugin/` uses, with `version` at `0.1.0` and `source` as `.`. | `plan/.claude-plugin/plugin.json`, `plan/.claude-plugin/marketplace.json` | DD-09, FR-11, FR-12 | S-07 |
| S-09 | [D::DD-09] Install the plugin from the local marketplace and confirm all nine skills load and resolve. | — | FR-11 | S-08 |
| S-10 | [D::DD-09] Remove the nine junctions at `~/.claude/skills/`, leaving the plugin as the single discovery path. | — | FR-11 | S-09 — RK-02: the junctions are the only fallback if the plugin fails to load, and re-creating them is manual. Confirm the plugin works before removing them, never after. |
| S-11 | [D::RK-03, RK-05] Run `plan` against a small task in an unrelated repository, walking the `Verification` cell of all twelve requirements, and record grounding's duration against total authoring duration. | — | FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-09, FR-10, FR-11, FR-12 | S-10 — the suite must be in its final installed state before the run means anything. |

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
| 2026-09-10 | Files Touched — `plan/skills/plan-update-invariant/SKILL.md` and the three atomics grouped with it | S-07 | The row claimed all four atomics take a version reset and no content change. Discovered false during S-07: DD-06 adds the `Agent Position` column to the Design Decisions table, which `plan-update-design-decision` owns, so the hub's `agent_position` argument would have reached an atomic that writes no such column. `What Changes` and `Why` corrected to record the argument, the column and the `update` field list; S-07's step text corrected to match. The other three atomics are unaffected and take the version reset alone. |

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
