---
template_version: "1.4.0"
---

# Implementation Plan: Plan Suite Collaboration Interface
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

[U] The plan hub has one delivery moment: `SendUserFile` at Step 6, after every gate has closed and the audit has passed. Between target instantiation at Step 3 and the audit at Step 5, the practitioner's only view of the document is conversational prose and `AskUserQuestion` cards, and the sole fixed-format moment — `CONFIRM WRITE` — renders a single row with no surrounding context. In the LogWatcher session this meant ten Design Decisions and nineteen Functional Requirements were settled against a 476-line document the practitioner had never seen. The plan's IDs compound it: `FR-08` and `DD-03` are the document's referential backbone, and the hub mentions them in conversation without their claims, so every reference costs a cross-reference against a document that is not yet readable.

[U] The hub routes every genuine design fork to `AskUserQuestion` with "options neutral, no recommendation." The rejection reasoning a Design Decision requires — the template demands it be "reproducible by someone who wasn't in the room" — averages 31 words per alternative across the LogWatcher plan's ten decisions. The tool imposes no length limit that this content exceeds, so the defect is structural rather than dimensional. `AskUserQuestion` renders options as discrete selectable items, so an alternative's reason for rejection is visible only inside the option proposing it, and the schema's own `preview` field — intended for "visual comparisons that help users compare options" — renders only while a single option is focused. A tradeoff is comparative by nature. The channel cannot place two alternatives side by side, so the argument that distinguishes them has nowhere to render no matter how much text each cell holds.

[U] The hub permits batching up to four questions "whose answers cannot affect one another." Two distinct failures follow. First, that predicate ranges over the answer space and is settled only once the answers arrive; for Design Decisions it is routinely false, because a resolution changes which decision points exist downstream. The LogWatcher investigation records the case — its second pass opens "The design moved from `add a bool field to FsEvent` to a value-object redesign" — and under the rejected branch, two of that plan's ten decisions had no reason to exist. When a batched answer diverges from what the agent anticipated, the remaining questions are already void and the practitioner must decline them one at a time before the batch can be re-formed. Second, and independent of validity: a batch the predicate correctly admits is still delivered as a simultaneous demand for up to four decisions. A practitioner reasoning carefully about a non-elementary question cannot do so four times at once, so even a well-formed batch forces either serialized attention against a parallel presentation, or a degraded answer on whichever questions received less of it.

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
| INV-01 | [V] `allowed-tools` grants permission for the listed tools during the invoking turn without restricting which tools are callable; `disallowed-tools` is the field that removes a tool from the pool. | `code.claude.com/docs/en/skills`, `allowed-tools` reference: "It does not restrict which tools are available: every tool remains callable, and your permission settings still govern tools that are not listed." |
| INV-02 | [V] No documented mechanism exists for a skill to render a document, table or diagram to the practitioner mid-run. The documented user-facing output paths are the agent's own response text and a bundled script that generates an HTML file. | `code.claude.com/docs/en/skills`, surveyed for rendering mechanisms; its codebase-visualizer example is the only user-facing display path documented, and it writes an HTML file from a bundled script. |
| INV-03 | [V] `AskUserQuestion` accepts one to four questions per call, each carrying two to four options, with `header` capped at 12 characters. No `maxLength` constrains `question`, `label` or `description`. Options are discrete selectable items, and `preview` renders only while its own option is focused. | The tool schema, read directly: `minItems: 1, maxItems: 4` on `questions`; `minItems: 2, maxItems: 4` on `options`; `header` "max 12 chars"; `preview` "rendered when this option is focused". Corroborated for the two counts by `INV-05` of the shipped suite plan. |
| INV-04 | [V] A fixed-format block is admitted by a stated criterion — that the cost of ambiguity at that moment is high — rather than by a fixed count. Three are currently spent. | `design-templates/Altitude_Skills__Authoring_Methodology.md:154`: "These three earn a fixed block because the cost of ambiguity there is high." |
| INV-05 | [V] Instructions to the agent are formalized; output to the practitioner stays natural. A gate table guarantees every hub checks the same things the same way, while what is said to the practitioner when a gate fails remains conversational. | `design-templates/Altitude_Skills__Authoring_Methodology.md:149`; recorded as `INV-09` of the shipped suite plan and cited there by its `DD-09`. |
| INV-06 | [V] `cascade` advances to the next level only after the current level is fully resolved with the practitioner, and precedes each level with a one-line signpost carrying its findings conversationally beneath it. | `design-templates/.claude/skills/cascade/SKILL.md:93`: "Advance to the next level only after the current level is fully resolved with the practitioner." The signpost form and the "One line. Findings discussed conversationally beneath it" rule are at `Altitude_Skills__Authoring_Methodology.md:175–182`. |
| INV-07 | [V] The hub already instructs a kebab-case slug, so the LogWatcher filename defect is non-compliance with an existing instruction rather than a missing one. | `plan/skills/plan/SKILL.md:68`: "derive a kebab-case slug from the task", contrasted against the delivered `PLAN__ingestioneventfiltering.md` in `plan/evals/`. |
| INV-08 | [V] A `[U]` marker rests on unambiguous attribution of the reviewer's choice, and that is the stated reason the suite routes design forks through a question card at all. | `plan/evals/PLAN__plan-skill-suite.md`, `DD-09`: `AskUserQuestion` is used for design forks "where attribution must be unambiguous for a `[U]` marker to be honest". |
| INV-09 | [V] The session scratchpad directory is session-specific — a new session receives a different path — so a document written there does not survive the session that wrote it. | The environment description, which names the scratchpad path and states it is session-specific; recorded independently as `INV-07` of the shipped suite plan, where it is the basis for that plan's `DD-07` declining a revision when no plan matches. |
| INV-10 | [V] A file reference written as a markdown link whose href is a path relative to the working directory is clickable and opens the file in a side pane. A bare path is not, and a file outside the working directory has no usable relative form, so it cannot be linked at all. | The harness's own file-reference convention, which specifies markdown links with working-directory-relative hrefs and an optional `:line` suffix. Confirmed against the working directory `C:\Users\diffi\Repos`, from which `skills/plan/skills/plan/SKILL.md` resolves; the practitioner reported that an absolute scratchpad path written as plain text rendered as text rather than as a link. |

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
| FR-01 | [U] WHEN a plan section is completed during the Author route, the `plan` skill shall state which section was written, how many rows it carries, and the plan file as a working-directory-relative markdown link. | Author a plan through two consecutive sections; observe a one-line statement after the first, naming the section, its row count and a clickable link to the file, and no rendering of the rows themselves. |
| FR-02 | [U] The `plan` skill shall not name a plan ID in conversation without the claim that ID records. | Author a plan past Design Decisions; observe every `DD-XX` and `FR-XX` mention in the responses carries its claim inline. |
| FR-03 | [U] WHEN the `plan` skill presents a design fork, it shall render every alternative and its reason for rejection in a single comparative view before any selection is captured. | Invoke `plan` on a task admitting three approaches; observe one view showing all three together, ahead of any question card. |
| FR-04 | [U] WHERE a design fork's selection is captured through `AskUserQuestion`, the card shall introduce no alternative, reason, or consequence absent from the comparative view that preceded it. | Same run as FR-03; compare the card's option text against the preceding view and observe it introduces no new claim. |
| FR-05 | [U] The `plan` skill shall present Design Decisions one at a time. | Invoke `plan` on a task carrying three design forks; observe three separate exchanges rather than one card carrying three questions. |
| FR-06 | [U] The `plan` skill shall present one question per `AskUserQuestion` call. | Author a plan end to end; observe no call carrying more than one question. |
<!-- FR-07 retired during authoring. It required the agent to render the document's full
     current state on request. Once the plan lives in the practitioner's repository
     (FR-11, DD-08) the file is openable at any moment without the agent's involvement,
     so the requirement had no remaining subject. Its ID is retired, never reissued. -->
| FR-11 | [U] The `plan` skill shall write the plan document into the practitioner's repository — a dedicated plan directory where one exists, otherwise the repository root — and shall leave the file untracked. | Invoke `plan` in a repository carrying no plan directory; observe `PLAN__<slug>.md` written at the repository root, and no git operation of any kind performed. |
| FR-08 | [U] WHEN the `plan` skill derives a plan's filename slug, that slug shall be kebab-case. | Invoke `plan` on a task named with three or more words; observe the file written as `PLAN__<word>-<word>-<word>.md`. |
| FR-09 | [U] IF the practitioner's answer is vague or unclear and no best guess is articulable, THEN the `plan` skill shall raise an `AskUserQuestion` card to force a definitive answer. | Answer a prose-asked design fork ambiguously; observe a card raised naming the competing readings, rather than the ambiguity resolved by assumption. |
| FR-10 | [U] WHEN a `[U]` resolution was reached through a prose exchange, the `plan` skill shall emit `CONFIRM WRITE` and wait for the practitioner's confirmation before writing it. | Resolve a design fork in prose; observe `CONFIRM WRITE` emitted and no write occurring until confirmation is given. |

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

<!-- Zero rows: no measurable threshold was named by the reviewer for this
     task, and none was measured. Every requirement above is a behavior the
     suite must exhibit, verifiable by observing one run; none carries a
     performance target. -->

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
| NG-01 | [U] Permitting the agent to recommend a resolution, and defining what makes one option optimal | Elected out of scope at authoring. The suite currently forbids the agent from advocating a resolution, and that prohibition is the reason every Design Decision in the LogWatcher plan carries `[U]`. Correcting it requires a change to the provenance marker model, reaching the template, the audit's checks, and every atomic that writes a marker. It is a separate body of work, deliberately deferred, not overlooked. |
| NG-02 | [U] Defining what an invariant is, and adding a completeness check for the Invariants section | Elected out of scope at authoring. The section's guidance states a usage constraint — a row belongs only if cited by a Design Decision or Failure Mode — rather than a definition of the concept, and no check verifies that a relevant invariant was found rather than merely that a listed one is cited. Both remain true after this plan. |
| NG-03 | [U] Changing "options neutral, no recommendation" | The neutrality clause of the shipped suite plan's FR-03 is preserved exactly. This plan relocates where a fork's argument is rendered; it does not change who makes that argument. FR-04 constrains the question card to introduce no claim absent from the comparative view preceding it, and must not be read as licence to place a recommendation in that view instead — that is NG-01 by another route. |
| NG-04 | [U] Revising `PLAN__plan-skill-suite.md`, the shipped suite plan | It is the closed record of what was built and committed. This plan supersedes its FR-03 channel clause and its FR-05 batching predicate going forward, and leaves both standing in place as the record of the specification the suite was originally built to. |

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
| DD-01 | How does the practitioner see the plan as it is being built? | [U] They open it. The plan is a file in their own repository (DD-08), so it is readable at any moment in whatever editor they already have open, and the agent renders no plan content into the conversation at all. Every reference to it is written as a working-directory-relative markdown link (INV-10), so opening it costs one click rather than a path to copy. | FR-01, FR-11, INV-02 | Four rendering surfaces were compared before this decision point was reframed. All four were genuinely available — INV-01 establishes that `allowed-tools` grants permission without restricting capability, so the hub's declaration foreclosed none of them and each had to be rejected on merit rather than on reach. That same fact makes dropping `SendUserFile` from the declaration safe: it withdraws pre-approval, not the tool. All four are rejected together, each carrying plan content into the conversation, which is unnecessary once the practitioner can hold the file open. For the record — a markdown table in the response body, rejected because a section such as Files Touched runs to two dozen rows and repeating it at every boundary reproduces the volume problem the render was meant to solve; `SendUserFile` per section, trialled live during this plan's own authoring and withdrawn, since a `.md` attaches as a download card rather than rendering inline; `Artifact`, the best rendering of the four and the only one readable away from the terminal, rejected for adding a network dependency and publishing the document to the web; a bundled HTML script, the one other mechanism INV-02 documents, rejected for requiring a maintained script file plus a Bash call on every render. |
| DD-02 | What marks a section boundary? | [U] One conversational line naming the section written, the number of rows it carries, and the plan file's path. No table, no fixed block, and no new fixed-format moment is spent. | FR-01, INV-05 | Rendering the section's rows beneath that line — rejected with DD-01: the file is open to the practitioner, so restating its content in the conversation buys nothing and costs the volume FM-03 identified. A one-line signpost in `cascade`'s fixed form — INV-04 admits a fourth fixed block by criterion rather than quota, so this was available; rejected because a boundary statement is practitioner-facing output, which INV-05 keeps natural, and a fixed form buys cross-run uniformity at the price of formalizing exactly what that principle leaves conversational. Extending `CONFIRM WRITE` to carry the whole section — rejected for growing a block sized for a single row into one sized for an entire section, and for reporting rows before they land when the boundary statement reports what has landed. |
| DD-03 | Where does a design fork's argument render, and what stays in the question card? | [U] The comparison renders as a markdown table in the response body, ahead of the card; the card carries option labels and a one-line restatement and introduces no alternative, reason or consequence absent from that table. Chosen as the option that inherits Altitude's conversational style. | FR-03, FR-04, INV-05, INV-08 | Placing the comparison inside the card's `question` string — viable, since INV-03 establishes no `maxLength` constrains that field, and it would keep briefing and attribution on one surface rather than two; rejected because it formalizes practitioner-facing output that INV-05 keeps natural, and because whether a markdown table renders inside that string is unverified. Splitting the comparison across each option's `preview` field — non-viable: the schema intends `preview` for "visual comparisons that help users compare options", but INV-03 establishes it renders only while its own option is focused, so side-by-side comparison is unreachable, which is the precise defect FR-03 exists to fix. |
| DD-04 | How is the practitioner consulted, and what makes a question batchable? | [U] Iterative conversational Q&A is the default for every question, design forks included, matching Altitude — which contains zero references to `AskUserQuestion` across every skill and framework document, and whose `l0-requirements:56` pattern is "Confirm a best guess before routing if not unambiguous; ask directly if genuinely unclear." Questions are never batched, which is the practice INV-06 already records inside the framework: `cascade` resolves one level fully with the practitioner before advancing to the next, so a hub sequencing one unit at a time is the established pattern rather than a new constraint. `AskUserQuestion` is retained for one purpose only: as a disambiguation fallback, raised when the practitioner's answer is vague or unclear and no best guess is articulable, to force a definitive answer. This satisfies INV-08 by a sharper mechanism than a standing card — the structured selection is deployed exactly when attribution would otherwise be doubtful, rather than on every fork regardless of whether doubt exists. | FR-05, FR-06, FR-09, INV-05, INV-08 | Never batching while retaining the card as the standing channel for every design fork — keeps attribution mechanical on all forks, rejected because it preserves a structured card for output Altitude keeps conversational, and because a card is the weaker briefing surface for any fork whose argument is comparative. A structural batchability test, admitting questions answerable by recall or confirmation — decidable before asking and covering both reported failures, rejected because it preserves batching at all, and the second reported failure is that even a valid batch is a simultaneous demand for several decisions. Retaining the independence predicate with a Design Decisions exception — rejected: it addresses invalidation only, leaving simultaneous demand untouched for every non-fork question. |
| DD-05 | How is a plan ID referred to in conversation? | [U] The agent states the row's content in conversational prose and cites the ID alongside it — "suppressed events never reach the bus (FR-08)" — rather than naming the ID and appending its claim. The content is what the sentence was carrying regardless, so the citation costs a parenthetical and no repetition budget is required. | FR-02, INV-05 | Three ID-leading variants were offered and rejected together, since each rations how often a claim is repeated and that cost exists only because the ID leads the sentence: the claim appended at every mention — unambiguous, but pays a full restatement on every occurrence; the claim on first mention per message — keeps it in view within the message being read, while leaving bare IDs in every earlier message; the claim on first mention per section — cheapest, and leaves most mentions bare, which preserves the defect FR-02 exists to remove. Stating the content and citing the ID eliminates the cost rather than budgeting it. |
| DD-06 | How is the kebab-case slug enforced? | [U] Both halves. Step 3 states the transformation explicitly — lowercase, split on word boundaries, join with hyphens — rather than naming the convention; and after the copy the hub verifies the written filename against `^PLAN__[a-z0-9]+(-[a-z0-9]+)*\.md$`, renaming on failure. | FR-08, INV-07 | The explicit transformation alone — rejected as insufficient against the observed cause: the LogWatcher agent derived `ingestion-event-filtering` correctly in its own investigation heading and still wrote `PLAN__ingestioneventfiltering.md`, so the convention was known and the divergence occurred at the write. Verification alone — sufficient against that cause, rejected because it leaves Step 3 naming a convention where it could state a transform, and a check that has to fire is a worse instruction than one that rarely does. A check inside `plan-audit` — catches the same defect, rejected because it fires only after every section has already referenced the filename, and because it widens the change from one skill to two. |
| DD-07 | What prevents a misread prose answer from reaching a `[U]` cell? | [U] `CONFIRM WRITE` becomes a gate rather than a display, for the single case where a resolution is marked `[U]` and was reached through a prose exchange: the hub emits the block and waits for confirmation before writing. Every other write keeps its existing emit-and-proceed behavior. The block already carries the exact field a misreading would corrupt, so the gate needs no new content and no new fixed-format moment. | FR-10, INV-08 | A separate prose readback sentence ahead of the block — rejected because `CONFIRM WRITE` already displays the resolution and its marker, so the readback would restate the same value twice on consecutive lines. Raising a card for every prose-resolved fork — rejected because it restores `AskUserQuestion` as the standing channel for design forks and so reverses DD-04 in substance while leaving its wording in place. |
| DD-08 | Where does the plan document live? | [U] In the practitioner's own repository — a dedicated plan directory where one exists, otherwise the repository root — left untracked, with the suite performing no git operation of any kind. Keeping the file out of a commit is the practitioner's concern, not the skill's. Where no repository is present the session scratchpad remains the fallback, preserving today's behavior for that case alone. | FR-11, INV-09 | The session scratchpad for every case, which the shipped suite plan's `DD-05` chose "in favor of zero repo footprint" — rejected on two independent grounds. INV-09 makes that path session-specific, so a plan never survives the session that wrote it and the Revise route must decline whenever it is invoked later. INV-10 makes it unlinkable: the scratchpad lies outside the working directory and has no usable relative form, so the practitioner cannot open the document in one click at any point while it is being written — which defeats FR-01's boundary statement and DD-01's entire premise that the practitioner simply opens the file. Placement inside the repository is what makes both work. Committed to the repository — reviewable in a diff beside the code it planned, rejected because every revision then becomes a commit and `plan-audit` findings enter the project's permanent history. A self-ignoring `.plans/` directory carrying its own `.gitignore` of `*` — guarantees nothing leaks into a commit, rejected for contradicting the repository-root preference and for making the suite create infrastructure inside someone else's repository. Appending the plan patterns to the target repository's `.gitignore` — rejected on the same ground: it writes to a tracked file the practitioner owns and lands in their diff. |

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
| `plan/skills/plan/SKILL.md` | Modify | [D::DD-01, DD-02, DD-03, DD-04, DD-05, DD-06, DD-07, DD-08] Rewrite `## Consulting the Practitioner` around iterative conversational Q&A with no batching, retaining `AskUserQuestion` solely as a disambiguation fallback. Add the comparative-view rule for design forks and the constraint on what a fallback card may carry. Add the boundary statement — one line naming the section written, its row count and the file path — and the ID citation convention. In Step 3, resolve the plan's location to the repository (dedicated plan directory, else root, else scratchpad when no repository is present), state the slug transformation explicitly, and verify the written filename after the copy. In Step 4's Revise route, glob the repository rather than the session scratchpad. Make `CONFIRM WRITE` a gate rather than a display for any `[U]` resolution reached through prose. In Step 6, replace the `SendUserFile` delivery with a working-directory-relative markdown link to the plan, and drop `SendUserFile` from `allowed-tools`. Bump `metadata.version` from `0.3.0`. | DD-01 – DD-08, FR-01 – FR-06, FR-08 – FR-11, INV-07, INV-09 |

<!-- One row. `find` over `plan/` returns thirteen files: eight skills, the template, and
     four eval artifacts. A grep for consultation, batching and question-card language
     across every file outside the hub returns nothing, and the investigation established
     that no atomic, `plan-cascade`, `plan-audit` or `plan-investigate` carries any
     practitioner-facing presentation instruction. The repository holds no README or
     documentation describing the suite's behavior, so nothing else goes stale. Every one
     of the nine requirements lands on the hub. -->


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
| FM-01 | A section completes and the boundary statement is not emitted. | [D::DD-02] No fixed form governs that statement, so its absence looks identical to a section that completed silently, and nothing in the conversation records that a section landed. The practitioner's recourse is the file itself, which DD-08 keeps open in their repository — so the state is always recoverable without the agent. | Low | [U] Yes — accepted while this mode carried Medium severity under a rendering design; the pivot to an in-repo document reduced it to Low, since the authoritative state is readable at any moment regardless of what the conversation says. |
| FM-02 | The practitioner answers a prose-asked design fork in a way that reads clearly but is ambiguous, and the agent's best guess is articulable and wrong. | [D::DD-04, DD-07] The fork resolves on the agent's reading and a `[U]` marker records a resolution the practitioner never chose, which is precisely what INV-08 exists to prevent. The FR-09 fallback does not catch it: that fallback fires only where *no* best guess is articulable, so a confident misreading passes straight through. Prevented by DD-07 via FR-10 — `CONFIRM WRITE` becomes a gate for any `[U]` resolution reached through prose, so the agent's reading is displayed and confirmed before it is written. | Critical | [U] No — prevented by DD-07 via FR-10. |
| FM-04 | A long authoring session, with the agent stating row content in prose and citing the ID. | [D::DD-05] The stated content drifts from the row's actual text. Under an ID-leading convention the appended claim quoted the cell; under DD-05's inversion it is the agent's own prose, so the practitioner can read a paraphrase, take it for the row, and be wrong about what the plan says. | Low | [U] Yes — the plan is an open file in the practitioner's repository under DD-08, so the authoritative text is one click away whenever the paraphrase matters. |
| FM-05 | The practitioner runs `git add -A` in a repository where a plan document is present. | [D::DD-08] The plan and its investigation record are committed. DD-08 has the suite perform no git operation of any kind, so nothing marks these files as untracked-by-intent and nothing prevents their inclusion. | Low | [U] Yes — managing what enters a commit is the practitioner's responsibility, not the skill's, and the accidental-commit risk was accepted explicitly in preference to the suite writing to `.gitignore` or creating a directory inside someone else's repository. |

<!-- FM-03 retired during authoring. It recorded a many-rowed section rendering as a large
     table in the conversation at every boundary, reproducing the volume problem the render
     was meant to solve. DD-01's reframing removed rendering from the conversation entirely,
     so the trigger no longer exists. Its ID is retired, never reissued. -->

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
| RK-01 | [V] The suite had never been executed before this session. All eight skills were authored, committed and installed by junction without a single run, and every verification procedure in the shipped plan is written but unexecuted. This session is the first execution, and it exercises the hub while authoring a plan *about* the hub — an unusual load rather than a representative one. | High | Degraded | Run `plan` on a small unrelated task in a different repository after the edit lands, and walk FR-01, FR-05, FR-06, FR-09, FR-10 and FR-11 against their verification procedures before treating the revision as complete. |
| RK-02 | [V] The installed suite is nine Windows junctions under `~/.claude/skills/` pointing into this repository, so an edit to `plan/skills/plan/SKILL.md` is live the instant it is saved. There is no deploy step, no staging copy and no version pinning between the working tree and what a session loads. A half-applied edit is a live half-applied hub. | High | Degraded | Apply the whole rewrite of the hub in one write rather than incrementally, and read the finished file end to end before invoking `plan` again in any session. |
| RK-03 | [V] FR-09's trigger — that no best guess is articulable — is a judgment the agent makes about its own state, and nothing outside the agent can check it. Its verification procedure exercises the case where ambiguity is recognised, never the case where it is not, so FR-09 cannot be shown by testing to catch what it is meant to catch. | Medium | Degraded | Treat FR-10's blocking `CONFIRM WRITE` as the load-bearing control and FR-09 as a convenience on top of it, so that a failure of FR-09's self-assessment is caught by the gate before it reaches a cell rather than being relied upon to fire. |
| RK-04 | [V] Every verification in this plan is of the form "invoke `plan`; observe X", requiring a human observer. No automated check exists anywhere in the suite: `plan-audit` inspects the finished document, not the hub's behavior, and an external validator was excluded at the suite's inception. Nothing regression-tests the hub, so a later edit can silently undo any of these nine requirements. | High | Degraded | Carry the verification procedures into the final Implementation Order step as an explicit checklist, so the manual run is a step that is performed rather than an intention that is recorded. |

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
     gated was written: scope election, the Problem Statement wording, the Non-goal set,
     eight design forks, four failure-mode verdicts, and the three facets of DD-08. Nothing
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
| S-01 | [D::DD-01, DD-02, DD-03, DD-04, DD-05, DD-06, DD-07, DD-08] Apply the whole hub rewrite in a single write: `## Consulting the Practitioner` recast around iterative prose Q&A with no batching and the card as disambiguation fallback; the comparative-view rule for design forks and the constraint on fallback card content; the boundary statement and the ID citation convention; Step 3's location resolution, slug transformation and post-copy filename verification; the Revise route's glob moved from scratchpad to repository; `CONFIRM WRITE` made a gate for prose-reached `[U]` resolutions; Step 6's delivery reduced to naming the path, with `SendUserFile` dropped from `allowed-tools`; `metadata.version` bumped from `0.3.0`. | `plan/skills/plan/SKILL.md` | DD-01, DD-02, DD-03, DD-04, DD-05, DD-06, DD-07, DD-08 | — |
| S-02 | [D::DD-01, DD-08] Read the finished hub end to end, confirming the six edited regions read coherently together and that no instruction still refers to the scratchpad, to `SendUserFile` delivery, or to batching. | `plan/skills/plan/SKILL.md` | — | S-01 — RK-02: the junction install makes the file live the instant it is saved, so this read is the only check standing between the write and the next session that loads it. |
| S-03 | [D::RK-01, RK-04] Run the verification checklist by invoking `plan` on a small unrelated task in a different repository, walking each requirement against its own `Verification` cell. | — | FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-08, FR-09, FR-10, FR-11 | S-02 — the suite has never been executed end to end, and nothing in it regression-tests the hub, so this run is the only evidence any of the ten requirements holds. |

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
