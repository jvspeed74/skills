# Investigation: ingestion-event-filtering

## 2026-09-10 — Authoring pass

### Candidate list (written before any source was opened)

Drawn from: paths and identifiers the subject names outright (`FilesystemWatcherAdapter.PublishEvent`, `FsEvent`, `Processable`, `OldPath`, `ProcessingCoordinator.WorkerLoop`, `IncrementFsEvent`, `LogDeleteUntracked`, `_isProcessable`, `BoundedEventBus`, `ING-003`, `PROC-005`, `invariants.md`); a `grep -rln` over each of those identifiers; documentation for the domain model the subject's Fix Scope table cites; and the neighbours of everything already listed.

**Subject-named production sources**
1. `LogWatcher.Core/Ingestion/FilesystemWatcherAdapter.cs`
2. `LogWatcher.Core/Ingestion/FsEvent.cs`
3. `LogWatcher.Core/Ingestion/FsEventKind.cs`
4. `LogWatcher.Core/Processing/ProcessingCoordinator.cs`
5. `LogWatcher.Core/Backpressure/BoundedEventBus.cs`
6. `LogWatcher.Core/Statistics/WorkerStatsBuffer.cs`
7. `LogWatcher.Core/Statistics/StatEventKind.cs`
8. `LogWatcher.Core/FileManagement/FileStateRegistry.cs`
9. `LogWatcher.Core/Processing/FileProcessor.cs`

**`FsEvent` construction and consumption sites (contract blast radius)**
10. `LogWatcher.App/LogWatcherService.cs`
11. `LogWatcher.Core/Reporting/Reporter.cs`
12. `LogWatcher.Core/Coordination/WorkerStats.cs`
13. `LogWatcher.Benchmarks/BoundedEventBusBenchmarks.cs`

**Invariant register and domain model**
14. `docs/L5__LogWatcher__Invariants.md` (the register the subject calls `invariants.md`)
15. `docs/invariant_definition.md` (the `behavioral` / `contract` type taxonomy)
16. `docs/L5__LogWatcher__Module_Boundaries.md` (Domain 1 and Domain 8 scope statements)
17. `docs/concurrency_model.md`
18. `docs/system_diagram.md`

**Tests**
19. `LogWatcher.Tests/Unit/Core/Ingestion/FilesystemWatcherAdapterTests.cs`
20. `LogWatcher.Tests/Integration/ProcessingCoordinatorTests.cs`
21. `LogWatcher.Tests/InvariantAttribute.cs`
22. `LogWatcher.Tests/InvariantCoverageTests.cs`
23. `LogWatcher.Tests/Helpers/CapturingLogger.cs`
24. `LogWatcher.Tests/Integration/HostLifecycleTests.cs`
25. `LogWatcher.Tests/Integration/ReporterTests.cs`
26. `LogWatcher.Tests/Stress/SyntheticStressTests.cs`
27. `LogWatcher.Tests/Unit/Core/Statistics/WorkerStatsBufferTests.cs`
28. `LogWatcher.Tests/Unit/Core/Backpressure/BoundedEventBusTests.cs`

**Repository conventions**
29. `AGENTS.md`
30. `.github/instructions/dotnet.instructions.md`
31. `.github/copilot-instructions.md`
32. `README.md`
33. `docs/project_specification.md`
34. `docs/module_definition.md`

### Consulted

| Source | Established |
|---|---|
| `LogWatcher.Core/Ingestion/FsEvent.cs` | `FsEvent` is a positional `readonly record struct` with exactly five parameters: `(FsEventKind Kind, string Path, string? OldPath, DateTimeOffset ObservedAt, bool Processable)`. It is a value type, so an `FsEvent` local is a stack slot, not a heap allocation. Adding `OldPathProcessable` as a sixth positional parameter is a source-breaking change to every construction site; adding it as an `init`-only property with a default is source-compatible. |
| `LogWatcher.Core/Ingestion/FilesystemWatcherAdapter.cs` | `PublishEvent(kind, path, oldPath)` at lines 114–129 computes `bool processable = _isProcessable(path)` (line 118), constructs `var ev = new FsEvent(...)` (line 119), then calls `_bus.Publish(ev)` (line 120) with no gate. **The `FsEvent` is constructed before publication today**; placing the gate between lines 118 and 119 means no `FsEvent` is ever constructed for a suppressed event. The whole body sits inside a `try` / `catch (Exception)` that logs `LogPublishException`, so an added `_isProcessable(oldPath)` call is already exception-guarded. `_isProcessable` is constructor-injected (`Func<string, bool>?`), defaulting to `DefaultIsProcessable`, which accepts `.log` and `.txt` case-insensitively and returns `false` for an empty extension. `LogEventPublished` already emits a **Debug** entry on every successful publish, carrying `processable={Processable}` — so per-event Debug logging for non-processable events exists today and is removed, not merely relocated, by suppression. The watcher's `Filter` is `*.*` and `NotifyFilter` is `FileName \| LastWrite \| Size`. |
| `LogWatcher.Core/Ingestion/FsEventKind.cs` | Four variants: `Created`, `Modified`, `Deleted`, `Renamed`. No explicit numeric values declared here. |
| `LogWatcher.Core/Processing/ProcessingCoordinator.cs` | Actual line numbers differ from the subject's. `stats.Active.IncrementFsEvent(ToStatEventKind(ev.Kind))` is **line 110**, not 108, and takes a translated `StatEventKind`, not `ev.Kind` directly. The `Deleted` case is **lines 120–122** and calls `HandleDelete(ev.Path, stats.Active)` with no `Processable` check. The `Renamed` case is **lines 123–128**; its guard is `if (!string.IsNullOrEmpty(ev.OldPath))` at **line 124**. `HandleCreateOrModify` is gated on `ev.Processable` at lines 117 and 126. `HandleDelete` (lines 208–235) calls `_registry.TryGet` and, on a miss, emits `LogDeleteUntracked` at **Debug** level and returns. The routing switch is wrapped in `try` / `catch (Exception)` (lines 107–134) per PROC-009, so an exception in routing does not kill the worker. |
| `LogWatcher.Core/Backpressure/BoundedEventBus.cs` | `Publish` increments `_published` on a successful `TryWrite` and `_dropped` when the channel is full; it returns early **without counting** when `_stopped`. Exposes `PublishedCount`, `DroppedCount`, and `Depth`. FR-08 is directly assertable against the first two. |
| `LogWatcher.Core/Statistics/WorkerStatsBuffer.cs` | `IncrementFsEvent(StatEventKind kind)` is **`internal`** and switches onto four fields: `FsCreated`, `FsModified`, `FsDeleted`, `FsRenamed`. Reachable from tests only through `InternalsVisibleTo`. |
| `LogWatcher.Core/Statistics/StatEventKind.cs` | Values pinned `Created = 0` through `Renamed = 3` to stay index-compatible with `FsEventKind`. Not affected by this change. |
| `LogWatcher.Core/FileManagement/FileStateRegistry.cs` | Public surface is `GetOrCreate`, `TryGet`, `FinalizeDelete`, plus `GetCurrentEpoch` used by tests. `TryGet` on an untracked path is the miss that produces `LogDeleteUntracked`. |
| `LogWatcher.Core/AssemblyInfo.cs` | `InternalsVisibleTo("LogWatcher.Tests")` and `InternalsVisibleTo("LogWatcher.Benchmarks")` are both declared, so tests can reach `internal` members including `IncrementFsEvent` and any internal seam added to the adapter. |
| `grep -rn "new FsEvent(" --include=*.cs` | **15 construction sites**: 1 in `FilesystemWatcherAdapter.cs:119`, 1 in `LogWatcher.Benchmarks/BoundedEventBusBenchmarks.cs:28`, and 13 across `LogWatcher.Tests` — `Integration/ProcessingCoordinatorTests.cs` ×8, `Integration/HostLifecycleTests.cs` ×1, `Integration/ReporterTests.cs` ×1, `Stress/SyntheticStressTests.cs` ×1, `Unit/Core/Ingestion/FilesystemWatcherAdapterTests.cs` ×2. All 15 pass exactly five positional arguments. This is the measured cost of the positional option: 15 sites versus 1. |
| `LogWatcher.App/LogWatcherService.cs` | References `FsEvent` only as the type argument `BoundedEventBus<FsEvent>` (lines 34, 45). Constructs no `FsEvent`. Unaffected by either shape option. |
| `LogWatcher.Core/Reporting/Reporter.cs` | References `FsEvent` only as `BoundedEventBus<FsEvent>` (lines 19, 49). Constructs no `FsEvent`. Unaffected. |
| `LogWatcher.Core/Coordination/WorkerStats.cs` | Contains no `FsEvent` reference. The earlier grep hit was on the `IncrementFsEvent` identifier elsewhere. Unaffected. |
| `LogWatcher.Benchmarks/BoundedEventBusBenchmarks.cs` | Constructs one `FsEvent` in `[GlobalSetup]` (lines 28–33) with five positional arguments. Breaks under the positional option; unaffected under the `init`-property option. |
| `docs/L5__LogWatcher__Invariants.md` | **The register the subject calls `invariants.md`; no file named `invariants.md` exists in this repository.** Format is a per-module Markdown table with columns `ID / Type / Modules / Description`. The Ingestion block is lines 162–164 and holds exactly `ING-001`, `ING-002`, `ING-003`, so the next free Ingestion ID is `ING-004`. `ING-003` reads verbatim: "Only `.log` and `.txt` files are marked processable. Other extensions are published as non-processable events." (`behavioral`, Modules `ING`). `PROC-005` is line 111 (`behavioral`, Modules `PROC, BP`). Cross-module rows already exist and list both modules — `BP-006` is `contract`, Modules `BP, ING` — so a new contract row would carry Modules `ING, PROC`. |
| `docs/invariant_definition.md` | Defines `contract` as "A shared assumption at a module boundary is broken — one side expects a condition the other does not satisfy", and `behavioral` as "Observable behavior degrades while the system remains operational". Classification priority is `strict` > `contract` > `resource` > `behavioral`. **Lines 370–406 are a worked example, "Example C — Valid `behavioral` invariant", that quotes `ING-003`'s current Description verbatim and walks all nine classification gates against it.** Editing `ING-003` in the register leaves this example quoting text that no longer exists. Its Gate 7 reasoning — "Processing Coordination does not declare a contract based on the specific set of extensions — it trusts the `Processable` field" — remains true of the marking clause but not of the new `OldPathProcessable` boundary agreement. |
| `docs/L5__LogWatcher__Module_Boundaries.md` | Module 1 (Ingestion, `LogWatcher.Core.Ingestion`) lists "Extension filtering" and "Event contracts" as **In Scope** and claims Data Ownership of `FsEvent`, describing its schema as "(path fields, processable flag, observed timestamp)". Its Contracts block (lines 58–63) names `bus.Publish(FsEvent item) → bool` as its only outbound behavioral contract and `FsEvent` as outbound data to Processing Coordination. Module 8 (Processing Coordination) shares the namespace `LogWatcher.Core.Processing` with Module 7 (File Processing), lists "Event routing (created/modified/deleted/renamed)" as In Scope and "Statistics" as **Out of Scope**, and its Data-inbound entry for `FsEvent` reads "dequeued event used to determine routing action". Neither module's contract block enumerates `FsEvent`'s individual fields, so adding a field contradicts no field list there. |
| `docs/system_diagram.md` | Line 156 renders `FsEvent` as a Mermaid node **enumerating all five fields explicitly**: `Kind`, `Path`, `OldPath`, `ObservedAt`, `Processable`. Adding `OldPathProcessable` makes this node an incomplete field list. |
| `docs/concurrency_model.md` | Line 142 states the rename transition as `RenamePath --> AckSwap2 : HandleDelete(old) + HandleCreateOrModify(new)` — **unconditional on both halves**, which contradicts FR-09 once `HandleDelete` is gated on `OldPathProcessable`. Line 120 already qualifies the create/modify transition as `Created / Modified (Processable=true)`. |
| `LogWatcher.Tests/Unit/Core/Ingestion/FilesystemWatcherAdapterTests.cs` | Three tests. **`Start_WhenNonProcessableFileCreated_PublishesEventWithProcessableFalse` (lines 48–76) is tagged `[Invariant("ING-003")]`, asserts `bus.PublishedCount > 0` after creating `x.dat`, then dequeues and asserts `Processable == false`. It asserts exactly the behavior this plan removes.** It is the only test tagged `ING-003` in the repository. The file's style drives the real `FileSystemWatcher` against a real temp directory and polls `bus.PublishedCount` for up to 2s; there is no synchronous seam onto `PublishEvent`, which is `private`. Asserting non-publication in this style means waiting out a timeout rather than observing a definite event. |
| `LogWatcher.Tests/Integration/ProcessingCoordinatorTests.cs` | Coordinator tests live under `Integration/`, not `Unit/`; **no `Unit/Core/Processing/` directory appears in the repository enumeration.** They construct a `BoundedEventBus`, a `FileStateRegistry`, a fake `IFileProcessor` and a `WorkerStats[]`, publish `FsEvent`s directly onto the bus, run real worker threads, and synchronise with `Thread.Sleep`. In-file fakes: `FakeProcessor` (records `Calls`), `GateCheckingProcessor`, `ThrowThenRecordProcessor`. Existing `[Invariant]` tags cover PROC-001 through PROC-007 and PROC-009. |
| `LogWatcher.Tests/InvariantCoverageTests.cs` | A **hard two-way CI gate**. `DefinedInvariant_HasAtLeastOneTaggedTest` fails for any ID present in `L5__LogWatcher__Invariants.md` with no `[Invariant("ID")]`-tagged test; `TaggedInvariant_ExistsInMarkdown` fails for the reverse. IDs are harvested by a regex matching a hyphenated uppercase prefix followed by three digits, applied to the **entire** document text — so an ID mentioned anywhere in the register, prose included, counts as defined. Any new invariant this plan adds must ship with a tagged test in the same change. |
| `LogWatcher.Tests/Helpers/CapturingLogger.cs` | `internal sealed class CapturingLogger<T> : ILogger<T>` records `(LogLevel Level, string Message)` with the message already formatted, exposed via the public `Entries` list. `IsEnabled` returns `true` unconditionally, so **Debug-level entries are captured**. Its `HasWarning` helper filters to `>= Warning` only, so an FR-11 assertion on a Debug entry must inspect `Entries` directly. |
| `LogWatcher.Tests/LogWatcher.Tests.csproj` | Embeds `..\docs\L5__LogWatcher__Invariants.md` as an `EmbeddedResource`, which is what `InvariantCoverageTests` reads. `TreatWarningsAsErrors` is `true`. Declared folders: `Unit\`, `Integration\`, `Stress\`. |
| `LogWatcher.Core/LogWatcher.Core.csproj` | `TargetFramework net10.0`, `Nullable enable`, `TreatWarningsAsErrors true`, `AnalysisMode Recommended`. **No `GenerateDocumentationFile`**, so a missing XML `<summary>` on a new public member is not a build error — though every existing public member in `FsEvent` and the adapter carries one. |
| `AGENTS.md` | `docs/` is the source of truth and wins over agent assumptions. Requires the smallest change that satisfies the task, tests added or updated when behavior changes, and docs updated when contracts change. States: "Do not break published data/CLI contracts without a compatibility plan (migration or backward compatibility)" — directly relevant to the `FsEvent` shape fork. |

### Not opened

| Not opened | Why |
|---|---|
| `LogWatcher.Core/Processing/FileProcessor.cs` | `HandleCreateOrModify` reaches it only through the unchanged `_processor.ProcessOnce` call; the plan alters which events reach that call, never the call's shape. The `IFileProcessor` signature was read in full from the test fakes. |
| `LogWatcher.Tests/Integration/HostLifecycleTests.cs`, `Integration/ReporterTests.cs`, `Stress/SyntheticStressTests.cs` | Enumerated only as `new FsEvent(` construction sites; their exact five-argument call shape was captured by the grep. Their assertions were not read, so **whether any asserts on a published non-processable event is unestablished** — named again below. |
| `LogWatcher.Tests/Unit/Core/Backpressure/BoundedEventBusTests.cs`, `Unit/Core/Statistics/WorkerStatsBufferTests.cs` | Bus and `IncrementFsEvent` semantics were established from the production sources directly; neither is modified by this plan. |
| `LogWatcher.Tests/InvariantAttribute.cs` | Its usage contract was established from `InvariantCoverageTests.cs`, which reflects over it, and from the tag sites already read. |
| `README.md`, `docs/project_specification.md`, `docs/module_definition.md`, `.github/copilot-instructions.md`, `.github/instructions/dotnet.instructions.md` | `README.md` and `.github/copilot-instructions.md` mention `FsEvent` but were not opened; whether either enumerates the field list the way `system_diagram.md:156` does is unestablished. The remaining three matched no changed identifier. |
| `LogWatcher.Benchmarks/*` other than `BoundedEventBusBenchmarks.cs`, `LogWatcher.Seeder/*`, the Tailing / Scanning / Parsing sources | Matched none of the subject's identifiers. |
| .NET `FileSystemWatcher` documentation on rename delivery | The plan gates events the OS already reports as `Renamed`, and NG-05 excludes reconstructing renames the OS splits into `Deleted` + `Created`. No behavioral claim here rests on OS delivery semantics beyond what PROC-005 already concedes. |

### Sufficiency

The read set supports, from direct observation of the sources named: the exact publish path and gate insertion point in `PublishEvent`, and the fact that an `FsEvent` is constructed before `Publish` today; the exact routing lines, guards and log levels in `WorkerLoop` and `HandleDelete`, with corrected line numbers; the bus counter semantics FR-08 is asserted against; the two shape options for `FsEvent` and the measured 15-versus-1 construction-site cost between them; the invariant register's real filename, table format and next free Ingestion ID; the hard two-way coverage gate that forces a tagged test for any new invariant; the single existing `ING-003` test that this change falsifies; and four documentation sites that go stale — `invariant_definition.md` Example C, `system_diagram.md:156`, `concurrency_model.md:142`, and Module 8's `FsEvent` Data-inbound entry.

It does not support the following, and no conclusion should be drawn past them:

- ~~Three `FsEvent`-constructing test files were never opened past their construction lines.~~ **Closed in the same pass.** `HostLifecycleTests.cs:90` does publish a non-processable `Created` event, but its only downstream assertion is `Assert.True(workerStats[0].Active.FsCreated >= 0)` at line 100 — a tautology on a `long` counter, which cannot fail under DD-03. `ReporterTests.cs` starts no coordinator at all; its five published events exist to bump the bus published counter, and its statistics assertions come from direct `IncrementFsEvent` calls on the worker buffers. `SyntheticStressTests.cs` publishes only processable `/tmp/fake/{id}.log` `Modified` events and asserts `DroppedCount > 0` and `totalProcessed > 0`, none of which the gate reaches. **All three need a construction-site edit only; none has an assertion this plan breaks.**
- ~~`README.md` and `.github/copilot-instructions.md` were not opened.~~ **Closed in the same pass.** `README.md:52` renders `FsEvent` as a Mermaid node labelled with its event *kinds* (`Created|Modified|Deleted|Renamed`), not its fields, and line 102 labels an edge with the type name. `.github/copilot-instructions.md` names `FsEvent` only as a type belonging to Module 1 (line 96) and as the thing workers dequeue (line 132). **Neither enumerates fields, so neither goes stale.** `docs/system_diagram.md:156` remains the only field-list site in the repository.
- **No build or test run was performed.** Every claim about what compiles or which test fails is read from source, not observed from a compiler or a test runner. In particular, "the existing `ING-003` test will fail" is an inference from its assertions against the planned change, not a recorded failure.
- **The claim that no `Unit/Core/Processing/` directory exists** rests on the `find` enumeration at the head of this pass, which filtered to `*.cs` and `*.md`; an empty directory would not have appeared in it.
- The `contract`-versus-`behavioral` classification of the proposed new invariant rests on the type definitions in `invariant_definition.md` as written. The nine-gate gauntlet that document specifies was **not executed** against the proposed invariant text; only the type table was consulted.

## 2026-09-10 — Second pass: value-object redesign

The design moved from "add a bool field to FsEvent" to a value-object redesign. Sources opened in this pass, beyond those above:

| Source | Established |
|---|---|
| `grep -rn "new FilesystemWatcherAdapter"` | **Five construction sites, none of which passes `isProcessable`**: `LogWatcher.App/LogWatcherService.cs:57` (passes only path, bus and logger), `HostLifecycleTests.cs:23` and `:82`, `FilesystemWatcherAdapterTests.cs:33` and `:53`. The predicate parameter is a seam no caller uses. |
| `LogWatcher.App/LogWatcherOptions.cs`, `LogWatcher.App/CommandConfiguration.cs` | **No extension or filter configuration surface exists.** The only grep hit is `logging.AddFilter("LogWatcher", options.LogLevel)` at `CommandConfiguration.cs:172`, which is log-level filtering, unrelated. Removing the predicate parameter therefore removes no configurability. |
| `grep -rn "FsCreated|FsModified|FsDeleted|FsRenamed|StatEventKind"` | The per-kind counters are read in nine files: `StatEventKind.cs`, `WorkerStatsBuffer.cs`, `ProcessingCoordinator.cs`, `GlobalSnapshot.cs`, `LogWatcher.App/ConsoleSnapshotConsumer.cs`, and the tests `WorkerStatsBufferTests.cs`, `GlobalSnapshotTests.cs`, `WorkerStatsSwapTests.cs`, `ReporterTests.cs`, `HostLifecycleTests.cs`. `ConsoleSnapshotConsumer.cs` renders `FsRenamed`, making the console report a consumer of the counter set. |
| `LogWatcher.Tests/Integration/HostLifecycleTests.cs:80-100` | Publishes a **non-processable** `Created` event at line 90, but its only downstream assertion is `Assert.True(workerStats[0].Active.FsCreated >= 0)` at line 100 — a tautology on a `long`. Nothing here breaks. |
| `LogWatcher.Tests/Integration/ReporterTests.cs:10-45` | Starts no coordinator. Its five published events exist to bump the bus published counter; its statistics assertions come from direct `IncrementFsEvent` calls on the worker buffers. Nothing here breaks behaviorally. |
| `LogWatcher.Tests/Stress/SyntheticStressTests.cs:45-75` | Publishes only processable `/tmp/fake/{id}.log` `Modified` events; asserts `DroppedCount > 0` and `totalProcessed > 0`. The gate does not reach either assertion. |
| `README.md`, `.github/copilot-instructions.md` | `README.md:52` renders `FsEvent` labelled with its event kinds, not its fields; `:102` labels an edge with the type name. `copilot-instructions.md:96` and `:132` name the type only. **Neither enumerates fields, so neither goes stale.** `docs/system_diagram.md:156` is the only field-list site. |

### Sufficiency, second pass

Additionally supported: that removing the adapter predicate costs no configurability, since no caller supplies one and no option exposes one; the full nine-file reach of the per-kind counters, including the console consumer; and that the three unopened test files from the first pass carry no assertion this plan breaks.

Still not supported, carried forward:

- **No build or test run has been performed at any point.** Every compile-or-fail claim in the plan is read from source. This is recorded as RK-04.
- **`ConsoleSnapshotConsumer.cs` was never opened.** Its use of `FsRenamed` is known from grep alone; the exact rendering, and whether it reads the other three counters, is unestablished. FR-18 asserts the four-line shape survives, which rests on `GlobalSnapshot` keeping its four properties rather than on having read the consumer.
- **`GlobalSnapshot.cs` was never opened.** Its four `Fs*` properties are known from grep counts only; whether they are fields, computed properties, or set during a merge step is unestablished, and DD-08 assumes a merge site exists where the three rename counters can be summed.
- **No Roslyn-based test exists anywhere in this repository**, so FR-12 has no in-repo precedent to follow. RK-01 carries this.
