# Investigation: collection-pagination

## 2026-09-10 — Authoring pass

### Candidate list (written before any source was opened)

Drawn from the subject's own terms — collection endpoints, index reads, repositories —
plus the abstractions they sit inside, the response path they return through, and,
listed separately, whatever states why this codebase is shaped the way it is.

**The abstractions a collection read passes through**
1. `src/Contracts/RepositoryInterface.php`
2. `src/Contracts/AbstractRepository.php`
3. `src/Contracts/ControllerInterface.php`
4. `src/Contracts/AbstractController.php`

**The five collection endpoints and their repositories**
5. `src/Controllers/CarController.php`, `DriverController.php`, `EventController.php`, `TeamController.php`, `TrackController.php`
6. `src/Repositories/CarRepository.php`, `DriverRepository.php`, `EventRepository.php`, `TeamRepository.php`, `TrackRepository.php`

**The response path**
7. `src/Helpers/ResponseHandler.php`
8. `src/Enums/HTTPStatusCode.php`
9. `public/` — the front controller and route table
10. `config/`

**Neighbours of the above**
11. `src/Models/*.php` — what a repository returns
12. `src/Middleware/*.php` — what runs before a controller
13. `src/Repositories/UserRepository.php`, `TokenRepository.php` — repositories with no collection endpoint, to see whether the interface obliges them anyway
14. `stubs/`

**Sources that state what governs, rather than what is done**
15. `README.md`
16. `phpstan.neon` — a declared static-analysis level is a stated rule
17. `.php-cs-fixer.dist.php` — a declared style ruleset
18. `.editorconfig`
19. `composer.json` — declared PHP version, autoload standard, scripts
20. `docs/`
21. `openapi/` — the published contract, which is a rule the implementation answers to
22. `.github/workflows/continuous-integration.yml` — what CI enforces is what the project treats as non-negotiable
23. **Absent by design:** this repository carries no `AGENTS.md` and no `CLAUDE.md`. It was chosen for this run because it has none, so nothing hands the agent a stated rule for free.

**Tests**
24. `tests/` — 13 files; what they assert about collection reads

### Consulted

| Source | Established |
|---|---|
| `src/Contracts/RepositoryInterface.php` | **Paging already exists in the contract.** The interface declares `getAllWithParams(int $page, int $limit, string $sortBy, string $order): LengthAwarePaginator` alongside `getAll(): Collection`. Every repository is obliged to implement both. Sorting is coupled to paging in one signature — they are not separable at this contract. |
| `src/Contracts/AbstractRepository.php` | Implements both. `getAll()` is `$this->model::all()` — unbounded. `getAllWithParams` returns Eloquent's `LengthAwarePaginator`, which computes a total as part of paging. Stands alone as the source for the base implementation. |
| `src/Contracts/AbstractController.php` | `getAll(Response)` calls `$this->repository->getAll()` and writes `$items->toJson()`. Unbounded, and inherited by every controller that does not override it. Holds no query construction and no `Request` parameter on this method. |
| `src/Controllers/TrackController.php:25–70` | The one paged endpoint, and the established pattern in full: params `page` (default 1), `limit` (default 10), `sort_by` (default `id`), `order` (default `asc`); `page < 1` → 400; `limit < 1 \|\| limit > 100` → 400; a per-entity allowlist of sortable fields; `order` restricted to `asc`/`desc`. Totals are returned as **response headers** — `X-Total-Count`, `X-Total-Pages`, `X-Current-Page`, `X-Items-Per-Page` — and the body is a bare `$tracks->items()` array with no envelope. **Line 58 computes the total as `$this->repository->getAll()->count()`, loading every row to count them, on the one endpoint whose purpose is not to load every row** — while the `LengthAwarePaginator` returned two lines earlier already carries that total. |
| `config/routes.php:85–123` | **One of five.** `/tracks` routes to `getAllWithParams`; `/teams`, `/events`, `/drivers` and `/cars` route to `getAll`. Independent of the controller sources, and the count they give agrees. |
| `grep -rn 'getAll()\|getAllWithParams' src/` | Corroborates the above from a third direction: `getAllWithParams` appears in the interface, the abstract, and `TrackController` alone. No other controller references it. |
| `openapi/paths/` + `openapi/paths/tracks.yaml` | Five collection path files exist; **`tracks.yaml` is the only one documenting `page` and `limit`**, describing "default is 1" and "default is 10, max is 100". The published contract tracks the implementation exactly as it stands today, including its asymmetry. |
| `.github/workflows/continuous-integration.yml` | What the project treats as non-negotiable, stated by enforcement: `composer validate --strict`, PHPStan, `php-cs-fixer check` (PER-CS2.0), `redocly lint openapi/openapi.yaml`, PHPUnit. **`redocly lint` validates the specification's own syntax; nothing compares the specification against the implementation.** |
| `phpstan.neon` | Level 5 over `src`, `config`, `public`, with `tests/**` excluded and three stub files for Eloquent. Types only — no layering or architectural rule is expressible here. |
| `composer.json` | Slim 4.14, `illuminate/database` 11.30 (Eloquent standalone, not full Laravel), `zircote/swagger-php`. PSR-4: `App\` → `src/`, `Config\` → `config/`. Scripts `lint` and `fix` wrap PHPStan and PHP-CS-Fixer. |
| `README.md:9, :41–43, :98` | Lists "pagination" among the project's features, captions a GIF "Demonstrating pagination functionality on the Drivers page", and names PER-CS2.0 under standards. The pagination claims do not describe the Drivers API endpoint — see Conflicts. |
| `public/driversPage.php:10, :19–26` | The SPA page fetches `http://localhost:8080/api/drivers` — the entire collection — and pages it in the browser at `driversPerPage = 5`. This is the cost the task exists to remove, running in production today. |
| `tests/` listing | 13 files. Unit tests exist for `AbstractController`, `Car`, `Team` and `Track` controllers, and for `AbstractRepository` and `TeamRepository`. Repository tests construct a repository directly, with no HTTP request — which is what makes the layer split observable. |
| Search for a stated architectural rationale | `README.md`, `composer.json`, `phpstan.neon`, `.php-cs-fixer.dist.php` and the repository root were searched. **No `AGENTS.md`, no `CLAUDE.md`, no architecture document, and no stated reason for the controller/repository split anywhere.** The absence is itself the finding: one of the three governing rules below has no stated rationale to rest on. |

### Governing rules

| Governing rule | Basis | Cost | Detected |
|---|---|---|---|
| The published OpenAPI specification is the contract the implementation answers to. | **Stated rationale:** none in prose; the statement is the enforcement — CI runs `redocly lint openapi/openapi.yaml` on every push. **Consumer chain:** spec → the `gh-pages` workflow that publishes it → external clients written from those docs, and the `.postman/` collections. Past one hop, a consumer who never reads the source is left calling an endpoint that behaves differently from its documentation. **Regularity:** 5 of 5 collection endpoints have a path file, and 1 of 5 documents paging — the spec matches the implementation exactly today, asymmetry included. **Reasons to change:** client needs, response-size limits, new fields; all trace to one assumption — what an external client is entitled to rely on. **Independent of the stated rationale:** the consumer chain and the regularity count, neither of which reads the CI configuration. | A client written against the published documentation breaks, and does so at their end rather than ours. Established by the consumer chain, corroborated by the regularity count. | **Nothing.** `redocly lint` checks that the specification is valid, not that it is true. An endpoint that starts paging without a spec change passes CI unchanged. |
| PER-CS 2.0 and PHPStan level 5 govern everything under `src/`, `config/` and `public/`. | **Stated rationale:** `.php-cs-fixer.dist.php` and `phpstan.neon` declare them; `README.md:98` names PER-CS2.0. **Consumer chain:** the fixer and analyzer consume the source, CI consumes their exit codes, a non-zero code blocks the merge. The chain is short and terminates in a hard stop. **Regularity:** `phpstan.neon` covers 3 of the 4 top-level PHP directories, excluding `tests/**` explicitly. **Reasons to change:** a PHP version bump or a level bump; both trace to the declared quality bar. **Independent of the stated rationale:** the consumer chain and regularity, though weakly — both observe the same CI configuration the rationale is declared in. | The build fails and the change cannot merge. Established from the CI configuration directly. | **Loudly, on every push,** by two separate CI steps. This rule defends itself and needs no help from a plan. |
| HTTP concerns stay in controllers; query construction stays in repositories. | **Stated rationale: none exists.** Searched and recorded above. **Consumer chain:** repositories are consumed by controllers and, separately, by unit tests that construct them with no `Request` — so the split is what makes `AbstractRepositoryTest` and `TeamRepositoryTest` possible at all. Past one hop: the `Contracts/` interfaces stop describing what implementers do, and the abstract bases stop being substitutable, which is the whole reason they exist. **Regularity:** 13 of 13. All 7 repositories take a `Model` and return `Model`, `Collection` or `LengthAwarePaginator`, touching no `Request` or `Response`; all 6 controllers take `Request`/`Response` and issue no query. **Reasons to change:** a new transport, a different persistence layer, testability — all trace to one assumption, that each layer is replaceable without the other. **Independent of the stated rationale:** all three mechanisms, necessarily, since there is no stated rationale for them to depend on. This rule is corroborated more strongly than either rule above, and stated nowhere. | The two layers stop being independently testable and independently replaceable, and the existing repository unit tests become unwritable. Established by consumer chain and regularity; **no source states it**, so the cost is inferred from what the codebase does rather than from what anyone claimed. | **Nothing.** PHPStan level 5 checks types, not layering. No architecture test exists, and `tests/**` is excluded from analysis. A query in a controller ships silently. |

### Conflicts

| Conflict | What each states |
|---|---|
| The task premise versus the implementation | The task states that every index endpoint returns the full table. `config/routes.php:103` routes `/tracks` to `getAllWithParams`, and `TrackController:25–70` pages it. One of five collection endpoints is already paged, and the paging pattern this plan would introduce already exists in the codebase. The premise is wrong, and the plan depends on it: the work is generalising an established pattern, not introducing one. |
| `README.md` versus the API | `README.md:9` lists pagination among the project's features and `:41–43` captions a GIF "Demonstrating pagination functionality on the Drivers page". `config/routes.php:112` routes `/drivers` to the unbounded `getAll`, and `public/driversPage.php:19–26` fetches the whole collection and pages it in the browser at 5 per page. Both readings hold: the README describes the SPA truthfully and the API misleadingly. Neither is preferred here. A reader taking "Features include pagination" as an API capability is wrong; a reader watching the GIF is not. |
| `RepositoryInterface` versus the routes | The interface obliges all 7 repositories to implement `getAllWithParams`, including `UserRepository` and `TokenRepository`, which back no collection endpoint. Only `TrackRepository`'s implementation is reachable through a route. Five of seven implementations exist to satisfy the contract and are never called. |

### Not opened

| Not opened | Why |
|---|---|
| `src/Models/*.php` | What a repository returns. The paging change alters how many models are returned and in what wrapper, never what a model is. |
| `src/Middleware/*.php` | NG-03 excludes the authentication chain, and no paging parameter reaches authorization. Their existence and count were established from the directory listing. |
| `src/Repositories/TrackRepository.php` | Whether it overrides `getAllWithParams` or inherits the abstract implementation is unestablished. The signature and return type are fixed by `RepositoryInterface` either way, which is what the plan depends on. |
| `src/Enums/HTTPStatusCode.php`, `src/Helpers/ResponseHandler.php` | Listed as the response path. `TrackController` writes its status codes as integer literals and its headers directly, so neither is on the paged route as it stands — but this means the established pattern bypasses the project's own response helper, which is unexamined. |
| `docs/`, `.editorconfig`, `stubs/`, `.postman/` | `docs/` holds the README's images; `.editorconfig` and `stubs/` are subordinate to the PER-CS and PHPStan rules already established; `.postman/` is a consumer named in the consumer chain but not read. |
| `tests/Feature/`, `tests/Unit/Controllers/TrackControllerTest.php` | The test *inventory* was established from the listing and is what the layer-split consumer chain rests on. What `TrackControllerTest` asserts about paging specifically was not read, so **whether the established pattern is test-covered is unestablished** — named again below. |
| `public/carsPage.php`, `teamsPage.php`, `tracksPage.php`, `eventsPage.php` | `driversPage.php` was read and establishes the client-side paging pattern. Whether the other four SPA pages do the same is inferred from the shared navigation and unverified. |

### Sufficiency

The read set supports, from direct observation: that paging already exists in this codebase as a contract method, a base implementation and one wired endpoint, so the task is generalisation rather than introduction; the exact shape of that established pattern, down to parameter names, defaults, bounds, the header-not-envelope choice and the per-entity sort allowlist; that one of five collection endpoints uses it, corroborated independently by the routes, the controllers, a grep and the OpenAPI path files; that the one paged endpoint defeats its own paging with a full-table count that the paginator it already holds would have supplied; and three governing rules, each run through all four mechanisms, of which two are costly and undetected and one defends itself through CI.

It does not support the following, and no conclusion should rest past them:

- ~~**Whether the established pattern is test-covered is unestablished.**~~ **Closed in the same pass.** `tests/Unit/Controllers/TrackControllerTest.php` is 218 lines and specifies the pattern: a `getAllWithParams` describe block asserting all four parameter names, the `X-Total-Count` and `X-Total-Pages` headers, and `400` for page `0`, limit `101` and an invalid sort field. Generalising the pattern therefore inherits a written specification rather than a convention. Both header assertions use `Mockery::type('string')` and constrain the value's type only, not its provenance — so the redundant full-table count is unprotected by any test and can be replaced without touching one. **This also corroborates INV-02 from a third independent source**, alongside `TrackController` and `openapi/paths/tracks.yaml`.
- **The layer-split rule has no stated rationale, and its cost is inferred.** It is the most strongly corroborated of the three rules — 13 of 13, three independent mechanisms — and the only one nobody wrote down. Its cost figure rests on what the codebase does and what its tests require, not on any claim about why.
- **`redocly lint` was not run, and the specification was not diffed against the implementation.** That CI cannot detect a spec/implementation divergence is read from the workflow file's command, not observed by making one.
- **Four of five SPA pages were not opened.** The client-side paging pattern is established from `driversPage.php` alone.
- **No test was executed and no request was issued.** Every claim about behaviour is read from source. In particular, that `getAll()->count()` loads every row is read from Eloquent's semantics rather than observed against a query log.
