---
template_version: "1.4.0"
---

# Implementation Plan: Plan Skill Suite

## Problem Statement

[U] The global planning gate requires a plan document before implementation, and `PLANNING.TEMPLATE.md` now specifies what that document must contain. But a template constrains only the finished artifact. Its guidance is passive — it describes what a filled row should look like, with nothing standing between the agent and the row. It therefore cannot stop an agent from writing a cell it inferred, from choosing among viable design alternatives on its own authority, from stating Invariants it never investigated, or from treating the `PRE-EXECUTE CHECK` as a formality to acknowledge on the way to an execute signal. Those four are exactly the failure modes that matter, and all four occur before or during the write, where a document cannot intervene. A skill can: it holds control flow, so it can gate a write, refuse to proceed, and route a decision back to the reviewer instead of resolving it. The suite below exists to supply that control flow alongside the template, not in place of it.

---

## Invariants

| # | Invariant | Basis |
|---|---|---|
| INV-01 | [V] A user-level skill is a directory under `~/.claude/skills/<name>/` containing `SKILL.md` | Existing user-level skills at that path: `diagram/SKILL.md`, `python-coder-v2/SKILL.md`, `i-have-adhd/SKILL.md` |
| INV-02 | [V] `SKILL.md` frontmatter requires `name` and `description` at minimum; `argument-hint`, `allowed-tools`, `metadata`, `user-invocable` and `disable-model-invocation` are documented fields | code.claude.com/docs/en/skills, frontmatter reference; corroborated by `diagram/SKILL.md`, which declares `name`, `description`, `tools`, `disable-model-invocation` |
| INV-04 | [V] `TaskCreate`, `TaskGet`, `TaskList` and `TaskUpdate` are not provided by default on Opus 4.8, Sonnet 5, Fable 5, Mythos 5 or later; opt-in is `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`, `--allowedTools`, or `--tools` | code.claude.com/docs/en/tools-reference, "Task tool availability" |
| INV-05 | [V] `AskUserQuestion` accepts one to four questions per call, each carrying two to four options | Its tool schema: `minItems: 1, maxItems: 4` on `questions`, `minItems: 2, maxItems: 4` on `options` |
| INV-06 | [V] The template is at `plan/skills/templates/PLANNING.TEMPLATE.md` in the skills monorepo at version 1.4.0, and defines the provenance marker set, the ID series, and the twelve-check pre-execute check | That file's frontmatter and header block |
| INV-07 | [V] The session scratchpad directory is session-specific — a new session receives a different path | Environment description, which names the path and states it is session-specific |
| INV-08 | [V] `user-invocable: false` hides a skill from the `/` menu while leaving Claude able to invoke it; `disable-model-invocation: true` does the reverse and puts the skill beyond reach of the Skill tool | code.claude.com/docs/en/skills, invocation-control table and Skill-invocation restrictions |
| INV-09 | [V] The Altitude authoring style: instructions to the agent are formalized, output to the practitioner is not; gates use one four-column shape; only three moments earn a fixed block; internal skills emit nothing but a completion tag; the executing agent is never named | `Altitude_Skills__Authoring_Methodology.md` — Governing Principle, Checkpoint & Gate Conventions, Invocation Mechanics — plus a grep across `design-templates/.claude/skills/*/SKILL.md` returning zero occurrences of "Claude", "the model", "LLM", "assistant" or "AI" |

---

## Requirements

### Functional Requirements

| # | Requirement | Verification |
|---|---|---|
| FR-01 | [U] IF a task does not meet the planning criteria THEN the `plan` skill shall decline to author a plan and state which criterion is unmet | Invoke `plan` for a single-file typo fix; observe refusal naming the criterion |
| FR-02 | [U] WHILE authoring any section the `plan` skill shall write no cell whose content it inferred | Invoke `plan` on a task with a deliberately unstated constraint; observe it asks rather than filling the cell |
| FR-03 | [U] WHEN two or more alternatives for a design decision are viable the `plan` skill shall present the choice through `AskUserQuestion` with neutral options and no recommendation | Invoke `plan` on a task admitting two storage approaches; observe a neutral question, and a `Resolution` marked `[U]` |
| FR-04 | [U] WHEN an unresolved item blocks the current section the `plan` skill shall ask immediately; WHERE it does not block, the skill shall record it in Open Questions | Invoke `plan` with one blocking and one non-blocking unknown; observe one immediate question and one parked row |
| FR-05 | [U] WHERE questions are mutually independent the `plan` skill shall batch up to four per `AskUserQuestion` call; IF one answer could change a later question THEN it shall ask sequentially | Invoke `plan` on a task with three independent design forks; observe a single batched call |
| FR-06 | [U] IF no plan document matches in the session scratchpad THEN the `plan` skill shall decline the revision and offer to re-author | Request a revision in a fresh session; observe refusal plus the re-author offer |
| FR-07 | [U] WHEN a row in Invariants, Requirements, Design Decisions or Files Touched is mutated the responsible atomic shall invoke `plan-cascade` | Mutate a `DD-XX` row; observe `plan-cascade` invoked and the dependent sections walked |
| FR-08 | [U] IF `plan-audit` returns any finding THEN the `plan` skill shall not request an execute signal | Author a plan with an uncited `INV-XX`; observe the execute signal withheld |
| FR-09 | [U] WHEN `plan-audit` returns clean the `plan` skill shall deliver the document via `SendUserFile` with a short inline summary | Complete a plan; observe the file card plus a summary in the response |
| FR-10 | [U] WHEN more than one `PLAN__*.md` matches the `plan` skill shall ask which to operate on; WHERE exactly one matches it shall proceed silently | Create two plan files, invoke `plan`; observe the disambiguating question |
| FR-11 | [U] WHEN investigation completes the `plan` skill shall write `INVESTIGATION__<task-slug>.md` naming every source consulted and asserting the read set was sufficient; IF that record is absent THEN Invariants and Files Touched shall not be written | Invoke `plan` and interrupt before investigation; observe Invariants withheld and no record written |
| FR-12 | [U] WHILE extracting content that is not a design fork the `plan` skill shall ask in prose rather than through a structured card | Invoke `plan` and observe the problem statement extracted conversationally, with no card |
| FR-13 | [U] WHEN a plan is changed after it has received an execute signal the `plan` skill shall append one Revision Log row naming the row changed, every row reached, and how each was resolved | Add a requirement to an approved plan; observe a Revision Log row whose `Propagated Into` reads "none", and a new execute signal requested |
| FR-14 | [U] WHEN a revision targets a section that has a matching gate the `plan` skill shall run that gate before invoking the section's atomic | Revise an `INV-XX` row; observe `plan-investigate` run and the record appended before `plan-update-invariant` is called |

### Non-Functional Requirements

| # | Requirement | Threshold | Verification |
|---|---|---|---|

---

## Non-goals

| # | Excluded Capability | Reason |
|---|---|---|
| NG-01 | [U] An external deterministic validator equivalent to Altitude's `altitude` CLI | Explicitly out of scope; the suite relies on gates plus the blocking audit instead |
| NG-02 | [U] Driving implementation against an approved plan | Lifecycle is authoring plus revision only; Altitude keeps this separate in `implement-req` / `implement-all` |
| NG-03 | [U] Plan persistence across session boundaries | Scratchpad location chosen knowingly, with the single-session consequence accepted |
| NG-04 | [U] Atomics for Non-goals, Failure Modes, Risks, Open Questions or Implementation Order | Those sections have no downstream citers, so a careless change there invalidates nothing |

---

## Design Decisions

| # | Decision Point | Resolution | Satisfies | Alternatives Rejected |
|---|---|---|---|---|
| DD-01 | How the suite decomposes into files | [U] Seven skills: a `plan` hub, a standalone `plan-audit`, a shared internal `plan-cascade`, and four internal atomics | FR-07, FR-08 | Single skill — the audit must be re-runnable after a revision, which it cannot be when buried as an internal step; atomics for every section — selection is driven by blast radius, not by uniformity |
| DD-02 | Which sections warrant an atomic | [U] Design Decisions, Requirements, Invariants, Files Touched | FR-07 | Design Decisions alone — leaves three citation targets unguarded at edit time; adding Problem Statement — heaviest invalidation but it is not a citation target, so cascade has no ID to key on |
| DD-03 | When atomics fire | [U] On mutation always, and additionally on initial authoring for Design Decisions | FR-02, FR-03 | Mutation only — misses the rationalization failure, which occurs on the first write; both uniformly — ceremony where nothing downstream yet exists to invalidate |
| DD-04 | What forces the agent through the workflow | [U] The four Task tools, targeted directly as Altitude does | INV-04 | On-disk phase checklist — environment-independent but adds a template section and a write per transition; gates only — nothing makes a skipped phase visible; dual code path — untestable branch in every skill |
| DD-05 | Where a plan document lives | [U] Session scratchpad, named `PLAN__<task-slug>.md` | NG-03, INV-07 | In-repo gitignored — survives sessions so revision and re-audit keep working, rejected in favor of zero repo footprint; in-repo committed — reviewable in diffs, rejected for the same reason; user-level — survives but needs the repo name in the filename |
| DD-06 | How the target plan is resolved | [U] Glob `PLAN__*.md`; proceed silently on one match, ask when several match | FR-10 | Required slug argument — unambiguous but must be typed on every revision; confirm on every invocation — an extra round trip in the common single-plan case |
| DD-07 | Behavior when no plan matches | [U] Decline the revision and offer to re-author | FR-06 | Reconstruct from conversation context — risks presenting an invented plan as the approved one; ask which — a round trip with no default behavior |
| DD-08 | How the no-inference rule is made checkable | [U] Provenance markers `[U]`/`[V]`/`[D]`/`[A]` prefixing each row's claim cell plus designated reviewer-authority cells, per the template | FR-02, INV-06 | No markers — the audit gains no way to detect a quietly inferred cell; Altitude's `[E]`/`[M]`/`[A]` — grades quantitative confidence rather than source authority, and presumes a codebase exists |
| DD-09 | How the skill consults the reviewer | [U] Split by kind: `AskUserQuestion` with neutral options and no recommendation for genuine design forks, where attribution must be unambiguous for a `[U]` marker to be honest; natural prose for all other extraction. Batch up to four independent forks per call, sequential when dependent | FR-03, FR-05, FR-12, INV-05 | Structured cards throughout — formalizes output the Altitude principle keeps conversational, and turns extractions that read as a sentence into cards; natural prose throughout — consistent with that principle, but rests a `[U]` marker on a prose exchange and leaves batching no mechanism; recommendation marked — faster, but places a thumb on a scale that is the reviewer's |
| DD-10 | What the audit does with findings | [U] Blocking, not waivable — a finding is resolved by fixing the plan | FR-08 | Advisory — reproduces the rubber-stamping risk the audit exists to prevent, one layer up; blocking with recorded waiver — needs a waiver mechanism the template has no home for |
| DD-11 | How a finished plan reaches the reviewer | [U] `SendUserFile` plus a short inline summary | FR-09 | File only — no context for whether to open it; full inline render — a long plan dominates the transcript; path only — unreachable from another device, and the scratchpad path is session-local |
| DD-12 | How the skills are named | [U] `plan-` prefix throughout, with verb-first atomics carrying full section names | INV-01 | Bare `update-*` atomics — collide with Altitude's own project-scoped atomics, and bare `cascade` collides outright; shortened nouns — `decision` and `files` stop matching the section headers they write |
| DD-13 | What happens when a task does not warrant a plan | [U] The hub verifies the planning criteria and declines with reasoning when none is met | FR-01 | Advisory only — states an assessment and proceeds regardless, so nothing guards against planning a trivial task; drop the check — no self-serve entry point for an agent that should have planned and did not |
| DD-14 | How an unresolved item is routed | [U] Ask immediately when it blocks the current section; record it in Open Questions when it does not | FR-04 | Always ask immediately — Open Questions stays empty by construction but every non-blocking unknown interrupts; park everything and drain at the end — later sections get authored on top of unresolved questions |
| DD-15 | Where the investigation record lives | [U] A separate `INVESTIGATION__<task-slug>.md` beside the plan in the scratchpad | FR-11 | New template section — travels with the plan and the audit can require it, rejected to keep process content out of the design document; second table under Invariants — records sources that yielded nothing, rejected for the same reason |
| DD-17 | What writing style the seven skills are authored in | [U] The Altitude authoring style per INV-09: agent never named, practitioner in third person, bare imperatives, gate and routing tables formalized, pushback given as shape rather than script, internal skills silent but for their completion tag | INV-09 | Author freely in this session's own register — no consistency with the framework the suite is modelled on, and no rule distinguishing what to formalize from what to leave conversational; adopt only the surface conventions — tables and tags without the governing principle, which is the part that decides every unlisted case |
| DD-18 | Where the Revision Log write lives | [U] The `plan` hub writes it, once per revision at the end of the Revise route, from the reached-row list each atomic reports back | FR-13 | `plan-cascade` writing it — cascade runs only on a mutation, so a post-approval create diverges from the approved plan with nothing recording it; cascade running on every revision regardless of mode — its completion tag then cannot distinguish a walk that found nothing from one that could not have found anything; a log-only mode in cascade — leaves a skill named for cascading with a mode that cascades nothing, and pushes knowledge of which modes have dependents into all four atomics |
| DD-16 | What frontmatter the seven skills declare | [U] `name` and `description` on all seven; `user-invocable: false` on the five internals; `argument-hint` on the internals; `allowed-tools` per skill; `metadata` carrying skill version and the template version written against | INV-02, INV-08 | Minimal surface — `name` and `description` only, rejected because the atomics' arg contracts and the template pinning would then live only in prose; `disable-model-invocation` on the internals — puts them beyond reach of the Skill tool, breaking hub-to-atomic invocation |
| DD-19 | Where the investigation procedure lives | [U] Its own user-invocable skill, `plan-investigate`, called by the hub on both the Author and Revise routes | FR-11 | A paragraph in the hub, where it began — three sentences carrying no enumeration discipline, no record shape and no gate of its own, for the phase holding the only Critical failure mode this plan declined to accept; a suite-internal skill — knowing what an agent did not read is useful wherever it reports findings, so hiding it behind the hub would waste it |
| DD-20 | Whether gates run on the Revise route | [U] The hub runs the gate owning the changed section before invoking that section's atomic | FR-14 | Leaving Revise ungated — every atomic asserts its gate ran upstream and on that route nothing ran it, so a revision could rewrite an Invariant's `Basis` to something never verified; gating investigation alone — closes one of three instances of the same defect and leaves the requirement and design-decision gates equally unrun |

---

## Files Touched

| File | Operation | What Changes | Why |
|---|---|---|---|
| `~/.claude/skills/plan/SKILL.md` | Create | [D::DD-01] The hub: trigger gate, document instantiation, intent routing, phase sequence, gates on both routes, investigation call, Revision Log, delivery | DD-01, DD-04, DD-15, DD-18, DD-19, DD-20 |
| `plan/skills/plan-investigate/SKILL.md` | Create | [D::DD-19] The investigation procedure as its own skill: enumeration gate, candidate sourcing, the two-table record, qualified sufficiency | DD-19, FR-11 |
| `~/.claude/skills/plan-audit/SKILL.md` | Create | [D::DD-01] Standalone re-runnable implementation of the template's pre-execute check | DD-01, DD-10 |
| `~/.claude/skills/plan-cascade/SKILL.md` | Create | [D::DD-01] Internal forward walk from a mutated section through its dependents | DD-01, FR-07 |
| `~/.claude/skills/plan-update-design-decision/SKILL.md` | Create | [D::DD-02] Internal atomic writing one `DD-XX` row; the only one firing on initial authoring | DD-02, DD-03 |
| `~/.claude/skills/plan-update-requirement/SKILL.md` | Create | [D::DD-02] Internal atomic mutating one `FR-XX` or `NFR-XX` row | DD-02 |
| `~/.claude/skills/plan-update-invariant/SKILL.md` | Create | [D::DD-02] Internal atomic mutating one `INV-XX` row | DD-02 |
| `~/.claude/skills/plan-update-files-touched/SKILL.md` | Create | [D::DD-02] Internal atomic mutating one Files Touched row | DD-02 |

---

## Failure Modes

| # | Trigger | Behavior | Severity | Accepted? |
|---|---|---|---|---|
| FM-01 | A skill is invoked in a session that did not opt into the Task tools (INV-04) | [V] The hub's first action returns nothing, so no phase is tracked and DD-04's forcing mechanism is absent; authoring still proceeds, silently unguarded | High | [U] Yes — the launch requirement is stated in each skill's description, and every gate plus the blocking audit still runs; only phase visibility is lost |
| FM-02 | A revision is requested after the authoring session ended | [D::DD-05] No `PLAN__*.md` matches; DD-07 declines and offers to re-author, so approved work is not silently re-planned but is unrecoverable | Medium | [U] Yes — the loss surfaces immediately rather than producing a reconstructed plan nobody approved |
| FM-03 | The model invokes an atomic or `plan-cascade` directly rather than through the hub | [V] The guard clause is prose the same model evaluates, so nothing mechanically prevents a write that skipped its gate and confirmation | Medium | [U] Yes — INV-08 shows no setting expresses "hub may invoke, model may not," since the hub is the model; the alternative would sever hub-to-atomic reach |
| FM-04 | The agent marks a `Resolution` `[V]`, asserting no choice existed, when a viable alternative was in fact passed over | [D::DD-08] The plan reads as reviewer-sanctioned where the agent in fact decided; the audit reads `Alternatives Rejected` prose and cannot mechanically distinguish non-viable from less attractive | Critical | [U] Yes — Critical severity is on the record, and `Alternatives Rejected` gives a reviewer the prose needed to catch it on reading |
| FM-05 | The investigation gate is satisfied by a shallow read that misses a relevant constraint | [D::DD-08] Invariants come out correctly formatted, fully cited and internally consistent, yet incomplete; prevented by DD-15 and FR-11, which put the consulted source set and a sufficiency assertion on the record where the reviewer can judge the scope | Critical | [U] No — DD-15, FR-11 |

---

## Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RK-01 | [V] The Task tools are omitted by default precisely because these models "keep track of multi-step work without a written checklist"; that rationale may extend to removing the opt-in | Low | Degraded | Each skill's `description` states the launch requirement, so a session without it is diagnosable rather than mysterious |
| RK-02 | [D::DD-05] Neither the plan nor its investigation record survives the session, so a plan approved and partially implemented cannot be revised or re-audited later | Medium | Degraded | DD-07 refuses rather than reconstructing, so the loss surfaces immediately instead of producing a plan nobody approved |
| RK-03 | [V] Seven skills enter the global skill namespace, where `plan` is a common word that a future built-in could claim | Low | Cosmetic | DD-12's `plan-` prefix scopes all seven; only the bare hub name is exposed to collision |

---

## Open Questions

| # | Question | Blocks |
|---|---|---|

---

## Implementation Order

| # | Step | Files | Implements | Depends On |
|---|---|---|---|---|
| S-01 | [D::DD-01] Write `plan-cascade` — traversal table, guard clause, completion tag | `~/.claude/skills/plan-cascade/SKILL.md` | DD-01, DD-16, DD-17, FR-07 | — |
| S-02 | [D::DD-02] Write the four atomics — arg signatures, guard clauses, single-row writes, cascade invocation | `~/.claude/skills/plan-update-design-decision/SKILL.md`, `~/.claude/skills/plan-update-requirement/SKILL.md`, `~/.claude/skills/plan-update-invariant/SKILL.md`, `~/.claude/skills/plan-update-files-touched/SKILL.md` | DD-02, DD-03, DD-16, DD-17 | S-01 — each atomic invokes cascade by name, so its traversal contract must exist first |
| S-03 | [D::DD-10] Write `plan-audit` — the template's pre-execute check as a standalone blocking pass | `~/.claude/skills/plan-audit/SKILL.md` | DD-01, DD-10, DD-16, DD-17 | — |
| S-04 | [D::DD-01] Write the `plan` hub — trigger gate, instantiation, routing, phase sequence, gates, investigation record, delivery | `~/.claude/skills/plan/SKILL.md` | DD-04, DD-05, DD-06, DD-07, DD-08, DD-09, DD-11, DD-13, DD-14, DD-15, DD-16, DD-17, DD-18 | S-02, S-03 — the hub invokes the atomics and the audit by name |
| S-05 | [D::DD-12] Verify all seven load and are correctly scoped: hub and audit reachable, five internals hidden from the `/` menu and still reachable by the hub | `~/.claude/skills/plan/SKILL.md`, `~/.claude/skills/plan-audit/SKILL.md`, `~/.claude/skills/plan-cascade/SKILL.md`, `~/.claude/skills/plan-update-design-decision/SKILL.md`, `~/.claude/skills/plan-update-requirement/SKILL.md`, `~/.claude/skills/plan-update-invariant/SKILL.md`, `~/.claude/skills/plan-update-files-touched/SKILL.md` | DD-12, INV-01, INV-02, INV-08 | S-04 |
| S-06 | [D::DD-19] Write `plan-investigate`, replace the hub's investigation paragraph with a call to it, and wire the Revise route to run the gate owning each changed section | `plan/skills/plan-investigate/SKILL.md`, `~/.claude/skills/plan/SKILL.md` | DD-19, DD-20, FR-14 | S-04 — the hub must exist before its investigation step and Revise route can be rewired |

---

## Revision Log

| Date | Mutated Row | Propagated Into | Resolution |
|---|---|---|---|
| 2026-09-09 | INV-06 — template version pin | DD-08, which cites it — confirmed still valid, the marker scheme is unchanged | The template gained a twelfth pre-execute check requiring every Design Decision's `Satisfies` to name a row, and moved to 1.4.0. `plan-audit` implements it and repins. `plan-cascade` and the four atomics stay pinned at 1.3.3 — the columns their bodies name are untouched by this version, so their declarations remain accurate. |
| 2026-09-09 | FR-13 created; DD-18 created, then revised | Implementation Order S-01 and S-04; Files Touched `~/.claude/skills/plan/SKILL.md` | FR-13 and DD-18 recorded who owns the Revision Log write. First use showed a post-approval create triggers no cascade and so wrote no row, which is the divergence this section exists to catch. DD-18 was reversed from cascade ownership to hub ownership: `plan-cascade`, the four atomics and the `plan` hub were amended, and the `phase` argument — dead once cascade stopped writing the log — was removed from all five internal skills. |
| 2026-09-09 | INV-06 — template location | DD-08, which cites it — confirmed still valid; the marker scheme is unchanged and only the file's location moved | The seven skills and the template moved into the skills monorepo under `plan/skills/`, and the originals under `~/.claude/` were removed. INV-06 repointed, and the plan's own `template_version` repinned to 1.4.0, whose twelfth check it already satisfies. Files Touched keeps its `~/.claude/skills/` paths: those record where implementation occurred, and repointing them would falsify that rather than update it. |
| 2026-09-09 | FR-14, DD-19 and DD-20 created; the hub's Files Touched row updated | Implementation Order — new step S-06 | Investigation extracted from the hub into `plan-investigate`, an eighth skill, and the Revise route wired to run the gate owning each changed section — closing three instances of an atomic asserting a gate its caller never ran. Files Touched gains a repo-path row for the new skill while the original seven keep their `~/.claude/skills/` paths, so that table now carries two conventions: historical for the files that moved, current for the one that never did. |
