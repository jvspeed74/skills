---
template_version: "1.4.0"
---

# Implementation Plan: Ingestion Event Filtering
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

[U] `FilesystemWatcherAdapter.PublishEvent` calls `_bus.Publish(ev)` for every filesystem event the OS reports, without consulting the `Processable` flag it has just computed. Events for extensions the system will never process therefore consume `BoundedEventBus` capacity, are dequeued by a worker, and increment `stats.Active.IncrementFsEvent(ToStatEventKind(ev.Kind))` before the routing switch discards them. Two further consequences follow downstream. `ProcessingCoordinator.WorkerLoop` invokes `HandleDelete` for every `Deleted` event with no `Processable` check, so `_registry.TryGet` misses and `LogDeleteUntracked` fires at Debug level for a path that was never tracked. Its `Renamed` case gates `HandleDelete(ev.OldPath)` on `!string.IsNullOrEmpty(ev.OldPath)` alone, with no processability check on the old path, producing the same Debug-level noise whenever the old path was non-processable. The cost is bus capacity spent on events that cannot produce work, filesystem-event statistics that overcount by the volume of non-target file activity in the watched directory, and log noise for entirely expected behavior. The operator reading those statistics cannot distinguish real ingestion load from directory churn.

[U] Beneath that defect sits its cause. Processability is carried as a `bool` on `FsEvent` and re-interpreted independently at each consumer, so nothing in the type system prevents a consumer from reading the flag wrongly, ignoring it, or pairing it with a path it does not describe. The `Renamed` case makes this concrete: one flag describes the new path while the routing decision for the old path has no flag at all, which is why the old-path guard degenerated into a null check. A boolean beside a path is an assertion any consumer may re-litigate; the classification needs to be a property of the value rather than an annotation travelling next to it.

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
| INV-01 | [V] Only `.log` and `.txt` files are treated as processable, matched case-insensitively, with an empty extension never processable. (ING-003, first clause — the classification rule this plan relocates but does not change.) | `docs/L5__LogWatcher__Invariants.md:164` states it; `FilesystemWatcherAdapter.DefaultIsProcessable` (lines 77–84) implements it, comparing the extension against `log` and `txt` with `StringComparison.OrdinalIgnoreCase` and returning `false` for a null or empty extension. |
| INV-02 | [V] Every byte appended to a watched file is eventually processed, assuming events are not permanently suppressed by the OS. (PROC-005) | `docs/L5__LogWatcher__Invariants.md:111`, typed `behavioral`, Modules `PROC, BP`; covered by the test tagged `[Invariant("PROC-005")]` at `LogWatcher.Tests/Integration/ProcessingCoordinatorTests.cs:153`. |
| INV-03 | [V] Watcher callbacks never perform IO, blocking operations, or heavy computation. (ING-001) | `docs/L5__LogWatcher__Invariants.md:162`; the four callbacks `OnCreated`, `OnChanged`, `OnDeleted` and `OnRenamed` (lines 86–104) delegate immediately to `PublishEvent`, whose only non-trivial work is the classification call. |
| INV-04 | [V] A publish failure due to a full bus is silent to the watcher; the watcher never retries or blocks, and publishers never block waiting for queue capacity. (ING-002, BP-006) | `docs/L5__LogWatcher__Invariants.md:163` and the `BP-006` row; `BoundedEventBus.Publish` (lines 59–78) uses `TryWrite` under `FullMode = Wait` and returns a bool without ever awaiting. |
| INV-05 | [V] Every invariant ID present in `docs/L5__LogWatcher__Invariants.md` has at least one `[Invariant("ID")]`-tagged test, and every tagged ID exists in that document. | `LogWatcher.Tests/InvariantCoverageTests.cs`: `DefinedInvariant_HasAtLeastOneTaggedTest` (lines 26–36) and `TaggedInvariant_ExistsInMarkdown` (lines 48–56) are xUnit theories failing hard in both directions; the document is supplied as an `EmbeddedResource` declared in `LogWatcher.Tests.csproj`. |
| INV-06 | [V] The worker event loop catches all exceptions at its boundary — no exception propagated from a downstream module terminates a worker thread. (PROC-009) | `docs/L5__LogWatcher__Invariants.md:115`; `ProcessingCoordinator.WorkerLoop` wraps the entire routing switch in `try` / `catch (Exception)` at lines 107–134, logging `LogWorkerEventException` at Error. |

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
| FR-01 | [U] `ProcessablePath.From` shall return a value if and only if the supplied path's extension is `log` or `txt`, compared case-insensitively. | Unit test over `.log`, `.LOG`, `.txt`, `.TXT`, `.bak`, `.tmp`, a path with no extension, an empty string, and null; assert presence for the first four and absence for the rest. Tagged `[Invariant("ING-003")]`. |
| FR-02 | [U] The Ingestion domain shall expose no public constructor for `ProcessablePath`; `From` shall be its only producer. | Reflection test asserting `typeof(ProcessablePath).GetConstructors(BindingFlags.Public \| BindingFlags.Instance)` returns no entry taking a `string`. |
| FR-03 | [U] WHEN `PublishEvent` receives a `Created` or `Modified` event whose path is processable, the Ingestion domain shall publish an `FsWork` of kind `Create` or `Modify` respectively, carrying that path. | Ingestion unit test asserting the dequeued `FsWork.Kind` and the payload path for each of the two kinds. |
| FR-04 | [U] WHEN `PublishEvent` receives a `Deleted` event whose path is processable, the Ingestion domain shall publish an `FsWork` of kind `Delete` carrying that path. | Ingestion unit test asserting the dequeued `FsWork.Kind` is `Delete` and `TryGetDelete` yields the path. |
| FR-05 | [U] WHEN `PublishEvent` receives a `Renamed` event whose old and new paths are both processable, the Ingestion domain shall publish an `FsWork` of kind `Replace` carrying the old path as `Remove` and the new path as `Add`. | `FsWork.From` unit test for `app.log` → `app.txt`, asserting kind and both payload paths. |
| FR-06 | [U] WHEN `PublishEvent` receives a `Renamed` event whose new path alone is processable, the Ingestion domain shall publish an `FsWork` of kind `RenameIn` carrying the new path as `Add`. | `FsWork.From` unit test for `app.bak` → `app.log`, asserting kind and payload path. |
| FR-07 | [U] WHEN `PublishEvent` receives a `Renamed` event whose old path alone is processable, the Ingestion domain shall publish an `FsWork` of kind `RenameOut` carrying the old path as `Remove`. | `FsWork.From` unit test for `app.log` → `app.bak`, asserting kind and payload path. |
| FR-08 | [U] IF an `FsEvent` has no processable path, THEN `FsWork.From` shall return no value and the Ingestion domain shall not publish it to the bus. | `FsWork.From` unit test asserting absence for a non-processable `Created`, `Modified` and `Deleted`, and for `app.tmp` → `app.bak`; plus an adapter test asserting `_bus.Publish` is not reached. |
| FR-09 | [U] WHEN the Ingestion domain suppresses an event, it shall not call `_bus.Publish`, and neither `BoundedEventBus.PublishedCount` nor `BoundedEventBus.DroppedCount` shall change. | Ingestion unit test capturing both counters before and after a suppressed event and asserting equality. |
| FR-10 | [U] WHEN the Ingestion domain suppresses an event, it shall emit a Debug-level log entry naming the event kind and the affected path. | Ingestion unit test with `CapturingLogger<FilesystemWatcherAdapter>` asserting exactly one Debug entry naming the suppressed path, and zero `LogEventPublished` entries. |
| FR-11 | [U] IF the adapter is about to publish an `FsWork` whose payload carries a `ProcessablePath` with a null `Value`, THEN it shall log at Warning and shall not publish it. | Ingestion unit test invoking the publish guard with a forged payload, asserting no publish and one Warning entry. |
| FR-12 | [U] The test suite shall fail if the `default` expression is used to construct `ProcessablePath`, `FsWork`, or any `FsWork` payload type anywhere in the solution's source. | A syntax-analysis test walking every `.cs` file in the solution and asserting no `DefaultExpressionSyntax` or `LiteralExpressionSyntax` of kind `DefaultLiteralExpression` resolves to one of those types. |
| FR-13 | [U] The Ingestion domain shall not expose `FsEvent` outside the `LogWatcher.Core.Ingestion` namespace. | Reflection test asserting `typeof(FsEvent).IsPublic` is false; enforced additionally by the compiler, since no public signature may name an internal type. |
| FR-14 | [U] `FsEvent` shall carry only facts the operating system reports: event kind, path, old path, and observation time. | Reflection test asserting `FsEvent`'s property set is exactly `Kind`, `Path`, `OldPath`, `ObservedAt`. |
| FR-15 | [U] WHEN `ProcessingCoordinator` dequeues an `FsWork`, it shall increment the work counter for that work kind exactly once. | Coordination test publishing one work item of each kind and asserting each counter advances by exactly one. |
| FR-16 | [U] WHEN `ProcessingCoordinator` routes an `FsWork`, it shall invoke `HandleDelete` for kinds `Delete`, `RenameOut` and `Replace`, and `HandleCreateOrModify` for kinds `Create`, `Modify`, `RenameIn` and `Replace`. | Coordination tests over all six kinds with a recording `FakeProcessor` and a registry probe, asserting which handler ran for each. |
| FR-17 | [U] The system shall not emit `LogDeleteUntracked` for any event whose corresponding path is non-processable. | Coordination test with a capturing logger asserting zero `LogDeleteUntracked` entries for a non-processable delete and for `app.bak` → `app.log`. |
| FR-18 | [U] `GlobalSnapshot.FsRenamed` shall equal the sum of the `RenameIn`, `RenameOut` and `Replace` work counters, so the console report retains its four filesystem-event lines. | `GlobalSnapshotTests` case seeding the three rename counters and asserting `FsRenamed` equals their sum; `ConsoleSnapshotConsumer` output compared against its current four-line shape. |
| FR-19 | [U] The `FilesystemWatcherAdapter` constructor shall not accept a processability predicate. | Reflection test asserting no constructor parameter of type `Func<string, bool>`; enforced additionally by the compiler at all five construction sites. |

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

<!-- Zero rows: no measurable performance threshold was stated for this task,
     and none was measured. The allocation posture is carried instead by
     DD-04, which keeps every new type a struct. -->

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
| NG-01 | [U] Modifying any domain other than Ingestion (1), Processing Coordination (8), Statistics Collection (9), Reporting (11) and CLI & Host (12) | The original Fix Scope table named Domains 1 and 8. It was amended to admit Domain 9, because counters keyed to OS event kinds are the wrong measure once work items exist, and Domains 11 and 12, which carry the bus's generic argument. No other namespace is touched. |
| NG-02 | [U] Changing the processable extension set | The set stays `.log` and `.txt`. This plan relocates the rule into `ProcessablePath.From` without altering which extensions it admits. |
| NG-03 | [U] Moving extension filtering to `FileSystemWatcher.Filter` or `NotifyFilter` | Excluded in favor of the in-process gate. An OS-level filter matches the new name only and cannot express the rename cases. |
| NG-04 | [U] Correcting statistics already inflated by previously published non-processable events | The fix is forward-only; no backfill, reset, or annotation of historical counters. |
| NG-05 | [U] Correlating renames the OS reports as separate `Deleted` + `Created` pairs | Reconstructing a logical rename from an uncorrelated pair is a separate concern from gating the `Renamed` events the OS does report. |
| NG-06 | [U] Changing the console report's four filesystem-event lines | FR-18 preserves the report's shape. Only the values change, and only by ceasing to count events that were never processable. |

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
| DD-01 | How is processability represented, so that no consumer can re-litigate or misread it? | [U] As a value object. `ProcessablePath` is a `readonly record struct` whose existence is the proof: a private constructor plus `static From(string?) : ProcessablePath?` as the sole producer, with the `.log` / `.txt` rule living inside `From`. Downstream code receives a proven path rather than a path plus a flag. | FR-01, FR-02, INV-01 | A `bool Processable` field beside the path — the defect's cause: an assertion travelling next to a value, which the `Renamed` case already proved can be paired with the wrong path or absent for the path that matters; a `bool OldPathProcessable` companion field with `[MemberNotNullWhen]` and a validating initializer — enforces the pairing at runtime rather than making it unrepresentable, and leaves an always-true `Processable` on every bus item once the gate exists; an `IsProcessable` predicate re-invoked at each consumer — puts extension-filtering policy in Module 8, whose In Scope list excludes it. |
| DD-02 | What does `FsEvent` become? | [U] `FsEvent` keeps its name and its role as the raw OS observation, narrowed to `(FsEventKind Kind, string Path, string? OldPath, DateTimeOffset ObservedAt)` and made `internal` to `LogWatcher.Core.Ingestion`. `Processable` is removed: it is not a fact the OS reports, and with the predicate gone nothing would compute it. | FR-13, FR-14, FR-19, NG-02 | Keeping `Processable` on `FsEvent` — requires a classification call on the raw type alongside `ProcessablePath.From`, so two places answer the same question; renaming `FsEvent` to `OsFileEvent` and giving the published type the name `FsEvent` — avoids touching Modules 11 and 12 but makes `FsEvent` name the parsed type rather than the filesystem event; leaving `FsEvent` public — exports a type whose only purpose is to be parsed away immediately, and invites a consumer to observe unparsed events. |
| DD-03 | What crosses the Ingestion boundary, and at what granularity? | [U] A tagged union in the enum result style. `FsWork` is the bus payload, carrying `FsWorkKind Kind`, `DateTimeOffset ObservedAt`, `static From(FsEvent) : FsWork?` as the gate, and `TryGet…` accessors over six payload types: `FsCreate(Target)`, `FsModify(Target)`, `FsDelete(Target)`, `FsRenameIn(Add)`, `FsRenameOut(Remove)` and `FsReplace(Remove, Add)`. Every payload field is a non-nullable `ProcessablePath`. | FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-16, FR-18, INV-02 | One type holding optional `ToProcess` and `ToDelete` paths — a single type meaning both "delete this" and "process this", two responsibilities and two nullables; a two-case `Process`/`Delete` work item where a rename publishes two items — zero optionals, but one rename then consumes two slots of bounded capacity and its halves can be dequeued by different workers, losing rename atomicity; four kinds folding `RenameIn` into `Create` and `RenameOut` into `Delete` — a smaller switch, but those two cases stop counting as renames and the console's `renamed` line silently changes meaning. |
| DD-04 | Is `ProcessablePath` a struct or a reference type? | [U] A `readonly record struct`. Zero allocation on the ingestion path, consistent with `FsEvent` and `FsWork` being structs and with the repository's `BoundedEventBusBenchmarks` posture. The consequence is accepted knowingly: C# gives every struct a `default` that bypasses the private constructor, so `default(ProcessablePath)` carries a null `Value` while claiming to be proven. | FR-02, FM-01 | A `sealed record class` — removes the forgeable default entirely, since absence becomes null and nullable reference types catch it at compile time, at roughly 24 bytes per proven path on x64 (one allocation per single-path work item, two per `FsReplace`); dropping the type and letting the payload structs hold plain strings — one fewer type, but the same forgeable default simply moves onto those structs and `ING-003` loses its dedicated, directly testable home. |
| DD-05 | What prevents a forged `default` from routing as valid work? | [U] Two layers. The adapter refuses to publish an `FsWork` whose payload path has a null `Value`, logging at Warning; and a syntax-analysis test fails the build if the `default` expression is used to construct `ProcessablePath`, `FsWork` or any payload type anywhere in the solution. The test is the primary defense, since it catches forgery at every site rather than only on the adapter-fed route. | FR-11, FR-12, FM-01, FM-02, INV-06 | Reserving `FsWorkKind.None = 0` so `default(FsWork).Kind` is inert — costs nothing on the hot path, but adds a permanently invalid case to a closed set the gate can never produce; a null check on every dequeued item in `WorkerLoop` — catches a forged payload inside an otherwise well-formed `FsWork` too, at one branch per dequeued item on the hot path. |
| DD-06 | Where does the gate live, and what is suppression? | [U] Suppression is `FsWork.From` returning no value, and `PublishEvent` simply does not publish when it does. The gate is a pure static function over `FsEvent`, total across all ten combinations of kind and path processability. | FR-08, FR-09, FR-17, INV-02, INV-03, INV-04 | An early `return` inside `PublishEvent` guarded by boolean checks — buries the gate in a private method reachable only through the real `FileSystemWatcher`, so its ten cases can be tested only through OS event delivery and a timeout; an OS-level `FileSystemWatcher.Filter` — excluded by NG-03; a gate in the coordinator — the bus capacity cost this plan exists to remove is already paid before the coordinator sees the event. |
| DD-07 | Is suppression observable at runtime? | [U] A Debug-level `LoggerMessage` entry per suppressed event naming the kind and the path, replacing the `LogEventPublished` Debug entry those same events produce today, so Debug volume is held roughly constant rather than dropped. | FR-10, FM-04, INV-03 | Silent suppression — leaves filter volume unmeasurable at runtime, with no way to distinguish a correctly filtered directory from a misconfigured rule; a distinct suppressed counter on the adapter — adds a member to Ingestion's public surface that nothing reads, since `Reporter` is constructed over `WorkerStats[]` and the bus and holds no adapter reference. |
| DD-08 | What do the statistics counters count, and what does the console print? | [U] Counters count work performed, one per `FsWorkKind`, so `FsWork` carries no originating `FsEventKind`. `GlobalSnapshot` preserves its four existing properties by summing `RenameIn`, `RenameOut` and `Replace` into `FsRenamed`, leaving `ConsoleSnapshotConsumer` untouched and the report's four lines intact. | FR-15, FR-18, NG-01, NG-06 | Keeping per-OS-kind counters and carrying `FsEventKind` on `FsWork` — byte-identical output, but re-couples the work type to the OS vocabulary it was separated from and preserves counters that inflate with directory churn; three work counters mapped onto four console lines — unreachable, because `Create` and `Modify` would have to be merged and cannot then be split apart again; letting the report drop to three lines — truest counters, but changes a published CLI contract, which NG-06 excludes. |
| DD-09 | What becomes of `Start_WhenNonProcessableFileCreated_PublishesEventWithProcessableFalse`, the sole `ING-003`-tagged test, which asserts the behavior being removed? | [V] It is replaced. The `[Invariant("ING-003")]` tag moves to the `ProcessablePath.From` classification test of FR-01, and the adapter test is rewritten to assert non-publication for a non-processable file. | INV-05, FR-01, FR-08, FR-09 | Delete it and add nothing — non-viable: it is the only test tagged `ING-003`, so `DefinedInvariant_HasAtLeastOneTaggedTest` fails for `ING-003` in CI; retain it unchanged alongside a new test — non-viable: it asserts `bus.PublishedCount > 0` for `x.dat` at line 65 and then dequeues expecting an event, both of which the gate falsifies, so the suite fails regardless of what is added beside it. |
| DD-10 | How is the invariant register restructured? | [U] `ING-003` is revised in place to state the relocated classification rule, and one new row `ING-004` is added, typed `contract`, Modules `ING, PROC`, stating that a rename whose old path was processable always yields work that deletes it. Each ships with a tagged test in the same change. | INV-01, INV-05, FR-01, FR-07 | Splitting into three rows — leaves `invariant_definition.md` Example C's Gate 7 reasoning wholly untouched, but costs a third ID and a third tagged test; revising `ING-003` alone with no new row — places a cross-module contract obligation inside a row typed `behavioral` and scoped to Modules `ING` alone, contradicting `invariant_definition.md`'s stated priority that `contract` outranks `behavioral`. |

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
| `LogWatcher.Core/Ingestion/ProcessablePath.cs` | Create | [D::DD-01, DD-04] The `readonly record struct` with `Value`, a private constructor, and `static From(string?)` carrying the `.log` / `.txt` rule relocated from `DefaultIsProcessable`. | DD-01, DD-04, FR-01, FR-02, INV-01 |
| `LogWatcher.Core/Ingestion/FsWork.cs` | Create | [D::DD-03, DD-06] `FsWorkKind`, the six payload structs, and `FsWork` with `Kind`, `ObservedAt`, the `TryGet…` accessors, and `static From(FsEvent)` implementing the gate across all ten kind-by-processability combinations. | DD-03, DD-06, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08 |
| `LogWatcher.Core/Ingestion/FsEvent.cs` | Modify | [D::DD-02] Drop the `Processable` parameter; change `public` to `internal`; update the XML docs. | DD-02, FR-13, FR-14 |
| `LogWatcher.Core/Ingestion/FilesystemWatcherAdapter.cs` | Modify | [D::DD-02, DD-05, DD-06, DD-07] Bus field and constructor parameter become `BoundedEventBus<FsWork>`; remove the `isProcessable` parameter, the `_isProcessable` field and `DefaultIsProcessable`; `PublishEvent` builds an `FsEvent`, calls `FsWork.From`, applies the publish guard, then publishes or logs suppression; add `LogEventSuppressed` and `LogInvalidWorkRejected` `LoggerMessage` declarations. | DD-02, DD-05, DD-06, DD-07, FR-09, FR-10, FR-11, FR-19 |
| `LogWatcher.Core/Processing/ProcessingCoordinator.cs` | Modify | [D::DD-03, DD-08] Bus field and constructor parameter become `BoundedEventBus<FsWork>`; replace `ToStatEventKind` and the `FsEventKind` switch with a six-arm switch over `FsWorkKind` using the `TryGet…` accessors; `IncrementFsWork` fires unconditionally at line 110, correct because every published item does work by construction. | DD-03, DD-08, FR-15, FR-16, FR-17 |
| `LogWatcher.Core/Statistics/StatEventKind.cs` | Modify | [D::DD-08] Replace the four OS-kind values with the six work kinds. | DD-08, FR-15 |
| `LogWatcher.Core/Statistics/WorkerStatsBuffer.cs` | Modify | [D::DD-08] Replace the four `Fs*` counter fields and `IncrementFsEvent` with six work counters and `IncrementFsWork`. | DD-08, FR-15 |
| `LogWatcher.Core/Reporting/GlobalSnapshot.cs` | Modify | [D::DD-08] Merge the six work counters, and expose the existing four properties by summing `RenameIn`, `RenameOut` and `Replace` into `FsRenamed`. | DD-08, FR-18, NG-06 |
| `LogWatcher.Core/Reporting/Reporter.cs` | Modify | [V] Change the bus generic argument at lines 19 and 49 to `BoundedEventBus<FsWork>`. Mechanical; no behavioral change. | DD-03, NG-01 |
| `LogWatcher.App/LogWatcherService.cs` | Modify | [V] Change the bus generic argument at lines 34 and 45 to `BoundedEventBus<FsWork>`, and drop the now-absent predicate argument at line 57. | DD-02, DD-03, FR-19, NG-01 |
| `docs/L5__LogWatcher__Invariants.md` | Modify | [V] Revise the `ING-003` Description at line 164; append `ING-004`, typed `contract`, Modules `ING, PROC`. The file is an `EmbeddedResource` read by `InvariantCoverageTests`, so both edits are load-bearing for CI. | DD-10, INV-05 |
| `docs/invariant_definition.md` | Modify | [V] Update the `ING-003` Description quoted in Example C at lines 378–381 to match the revised register text. | DD-10, INV-05 |
| `docs/system_diagram.md` | Modify | [V] Replace the `FsEvent` field list at line 156 — the only field-list rendering of the type in the repository — with the new `FsEvent`, `ProcessablePath` and `FsWork` shapes. | DD-01, DD-02, DD-03 |
| `docs/concurrency_model.md` | Modify | [V] Qualify the routing transitions at lines 120 and 142, which currently read `Created / Modified (Processable=true)` and `HandleDelete(old) + HandleCreateOrModify(new)`, to describe work-kind routing. | DD-03, FR-16 |
| `docs/L5__LogWatcher__Module_Boundaries.md` | Modify | [V] Rewrite Module 1's Data Ownership and Contracts blocks (lines 52–63) for `ProcessablePath` and `FsWork`; update Module 8's `FsEvent` Data-inbound entry and its `IncrementFsEvent` outbound entry; update Module 9's and Module 11's entries for the work counters. | DD-01, DD-03, DD-08, NG-01 |
| `LogWatcher.Tests/Unit/Core/Ingestion/ProcessablePathTests.cs` | Create | [D::DD-01, DD-09] The FR-01 classification cases, tagged `[Invariant("ING-003")]`, and the FR-02 reflection test. | DD-01, DD-09, FR-01, FR-02, INV-05 |
| `LogWatcher.Tests/Unit/Core/Ingestion/FsWorkTests.cs` | Create | [D::DD-03, DD-06] The gate's ten kind-by-processability cases, including at least one tagged `[Invariant("ING-004")]`, plus the FR-13 and FR-14 reflection tests. | DD-03, DD-06, DD-10, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-13, FR-14, INV-05 |
| `LogWatcher.Tests/Unit/Core/Ingestion/DefaultConstructionTests.cs` | Create | [D::DD-05] The FR-12 syntax-analysis test walking the solution's `.cs` files for `default` expressions resolving to `ProcessablePath`, `FsWork` or a payload type. | DD-05, FR-12 |
| `LogWatcher.Tests/Unit/Core/Ingestion/FilesystemWatcherAdapterTests.cs` | Modify | [V] Rewrite `Start_WhenNonProcessableFileCreated_PublishesEventWithProcessableFalse` (lines 48–76) as a non-publication assertion; move its `ING-003` tag to `ProcessablePathTests`; add the FR-09, FR-10, FR-11 and FR-19 tests; update the two `new FsEvent(` sites at lines 88 and 95. | DD-05, DD-07, DD-09, FR-09, FR-10, FR-11, FR-19 |
| `LogWatcher.Tests/Integration/ProcessingCoordinatorTests.cs` | Modify | [V] Add the FR-15, FR-16 and FR-17 tests over all six work kinds, reusing the in-file `FakeProcessor`; convert the eight `new FsEvent(` sites at lines 88, 90, 119, 143, 168, 187, 231 and 237 to `FsWork` factory calls and change the bus generic argument. | DD-03, DD-08, FR-15, FR-16, FR-17 |
| `LogWatcher.Tests/Integration/HostLifecycleTests.cs`, `Integration/ReporterTests.cs`, `Integration/WorkerStatsSwapTests.cs`, `Stress/SyntheticStressTests.cs` | Modify | [V] Change bus generic arguments and convert `new FsEvent(` sites at `HostLifecycleTests.cs:90`, `ReporterTests.cs:20` and `SyntheticStressTests.cs:54`; update the `FsCreated` and `StatEventKind` references the counter rename reaches. No assertion in these files depends on behavior this plan changes — `HostLifecycleTests.cs:100` asserts `FsCreated >= 0`, a tautology on a `long`. | DD-03, DD-08, NG-01 |
| `LogWatcher.Tests/Unit/Core/Statistics/WorkerStatsBufferTests.cs`, `Unit/Core/Reporting/GlobalSnapshotTests.cs` | Modify | [V] Update the seven `StatEventKind` and six `Fs*` counter references to the work counters; add the FR-18 case asserting `FsRenamed` equals the sum of the three rename counters. | DD-08, FR-15, FR-18 |
| `LogWatcher.Tests/LogWatcher.Tests.csproj` | Modify | [D::DD-05] Add the package reference the FR-12 syntax-analysis test requires. | DD-05, FR-12 |
| `LogWatcher.Benchmarks/BoundedEventBusBenchmarks.cs` | Modify | [V] Change the bus generic argument and convert the `new FsEvent(` site at lines 28–33 to an `FsWork` factory call. Compile-forced; no benchmark behavior changes. | DD-03 |

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
| FM-01 | Code writes `default(ProcessablePath)`, bypassing the private constructor. | [D::DD-04, DD-05] The value carries a null `Value` while presenting as a proven path. Reaching `HandleDelete` or `HandleCreateOrModify` it would pass null to the registry. DD-05's syntax-analysis test (FR-12) fails the build at any such site, and DD-05's publish guard (FR-11) rejects it on the adapter route. | Medium | [U] Yes — the forgeable default is inherent to any struct in C# and was accepted knowingly when DD-04 chose the struct for zero allocation; FR-12 converts it from a latent hole into a build failure. |
| FM-02 | Code writes `default(FsWork)` and publishes it. | [D::DD-03, DD-05] `FsWorkKind`'s zero value is `Create`, so the item presents as a create carrying a default payload with a null `Value`. If one reached `WorkerLoop` it would pass null to `GetOrCreate` and throw `NullReferenceException`, caught by the PROC-009 boundary catch at lines 107–134 and logged at Error, leaving the worker alive. Prevented by FR-11 on the adapter route and by FR-12 at every construction site. | Medium | [U] No — prevented by DD-05 via FR-11 and FR-12. |
| FM-03 | A processable file is deleted having never been created or modified while the watcher ran. | [D::DD-03, DD-06] The path classifies, so `FsWork.From` yields `FsDelete`, the item publishes and routes, and `HandleDelete` hits a `TryGet` miss, emitting `LogDeleteUntracked` at Debug. FR-17 removes this noise only for non-processable paths; this case survives by design. | Low | [U] Yes — the path genuinely was processable, so the Debug line reports a real and informative condition rather than the expected-noise case FR-17 targets. |
| FM-04 | A watched directory carries heavy non-target churn, such as `.tmp` or `.bak` write traffic. | [D::DD-07] FR-10 emits one Debug entry per suppressed event, so Debug volume stays proportional to that churn — the same volume `LogEventPublished` produces for those events today, held constant rather than added. | Low | [U] Yes — suppression must remain observable, and holding Debug volume constant is the cost of that; the plan reduces bus and statistics pressure regardless of log level. |

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
| RK-01 | [V] The FR-12 syntax-analysis test needs a package this solution does not reference. `LogWatcher.Tests.csproj` currently carries only `coverlet.collector`, `Microsoft.NET.Test.Sdk`, `System.CommandLine`, `xunit` and `xunit.runner.visualstudio`, and no project in the repository references Roslyn. | High | Degraded | Add `Microsoft.CodeAnalysis.CSharp` to `LogWatcher.Tests.csproj` as the first step of S-09 and confirm the suite still builds under `TreatWarningsAsErrors` before writing the test body. If the dependency proves unacceptable, fall back to a text scan over the same file set, which needs no package. |
| RK-02 | [V] This plan spans 24 files across five modules, where the originating issue described a defect in two. `TreatWarningsAsErrors` is set in both `LogWatcher.Core.csproj` and `LogWatcher.Tests.csproj`, so every intermediate state that leaves a stale `FsEvent` construction or an old counter name fails the build rather than warning. | High | Degraded | Follow Implementation Order strictly: land the new Ingestion types first (S-01 to S-03), then convert consumers in dependency order, and do not run the suite expecting green until S-08 completes. |
| RK-03 | [V] The adapter's non-publication assertions must wait out a timeout. `PublishEvent` stays private and the existing tests poll the real `FileSystemWatcher` for up to 2s, so asserting that nothing was published can only mean waiting a fixed interval and then checking the counters. A regression that re-introduced publishing after the wait window would pass. | Medium | Degraded | Put the ten gate cases in `FsWorkTests` against `FsWork.From` directly, where they are synchronous and total, and leave the adapter test as a single end-to-end confirmation rather than the primary coverage for FR-08. |
| RK-04 | [V] No build or test run informed this plan. Every claim about what compiles or which test fails is read from source; in particular, "the existing `ING-003` test fails" is an inference from its assertions at lines 48–76 against the planned change, not a recorded failure. | Medium | Cosmetic | Run `dotnet build` and `dotnet test` before S-01 to capture a known-green baseline, so any failure after that point is attributable to this change rather than to a pre-existing condition. |
| RK-05 | [V] `docs/invariant_definition.md` Example C walks all nine classification gates against `ING-003`'s current text. Its Gate 7 reasoning — that Processing Coordination "trusts the `Processable` field, not the extension logic" — describes a field this plan deletes, so the worked example may need more than the Description line updated. | Medium | Cosmetic | Re-read Example C's Gate 1, 2 and 7 text during S-10 and update whichever gates reference the removed field, rather than editing only the quoted Description. |

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

     Provenance: the marker prefixes `Step`. The sequence is generally
     deduced from the decisions and file set above, in which case the marker
     names what each step carries out. Where the reviewer dictated an
     ordering this plan's own content does not imply, the marker records it
     as theirs instead. -->

| # | Step | Files | Implements | Depends On |
|---|---|---|---|---|
| S-00 | [D::RK-04] Capture a green baseline with `dotnet build` and `dotnet test` before touching any file. | — | — | — |
| S-01 | [D::DD-01] Add the `ProcessablePath` value object, relocating the `.log` / `.txt` rule out of `DefaultIsProcessable`. | `LogWatcher.Core/Ingestion/ProcessablePath.cs` | DD-01, DD-04 | — |
| S-02 | [D::DD-02] Narrow `FsEvent` to the four OS fields and make it `internal`. | `LogWatcher.Core/Ingestion/FsEvent.cs` | DD-02 | — |
| S-03 | [D::DD-03, DD-06] Add `FsWorkKind`, the six payload structs, `FsWork`, and the `FsWork.From` gate. | `LogWatcher.Core/Ingestion/FsWork.cs` | DD-03, DD-06 | S-01, S-02 — the gate consumes `FsEvent` and produces `ProcessablePath` payloads. |
| S-04 | [D::DD-08] Replace `StatEventKind`'s four OS kinds with the six work kinds and swap `IncrementFsEvent` for `IncrementFsWork`. | `LogWatcher.Core/Statistics/StatEventKind.cs`, `LogWatcher.Core/Statistics/WorkerStatsBuffer.cs` | DD-08 | S-03 — the counter set mirrors `FsWorkKind`. |
| S-05 | [D::DD-08] Merge the six work counters in `GlobalSnapshot` and preserve its four existing properties. | `LogWatcher.Core/Reporting/GlobalSnapshot.cs` | DD-08 | S-04 |
| S-06 | [D::DD-02, DD-05, DD-06, DD-07] Rewrite `PublishEvent` around the gate, remove the predicate and `DefaultIsProcessable`, add the publish guard and the suppression log, and change the bus generic argument. | `LogWatcher.Core/Ingestion/FilesystemWatcherAdapter.cs` | DD-02, DD-05, DD-06, DD-07 | S-03 |
| S-07 | [D::DD-03, DD-08] Replace the coordinator's `FsEventKind` switch with the six-arm `FsWorkKind` switch and change the bus generic argument. | `LogWatcher.Core/Processing/ProcessingCoordinator.cs` | DD-03, DD-08 | S-03, S-04 — routing needs the work kinds and the counter API together. |
| S-08 | [D::DD-03] Change the remaining bus generic arguments so the solution compiles again. | `LogWatcher.Core/Reporting/Reporter.cs`, `LogWatcher.App/LogWatcherService.cs`, `LogWatcher.Benchmarks/BoundedEventBusBenchmarks.cs` | DD-03 | S-07 — this is the step at which a full build is expected to succeed. |
| S-09 | [D::DD-05] Add the Roslyn package reference, then the `default`-construction test. | `LogWatcher.Tests/LogWatcher.Tests.csproj`, `LogWatcher.Tests/Unit/Core/Ingestion/DefaultConstructionTests.cs` | DD-05, FR-12 | S-08 — the test names types that must already exist and compile. |
| S-10 | [D::DD-10] Revise `ING-003` and add `ING-004` in the register, then update Example C's affected gates. | `docs/L5__LogWatcher__Invariants.md`, `docs/invariant_definition.md` | DD-10 | S-08 — the register text describes the shipped behavior. |
| S-11 | [D::DD-01, DD-03, DD-09, DD-10] Add the Ingestion tests, carrying the `ING-003` tag to `ProcessablePathTests` and the `ING-004` tag to `FsWorkTests`, and rewrite the falsified adapter test. | `LogWatcher.Tests/Unit/Core/Ingestion/ProcessablePathTests.cs`, `LogWatcher.Tests/Unit/Core/Ingestion/FsWorkTests.cs`, `LogWatcher.Tests/Unit/Core/Ingestion/FilesystemWatcherAdapterTests.cs` | DD-01, DD-03, DD-09, DD-10 | S-10 — `InvariantCoverageTests` checks tags against the register in both directions, so the two must land together. |
| S-12 | [D::DD-03, DD-08] Add the coordination tests and convert the remaining test construction sites and counter references. | `LogWatcher.Tests/Integration/ProcessingCoordinatorTests.cs`, `LogWatcher.Tests/Integration/HostLifecycleTests.cs`, `LogWatcher.Tests/Integration/ReporterTests.cs`, `LogWatcher.Tests/Integration/WorkerStatsSwapTests.cs`, `LogWatcher.Tests/Stress/SyntheticStressTests.cs`, `LogWatcher.Tests/Unit/Core/Statistics/WorkerStatsBufferTests.cs`, `LogWatcher.Tests/Unit/Core/Reporting/GlobalSnapshotTests.cs` | DD-03, DD-08 | S-08 |
| S-13 | [D::DD-01, DD-03, DD-08] Update the remaining documentation to the shipped shapes. | `docs/system_diagram.md`, `docs/concurrency_model.md`, `docs/L5__LogWatcher__Module_Boundaries.md` | DD-01, DD-03, DD-08 | S-08 |

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
