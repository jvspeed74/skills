---
template_version: "0.1.0"
---

# Implementation Plan: Collection Pagination
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

  ID STABILITY:   Every ID (PS-XX, INV-XX, FR-XX, NFR-XX, NG-XX, DD-XX, FM-XX,
                  RK-XX, OQ-XX, S-XX) is permanent once assigned. Never renumber an
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

[U] Four of the five collection endpoints return their entire table in one response. `config/routes.php` wires `/teams`, `/events`, `/drivers` and `/cars` to `AbstractController::getAll`, which calls an unbounded repository read, so response size and query cost grow linearly with table size and neither the client nor the server can bound them. `/tracks` is the exception: it has been paged since before this plan, through `getAllWithParams`, and the paging contract it uses is already declared on `RepositoryInterface` for every repository. The work is therefore generalising a pattern this codebase already contains, not introducing one — and the four unpaged endpoints are not merely slow but actively depended upon: `public/driversPage.php` fetches the whole driver collection and pages it in the browser at five rows per page.

[U] The one paged endpoint undercuts itself. `TrackController:58` computes its total as `$this->repository->getAll()->count()`, loading every row to count them, on the single endpoint whose purpose is to avoid loading every row — while the `LengthAwarePaginator` it obtained two lines earlier already carries that total.

[U] The published contract records the asymmetry rather than resolving it. `openapi/paths/tracks.yaml` is the only path file documenting `page` and `limit`, and CI's `redocly lint` validates that specification's syntax without ever comparing it against the implementation, so nothing detects a divergence between what the API does and what its published documentation says it does.

---

## Postulates
<!-- The unyielding rules the thing being modified was built inside — the
     external assumptions it has no authority over. A Postulate is
     inward-facing: what the thing conforms to. An Invariant below is the
     outward half: what a boundary guarantees to whatever depends on it.
     Both are non-negotiable; they face opposite directions.

     Four properties. A candidate failing any one is not a Postulate:
       No authority — the thing cannot negotiate, alter, or debate it. It
                      can only conform.
       Exclusive    — every aspect of the thing's shape traces to it. A
                      proposed change that cannot be traced back either
                      belongs elsewhere, or shows the Postulate was stated
                      too loosely.
       Sufficient   — it alone explains the shape. No additional force is
                      needed.
       External     — it exists independently of the thing, which did not
                      author it. It may originate outside the system
                      entirely (an OS contract, a format standard, a
                      protocol) or above it (an architectural policy, a
                      stated philosophy).

     Four negative tests. None of these is a Postulate:
       A stakeholder or team decision — stakeholders are proxies. The
         Postulate is the assumption behind the decision.
       A technology — a choice made inside a Postulate's space. The
         Postulate is the rule that made the choice necessary.
       A list of change scenarios — those are the Postulate's dimensions,
         the ways it could shift. The Postulate is the thing being redrawn.
       Anything internal to the thing — it cannot author its own Postulate.

     A row belongs here only if cited by at least one Design Decision or
     Failure Mode below, on the same footing as an Invariant.

     Provenance: the marker prefixes `Postulate`. `Basis` names what
     established it — the source, which mechanisms were run against it, and
     which of those were independent of the source's own stated rationale.
     `Cost` states what violating it would cost and how that was
     established; "unestablished" is a permitted value and is not the same
     as none. `Detected` states what, if anything, would catch a violation.
     A Postulate whose violation is costly and would go undetected is the
     most load-bearing kind — nothing else will ever catch it. -->

| # | Postulate | Basis | Cost | Detected |
|---|---|---|---|---|
| PS-01 | [V] The published OpenAPI specification is the contract this API answers to. What an endpoint accepts and returns is settled by `openapi/`, not by the implementation; the code conforms and cannot renegotiate. | All four mechanisms run. **Stated rationale:** no prose states it; the statement is the enforcement, `redocly lint openapi/openapi.yaml` on every push. **Consumer chain:** spec → the `gh-pages` publish workflow → external clients and `.postman/`. **Regularity:** 5 of 5 collection endpoints carry a path file; 1 of 5 documents paging, matching the implementation exactly. **Reasons to change:** client needs, response size, new fields — all trace to what an external client may rely on. **Independent of the stated rationale:** consumer chain and regularity, neither of which reads the CI config. Negative tests pass: not a stakeholder decision, not a technology (swagger-php generates it; the contract is not the generator), not a change-scenario list, not internal — it is published and consumed outside this repository. | A client written against the published documentation breaks, at their end rather than ours. Established by the consumer chain, corroborated by the regularity count. | **Nothing.** `redocly lint` checks the specification is valid, never that it is true. An endpoint that starts paging without a spec change passes CI unchanged. |
| PS-02 | [V] PER-CS 2.0 and PHPStan level 5 govern every file under `src/`, `config/` and `public/`. | All four mechanisms run. **Stated rationale:** declared in `.php-cs-fixer.dist.php` and `phpstan.neon`; named at `README.md:98`. **Consumer chain:** fixer and analyzer consume the source, CI consumes their exit codes, a non-zero code blocks the merge — short, and terminating in a hard stop. **Regularity:** `phpstan.neon` covers 3 of 4 top-level PHP directories, excluding `tests/**` explicitly. **Reasons to change:** a PHP version bump or a level bump, both tracing to the declared quality bar. **Independent of the stated rationale:** consumer chain and regularity, but only weakly — both observe the same CI configuration the rationale is declared in. Negative tests pass, with the second doing real work: PHPStan and PHP-CS-Fixer are technologies, but PER-CS 2.0 is a standard published by PHP-FIG that the code conforms to, and the tools are its enforcement rather than the rule itself. | The build fails and the change cannot merge. Established directly from the CI configuration. | **Loudly, on every push,** by two separate CI steps. This rule defends itself. |
| PS-03 | [V] HTTP concerns stay in controllers; query construction stays in repositories. Each layer is replaceable without the other. | All four mechanisms run. **Stated rationale: none exists** — `README.md`, `composer.json`, `phpstan.neon`, `.php-cs-fixer.dist.php` and the repository root were searched, and the project carries no `AGENTS.md`, no `CLAUDE.md` and no architecture document. **Consumer chain:** repositories are consumed by controllers and, separately, by unit tests that construct them with no `Request` — the split is what makes `AbstractRepositoryTest` and `TeamRepositoryTest` writable at all. Past one hop, the `Contracts/` interfaces stop describing what implementers do and the abstract bases stop being substitutable, which is their only reason to exist. **Regularity: 13 of 13.** All 7 repositories take a `Model` and return `Model`, `Collection` or `LengthAwarePaginator`, touching no `Request` or `Response`; all 6 controllers take `Request`/`Response` and issue no query. **Reasons to change:** a new transport, a different persistence layer, testability — all tracing to one assumption. **Independent of the stated rationale: all three, necessarily**, there being no stated rationale to depend on. This is the most strongly corroborated of the three rules and the only one nobody wrote down. Negative tests: the fourth required a judgment. An architectural policy authored inside this system is internal to the system, but sits above the collection-read path this plan modifies, which is the case a Postulate is permitted to originate from. | The two layers stop being independently testable and independently replaceable, and the existing repository unit tests become unwritable. Established by consumer chain and regularity; **not by any statement**, since none exists. | **Nothing.** PHPStan level 5 checks types, not layering, and `tests/**` is excluded from analysis. No architecture test exists. A query written into a controller ships silently. |

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
| INV-01 | [V] `RepositoryInterface` declares `getAllWithParams(int $page, int $limit, string $sortBy, string $order): LengthAwarePaginator`, and all seven repositories satisfy it through `AbstractRepository`. Paging and sorting are one signature at this boundary; they cannot be taken separately without changing the interface. | `src/Contracts/RepositoryInterface.php:42` and `src/Contracts/AbstractRepository.php:59`, read directly. |
| INV-02 | [V] `/tracks` accepts `page`, `limit`, `sort_by` and `order`, defaulting to 1, 10, `id` and `asc`, rejecting `page < 1` and any `limit` outside 1–100 with `400`. These names and bounds are published. | `src/Controllers/TrackController.php:25–55`; independently documented at `openapi/paths/tracks.yaml:7–17`, which states "default is 1" and "default is 10, max is 100". Two sources agreeing. |
| INV-03 | [V] A paged collection returns its totals as the response headers `X-Total-Count`, `X-Total-Pages`, `X-Current-Page` and `X-Items-Per-Page`, and its body as a bare array with no envelope. | `src/Controllers/TrackController.php:63–70`. Stands on one source — the only paged endpoint in the codebase. |
| INV-04 | [V] `AbstractController::getAll(Response $response)` takes no `Request`. Any paging placed on the inherited path requires a signature change that reaches every controller extending it and every route naming it. | `src/Contracts/AbstractController.php:19`; the five route bindings at `config/routes.php:85, 94, 112, 122`. |
| INV-05 | [V] A merge is blocked by PHPStan level 5, `php-cs-fixer check` against PER-CS 2.0, `redocly lint` over the OpenAPI specification, and PHPUnit. | `.github/workflows/continuous-integration.yml`, read directly. |

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
| FR-01 | [U] WHEN a collection endpoint receives a request carrying no paging parameters, the API shall return the first page at the default page size. | `GET /drivers` with no query string; observe a row count equal to the default page size, not the table count. |
| FR-02 | [U] WHEN a collection endpoint receives a valid page number, the API shall return that page. | `GET /drivers?page=2` against a seeded table; observe the rows following the first page, in the same order. |
| FR-03 | [U] IF a paging parameter is non-numeric, negative, or zero, THEN the API shall return `400` and shall not query the collection. | Request `page=abc`, `page=-1` and `page=0`; observe `400` for each and no query issued, asserted against a query log or a repository spy. |
| FR-04 | [U] IF a requested page size exceeds the maximum, THEN the API shall return `400`. | Request one row above the maximum; observe `400`. |
| FR-05 | [U] The API shall report, with every paged collection response, the total row count and the page returned. | `GET /drivers?page=1`; observe both values present and the total matching a direct `COUNT` of the table. |
| FR-06 | [U] WHEN a requested page lies beyond the last page, the API shall return an empty collection with `200`. | Request a page past the end; observe `200`, an empty collection and the total still reported. |
| FR-07 | [U] Every collection endpoint shall accept the same paging parameter names. | Issue the same paging query string against all five collection endpoints; observe identical handling. |
| FR-08 | [U] WHERE a repository exposes a collection read, it shall receive the paging bounds and apply them within the query rather than trimming a full result set afterwards. | Repository test asserting the emitted SQL carries a limit clause; a spy asserting the driver returns at most the page size rows. |

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
| NFR-01 | [U] WHILE serving any collection endpoint, the API shall return no more rows in a single response than the maximum page size. | [U] 100 rows | Request a page size of 101 against every collection endpoint; observe `400` and no response exceeding 100 rows. The number is the reviewer's, not measured. |

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
| NG-01 | [U] Paging the single-resource endpoints | A `show` route returns one row by identifier. Paging has no meaning there, and naming the exclusion keeps a later reader from treating the untouched routes as an oversight. |
| NG-02 | [U] Filtering and field selection. **Sorting is not excluded** — narrowed during authoring, after the contradiction check found the original exclusion unsatisfiable. | Filtering and field selection remain adjacent capabilities a reader may expect alongside paging, and each is a separate contract with its own validation surface. Sorting was excluded with them until INV-01 established that `getAllWithParams(page, limit, sortBy, order)` is a single signature every repository already satisfies: routing the four unpaged endpoints through the established contract adds sorting to all four whether or not this plan wants it. The exclusion was narrowed rather than the contract avoided, because avoiding it means a second collection-read method on an interface that already has one — PS-01's cost, paid to keep a Non-goal that was written before the interface was read. Each endpoint therefore ships the per-entity sort-field allowlist the established pattern requires. |
| NG-03 | [U] Changing the authentication or middleware chain | Paging is a query concern. The four authentication middlewares and their ordering are untouched, and no paging parameter affects authorization. |
| NG-04 | [U] The Postman collection under `.postman/`. **The OpenAPI path files are not excluded** — narrowed during authoring, after the contradiction check found the original exclusion unsatisfiable against PS-01. | The original exclusion covered both, on the reasoning that backfilling needs shipped parameter names this plan decides but does not publish. That reasoning dissolved once DD-01 and DD-02 fixed the names and the response shape. PS-01 then made the specification half non-negotiable: four endpoints changing behaviour while `cars.yaml`, `drivers.yaml`, `events.yaml` and `teams.yaml` continue to document unbounded collections puts the API in violation of its own published contract, and PS-01's `Detected` column reads "nothing", so the divergence would ship unnoticed. The four path files are therefore in scope. `.postman/` remains excluded: it is a convenience export rather than the published contract, nothing in CI validates it, and no external consumer is entitled to rely on it. |

---

## Design Decisions
<!-- One row per non-obvious choice — if a reviewer could reasonably ask "why
     not X instead?", it belongs here. Obvious choices given the constraints
     don't need a row.

     Satisfies: the Requirement, Non-goal, Postulate or Invariant # (FR-XX,
     NFR-XX, NG-XX, PS-XX or INV-XX) that justifies the choice. A decision
     satisfying none of these is either unnecessary or the row it needs is
     missing above — fix whichever is true before proceeding.

     Agent Position: which option the agent recommended and the basis for
     it, with that basis marked established or novel. A novel basis is
     legitimate — the right answer is sometimes one nothing precedents —
     and saying so keeps it from reading as precedent. Use — where the
     agent held no view. This column exists so the finished plan can
     distinguish a resolution the reviewer originated from one they
     ratified; without it both look identical, and a later reader cannot
     see where they were nudged.

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

| # | Decision Point | Resolution | Satisfies | Agent Position | Alternatives Rejected |
|---|---|---|---|---|---|
| DD-01 | Where does paging live for the four unpaged endpoints? | [U] A protected helper on `AbstractController` performs the parameter parsing, bounds checking and header writing once; each controller calls it supplying its own sort-field allowlist. The four unpaged controllers gain a `getAllWithParams` method that delegates to the helper, and `TrackController`'s existing implementation is refactored onto it. | FR-01, FR-02, FR-03, FR-04, FR-06, FR-07, NFR-01, INV-02, INV-04, PS-03 | Recommended this, on an **established** basis: INV-02's allowlist is per-entity so no base-class method can own it, while the parsing and bounds are byte-identical across all five, and PS-03 keeps both halves in the controller layer where HTTP concerns belong. | Each controller overriding independently, as `TrackController` does today — the established pattern followed literally, rejected because it produces five near-copies of the same forty lines of validation and FR-07's identical-parameter-names guarantee would then rest on five separate implementations staying in step. Moving paging into `AbstractController::getAll` and changing its signature to accept a `Request` — removes duplication entirely, rejected because INV-04 makes that a breaking signature change reaching every controller and all five route bindings, and it would page the single-resource path's siblings by inheritance rather than by choice. |
| DD-02 | Are totals returned as headers or as a body envelope? | [U] Headers, exactly as established: `X-Total-Count`, `X-Total-Pages`, `X-Current-Page`, `X-Items-Per-Page`, with the body remaining a bare array. | FR-05, INV-03, PS-01 | Recommended this, on an **established** basis: PS-01 makes the published specification the contract, and `openapi/paths/tracks.yaml` already documents this shape for `/tracks`. An envelope would make two collection response shapes coexist in one API. | A body envelope wrapping `data` and `meta` — the more common REST convention, self-describing, and survives proxies that strip unknown headers; rejected because adopting it means either changing `/tracks` and breaking a published contract, or shipping two different collection shapes in the same API. INV-03 stands on a single source, so this rejection is weaker than it reads: `TrackController` is the only paged endpoint in the codebase and nothing corroborates the header choice as deliberate. |
| DD-03 | What becomes of `TrackController`'s full-table count? | [U] Replaced by `$tracks->total()` from the `LengthAwarePaginator` already in hand. The header values are unchanged; only their source changes. | FR-05, INV-03 | Recommended this, on an **established** basis: `AbstractRepository::getAllWithParams` returns a `LengthAwarePaginator`, whose contract carries the total, so the second query is redundant rather than merely expensive. | Leaving it as it stands — no behavioural change and no risk, rejected because generalising the pattern to four more endpoints would replicate a full-table scan onto every paged route, turning one endpoint's defect into five. Computing the total with a dedicated `COUNT` query — correct and cheap, rejected as unnecessary when the paginator already holds the number. |
| DD-04 | What happens to `getAll()` once no route reaches it? | [U] It stays on `RepositoryInterface` and `AbstractRepository`, routed nowhere. | FR-08, INV-01, PS-01, NG-04 | — | Removing it from the interface and the abstract — the tidier end state, rejected because `AbstractRepositoryTest` covers it, seven repositories implement it, and PS-01 requires no such change: nothing published depends on its removal. Deprecating it with an annotation — rejected as a claim about a future this plan does not schedule. |
| DD-05 | Does the default page size apply when a request supplies no paging parameters? | [U] Yes. A request with no parameters receives page 1 at 10 rows, matching `/tracks`. | FR-01, INV-02, PS-01 | Recommended this, on an **established** basis: INV-02 fixes the defaults at 1 and 10 for the one endpoint that pages, and an unbounded default is precisely the condition this plan exists to remove — leaving it in place would fix the endpoints only for clients who already knew to ask. | Paging only when parameters are supplied, leaving the bare path unbounded — fully backwards compatible and breaks no existing consumer, rejected because it retains the defect for every caller who does not opt in, including the four SPA pages that are the API's own largest consumers. The cost of rejecting it is real and is recorded as FM-01: `public/driversPage.php` and its three siblings fetch whole collections today and will silently receive ten rows. |

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
| `src/Contracts/AbstractController.php` | Modify | [D::DD-01] Add a protected helper performing the parameter parse, the `page`/`limit` bounds check, the `order` allowlist and the four `X-*` header writes, taking the caller's sort-field allowlist as an argument. `getAll(Response)` is left untouched, so INV-04's signature does not move. | DD-01, FR-03, FR-04, FR-05, FR-07, INV-04 |
| `src/Controllers/TrackController.php` | Modify | [D::DD-01, DD-03] Refactor `getAllWithParams` onto the helper, passing the existing six-field allowlist. Replace `$this->repository->getAll()->count()` at line 58 with `$tracks->total()`. Behaviour and header values unchanged. | DD-01, DD-03, FR-05, INV-02, INV-03 |
| `src/Controllers/CarController.php`, `DriverController.php`, `EventController.php`, `TeamController.php` | Modify | [D::DD-01, DD-05] Each gains a `getAllWithParams(Request, Response)` delegating to the helper with its own sort-field allowlist, drawn from that entity's columns. `DriverController::search` is untouched. | DD-01, DD-05, FR-01, FR-02, FR-06, FR-07, NG-02 |
| `config/routes.php` | Modify | [D::DD-05] Rebind the four collection routes at lines 85, 94, 112 and 122 from `:getAll` to `:getAllWithParams`. The `/tracks` binding at line 103 already points there. | DD-05, FR-01, INV-04 |
| `public/driversPage.php`, `carsPage.php`, `teamsPage.php`, `eventsPage.php` | Modify | [D::DD-05] Each fetches a whole collection and pages it in the browser. Under DD-05 they receive ten rows and their client-side paging silently truncates. Each is changed to request pages from the API and to read the `X-Total-*` headers rather than counting a local array. Only `driversPage.php` was read; the other three are named from the shared navigation and their handling is unverified. | DD-05, FR-01, FR-05, INV-03 |
| `openapi/paths/cars.yaml`, `drivers.yaml`, `events.yaml`, `teams.yaml` | Modify | [D::DD-05] Add the `page`, `limit`, `sort_by` and `order` query parameters and the four response headers, matching `tracks.yaml:7–17` exactly. Required by PS-01 once behaviour changes; NG-04 was narrowed to admit these four files. | DD-05, PS-01, INV-02, FR-07 |
| `tests/Unit/Controllers/TrackControllerTest.php` | Modify | [V] 218 lines, and it is the specification of the established pattern: a `getAllWithParams` describe block asserting the four parameter names, the `X-Total-Count` and `X-Total-Pages` headers, and `400` for page `0`, limit `101` and an invalid sort field. Updated only where the refactor onto the helper moves a call site. DD-03 passes it untouched — both header assertions use `Mockery::type('string')`, so changing the total's source from a full-table count to `$tracks->total()` is invisible to it. | DD-01, DD-03, INV-02, INV-03 |
| `tests/Unit/Controllers/CarControllerTest.php`, `TeamControllerTest.php` | Modify | [D::DD-05] Existing collection assertions expect unbounded results and will fail once the routes page. Updated to assert the first page, the headers, and the `400` cases of FR-03 and FR-04. | DD-05, FR-01, FR-03, FR-04, NFR-01 |
| `tests/Unit/Controllers/DriverControllerTest.php`, `EventControllerTest.php` | Create | [D::DD-01] No controller test exists for either. Added to cover FR-01 through FR-07 on the two endpoints that would otherwise ship paged with no test at all. | DD-01, FR-01, FR-02, FR-06, FR-07 |

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
     above must prevent this mode — cite it (FR-#, NFR-#, DD-#, PS-#, or INV-#) in
     Behavior. If Yes, state why the outcome is tolerable inline; an
     unexplained "Yes" is not a verdict.

     Provenance: two markers. One prefixes `Behavior`, recording whether the
     behavior was established from a named source or follows from rows
     above. One prefixes `Accepted?`, which is always the reviewer's —
     accepting a failure mode is accepting risk on their behalf, so the
     verdict is theirs every time, including when it looks obvious. -->

| # | Trigger | Behavior | Severity | Accepted? |
|---|---|---|---|---|
| FM-01 | The four collection routes begin paging by default, and a SPA page still fetches the collection expecting all of it. | [D::DD-05] `public/driversPage.php:19` fetches `/api/drivers` and pages the result in the browser at five rows per page. Under DD-05 it receives ten rows, renders two pages of working-looking controls, and shows ten drivers as though they were every driver. Nothing errors and nothing logs. Prevented by DD-05 via the Files Touched rows that change all four SPA pages to request pages and read the `X-Total-*` headers. | Critical | [U] No — prevented by DD-05 via the four `public/*Page.php` rows. |
| FM-02 | An OpenAPI path file is updated to describe paging, and its stated default or bound does not match what the controller enforces. | [D::DD-05, PS-01] The four path files are written by hand against `tracks.yaml`. PS-01's `Detected` column reads nothing: `redocly lint` validates that the specification is well-formed, never that it is true of the implementation, so a documented default of 20 against an enforced default of 10 passes CI and ships — INV-05 lists what a merge is blocked on, and agreement between specification and implementation is not among them. | Medium | [U] Yes — the divergence is bounded to four parameter descriptions copied from one working example, and the same exposure already exists for `/tracks` today. Closing it needs contract testing, which is a larger change than this plan. |
| FM-03 | A sort-field allowlist names a column the table does not have. | [D::DD-01] The four allowlists are written per entity by hand. A wrong column name passes the `in_array` check, reaches the query builder, and fails at request time as a database error rather than at build time — PHPStan level 5 compares a string in an array against nothing, and PS-02 cannot see a schema. | Medium | [U] Yes — a wrong column surfaces on the first request against that sort field, and the new controller tests of FR-07 exercise each allowlist. |
| FM-04 | A future controller calls `getAll()`, which DD-04 leaves on the interface. | [D::DD-04, PS-03] The unbounded read stays available and reachable. PS-03's `Detected` column reads nothing — no architecture test exists, so an unbounded collection read reintroduced later ships silently, exactly as the current four did. | Medium | [U] Yes — removing it is a contract change PS-01 does not require, and `AbstractRepositoryTest` covers it. The risk is a future one, and this plan does not schedule that future. |
| FM-05 | A client outside this repository calls `/api/drivers` and receives ten rows where it previously received the table. | [D::DD-05] Any consumer written against the current unbounded behaviour breaks, and this repository cannot enumerate them. The published specification is updated in the same change, so the new behaviour is documented — but documentation does not reach a client already written. | High | [U] Yes — PS-01 makes the published contract the boundary of what a consumer may rely on, and the four endpoints' contract is being changed deliberately and published. An unbounded collection read is the defect; preserving it for unknown callers preserves the defect. |

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
| RK-01 | [V] No command was run against this repository. `composer install`, PHPStan, PHP-CS-Fixer and PHPUnit were read from configuration rather than executed, and whether PHP is available on this machine is unverified. Every claim about what compiles, passes or fails is read from source. | High | Degraded | Run `composer lint` and the PHPUnit suite before S-01 to capture a known-green baseline, so any later failure is attributable to this change rather than to a pre-existing condition or a missing toolchain. |
| RK-02 | [V] Three of the four SPA pages were never opened. `public/driversPage.php` establishes the fetch-everything-and-page-in-the-browser pattern; `carsPage.php`, `teamsPage.php` and `eventsPage.php` are named from the shared navigation and their handling is inferred from a sibling. | Medium | Breaking | Open all three before S-04. FM-01 is Critical and its prevention rests on changing four files, three of which are unexamined — if any fetches differently, its Files Touched row is wrong. |
| RK-03 | [V] The four sort-field allowlists need per-entity column knowledge this plan does not hold. `src/Models/*.php` was listed as a candidate and not opened, and `f1_db.sql` was never consulted, so the columns each allowlist may legitimately name are unestablished. | High | Degraded | Read each model and the schema during S-02, before writing any allowlist. FM-03 accepts a wrong column reaching runtime; that acceptance assumes the allowlists were written from the schema rather than guessed. |
| RK-04 | [V] Whether `TrackRepository` overrides `getAllWithParams` or inherits `AbstractRepository`'s implementation is unestablished — named in the investigation and set aside, since `RepositoryInterface` fixes the signature either way. | Low | Cosmetic | Read it during S-02. If it overrides, the other four repositories may need overrides rather than inheriting, which would add four rows to Files Touched. |

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

<!-- Zero rows. Two questions arose during authoring and both were resolved before the
     section they gated was written: the NG-02 sorting exclusion and the NG-04 OpenAPI
     exclusion, each surfaced by the contradiction check and each narrowed rather than
     parked. Four unread-source gaps remain, but each is a Risk with a mitigating step,
     not an unresolved question. -->


---

## Implementation Order
<!-- Dependency-ordered execution sequence, one row per step. Row order IS
     execution order — Depends On is for a prerequisite other than the
     immediately preceding row.

     Files: bare file path(s) from Files Touched changed in this step. What
     changes in each file is Files Touched's job — do not restate it here.

     Implements: DD-XX this step carries out — or FR-XX / NFR-XX / PS-XX / INV-XX
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
| S-00 | [D::RK-01] Capture a green baseline: `composer install`, `composer lint`, `php-cs-fixer check` and the PHPUnit suite. | — | — | — |
| S-01 | [D::RK-02, RK-03, RK-04] Read what the plan named and set aside: `src/Models/*.php` and `f1_db.sql` for the sort-field columns, `src/Repositories/TrackRepository.php` for whether it overrides, and the three unopened SPA pages. Correct Files Touched before writing code if any differs from what was inferred. | — | — | S-00 |
| S-02 | [D::DD-01] Add the protected paging helper to `AbstractController` — parameter parse, `page`/`limit` bounds, `order` allowlist, the four `X-*` header writes — taking the caller's sort-field allowlist as an argument. Leave `getAll(Response)` untouched so INV-04's signature does not move. | `src/Contracts/AbstractController.php` | DD-01, DD-02, FR-03, FR-04, FR-05, FR-07, NFR-01 | S-01 — the helper's allowlist argument is shaped by what the models actually expose. |
| S-03 | [D::DD-01, DD-03] Refactor `TrackController::getAllWithParams` onto the helper and replace the full-table count at line 58 with `$tracks->total()`. Behaviour and header values unchanged; `TrackControllerTest` must pass without modification beyond the moved call site. | `src/Controllers/TrackController.php`, `tests/Unit/Controllers/TrackControllerTest.php` | DD-01, DD-03, INV-02, INV-03 | S-02 — refactoring the working endpoint onto the helper first proves the helper against a test that already specifies the pattern. |
| S-04 | [D::DD-01, DD-05] Add `getAllWithParams(Request, Response)` to the four unpaged controllers, each delegating to the helper with its own sort-field allowlist. | `src/Controllers/CarController.php`, `src/Controllers/DriverController.php`, `src/Controllers/EventController.php`, `src/Controllers/TeamController.php` | DD-01, DD-04, DD-05, FR-01, FR-02, FR-06, FR-07, FR-08, NG-02 | S-03 |
| S-05 | [D::DD-05] Rebind the four collection routes to `:getAllWithParams` **and** change all four SPA pages to request pages and read the `X-Total-*` headers, in one commit. | `config/routes.php`, `public/driversPage.php`, `public/carsPage.php`, `public/teamsPage.php`, `public/eventsPage.php` | DD-05, FR-01, FR-05, INV-03, INV-04 | S-04 — FM-01 is Critical and its window is exactly the gap between these two edits: the moment a route pages, an unchanged SPA page shows ten rows as though they were all, with working-looking controls and no error. The two must not ship separately. |
| S-06 | [D::DD-05, PS-01] Add `page`, `limit`, `sort_by` and `order` and the four response headers to the remaining path files, matching `tracks.yaml:7–17` exactly. | `openapi/paths/cars.yaml`, `openapi/paths/drivers.yaml`, `openapi/paths/events.yaml`, `openapi/paths/teams.yaml` | DD-05, PS-01, FR-07, INV-02 | S-05 — the specification describes shipped behaviour, so it follows the behaviour rather than preceding it. PS-01 makes this step non-optional, not cosmetic. |
| S-07 | [D::DD-05] Update the two existing controller tests whose collection assertions expect unbounded results, and add the two that do not exist, covering the first page, the headers and the `400` cases. | `tests/Unit/Controllers/CarControllerTest.php`, `tests/Unit/Controllers/TeamControllerTest.php`, `tests/Unit/Controllers/DriverControllerTest.php`, `tests/Unit/Controllers/EventControllerTest.php` | DD-01, DD-05, FR-01, FR-02, FR-03, FR-04, FR-06, FR-07, NFR-01 | S-05 |
| S-08 | [D::RK-01, INV-05] Run the full CI gate locally — PHPStan level 5, `php-cs-fixer check`, `redocly lint openapi/openapi.yaml`, PHPUnit — and confirm each passes before opening a pull request. | — | INV-05, PS-02 | S-07 |

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
       - Every Postulate # (PS-XX) and Invariant # (INV-XX) is cited by at
         least one Design Decision or Failure Mode.
       - Every source of governing intent named in the investigation record
         is reflected in at least one Postulate or Invariant, or explicitly
         noted there as bearing on nothing in this plan. The check above
         tests whether what was written is relevant; this one tests whether
         what mattered was written.
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
