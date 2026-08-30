# Plan — C1: Batch type/axis sequencing (#8)

**Status:** Planning. Not implemented. Stage 2 (implementation) is gated on an explicit execute
signal and on the open questions below.
**Parent:** `plans/5-frontload-question-generation.md` (Feature C, #5) — approved. Its artifact
schema, two-pass draw decision, and REQ-C-001…011 are binding and are not revisited here.
**Branch:** `feat/8-batch-type-axis-sequencing`
**Target file:** `mcq-probe/skills/mcq-probe-0-router/SKILL.md` (single file; the split is #6).

---

## 1. Background / context

`mcq-probe` runs Intake (I1–I6) → Trial Loop (7 steps, per trial) → Response Protocol →
Analysis Phase → Report. Per trial the orchestrator calls `SCRIPT_TYPE` for the question type
and `SCRIPT_AXIS` for the judgment axis, reads the four generation prompts once on Trial 1,
constructs the trial from the type's prompt, presents it, waits, grades, and authors the full
breakdown live from the Response Protocol. Nothing about a trial exists before the trial before
it has been answered.

This issue moves the type draw, the axis draw, the axis refit, and the content construction for
**all** slots ahead of the first presentation, leaving a Delivery Loop that presents, parses,
grades against a stored key, and assembles the breakdown from stored explanation atoms.

### Key globals

| Global | Value before | Value after |
|---|---|---|
| Generation timing | Per trial, interleaved with delivery (Trial Loop steps 1–4) | Once per batch, before any presentation |
| `BATCH_SIZE` | n/a | New. `= N` for a bounded session; endless-mode windowing is #4 |
| Batch count | n/a | Exactly 1 for a bounded session (degenerate case, no separate mechanism) |
| Type draw | `SCRIPT_TYPE` once per trial, at delivery time | `SCRIPT_TYPE` once per slot, in pass 1 |
| Axis draw | `SCRIPT_AXIS` once per trial, `--exclude` = axes used so far | `SCRIPT_AXIS` once per slot, `--exclude` = axes assigned to earlier slots |
| Ordering/matching axis refit | Trial Loop step 2, mid-delivery, ≤3 attempts | Pass 2, mid-generation, ≤3 attempts, re-drawing only from axes assigned to **no other slot** |
| Rejected axis | Not added to used-axes; available to later trials | Not added to used-axes; available to other **slots** (REQ-C-004) — unchanged in substance |
| Prompt load | Trial Loop step 3, "Trial 1 only" | Generation Phase, once, before pass 2. Still all four — gating is #6 |
| `probe_target` | Authored after each trial (Trial Loop step 7) | Authored in pass 2, stored in the artifact |
| Breakdown prose | Authored live, per trial, after the learner answers | Assembled from stored atoms; delivery authors no new rationale and reads no generation prompt (REQ-C-010) |
| Batch artifact | n/a | In-context only. No path constant, no writer, no file — #7 persists it later |
| First-trial latency | ~1 trial of generation | ~`BATCH_SIZE` trials of generation. Announced, never silent (REQ-C-011) |
| `SKILL.md` length | 785 lines | Grows; exact delta unmeasured until stage 2 |
| Difficulty invariant | `CLAUDE.md`, enforced by the per-trial internal-validation checklist | **Unchanged.** Checklist runs per slot, inside pass 2, before the slot enters the artifact |

### Seam-map verification

The parent plan (and `plans/18-plugin-bundle-restructure.md` §Seam map) records Trial Loop =
lines 236–358, Response Protocol = 359–532. **Verified against the current file, both exact.**
`## Trial Loop` is line 236; line 357 is the closing `---`. `## Response Protocol` is line 359;
line 531 is the closing `---` of Tangent Handling. Router = 1–235, Analysis = 533–785, file
length 785. No drift.

### Pipeline after this change

Intake I1–I6 (unchanged) → **Generation Phase** (announce; set `BATCH_SIZE = N`; load the four
prompts; pass 1 draws type+axis for every slot; pass 2 constructs content slot by slot, refitting
ordering/matching axes, running the internal-validation checklist per slot, and writing each slot
into the in-context batch artifact) → **Delivery Loop** (per trial: present, wait, parse, grade
against the stored key, assemble the breakdown from stored atoms, record the result) → Analysis
Phase → Report. Both new sections are `##` headings in the same file so #6's split stays a cut,
not a rewrite.

---

## 2. Problem statement

Three concrete defects in the current Trial Loop block Feature C:

1. **No phase boundary exists.** Type selection, axis selection, prompt load, construction,
   presentation, waiting, grading, and internal recording are seven steps of one loop under one
   `##` heading. There is nothing for #6 to split along and nothing for #9's atoms to be consumed
   by, because there is no consumer distinct from the producer.

2. **The axis draw cannot see the batch.** `SCRIPT_AXIS --exclude` is passed only the axes used by
   *completed* trials, so the axis assignment for trial k is undecidable until trial k−1 has been
   answered. Any cross-trial property — #10's consistency pass, #4's rolling windows — has no
   input to work from.

3. **Two instructions in `SKILL.md` and eight in the prompts assert the opposite of Feature C.**
   `SKILL.md` line 76 reads "Generate one trial at a time. Present it. Wait for response." Each
   of the four generation prompts carries a `<generation-cadence>` block ("Do NOT pre-generate all
   trials before the learner has responded. Do NOT present trials as a numbered batch.") and a
   `<trial-sequence-rules><rule id="1-at-a-time">` block ("This is not optional — it is
   structurally required. Batching trials destroys the ability to adapt subsequent trials based on
   what earlier trials reveal."). Line 76 is inside this issue's scope. The eight prompt-side
   assertions are **not** — they live in files #9 owns. See OQ-1; this is the one finding that can
   make a correct implementation of #8 do nothing at runtime.

---

## 3. Design decisions

Every row is inherited from the parent plan, the issue body, or the current file — none is
originated here. Genuine forks are in §8, unresolved.

| Decision | Resolution | Source |
|---|---|---|
| Phase boundary | Trial Loop is replaced by two sibling `##` sections, `## Generation Phase` and `## Delivery Loop`, in the same `SKILL.md` | Parent §Design decisions (Phase restructure); issue #8 body |
| Draw ordering | Two-pass. Pass 1 = type+axis for all `BATCH_SIZE` slots. Pass 2 = content, slot by slot | Parent §Design decisions (Axis-fit chicken-and-egg); REQ-C-002/003 |
| Where the refit runs | Pass 2, not pass 1 — the fit check asks whether the axis can force *this scenario's* order/grid, which does not exist until content is constructed | Parent, same row |
| Refit exclusion set | `SCRIPT_AXIS --exclude` = (axes currently assigned to any **other** slot) ∪ (axes rejected for **this** slot). ≤3 attempts, then hold-and-reconstruct | REQ-C-003; REQ-ORD-E-003 / REQ-MAT-E-003 |
| Rejected-axis bookkeeping | A rejected axis is not added to the session's used-axes list and stays drawable by other slots' refits; only the finally-used axis enters Axis Coverage | REQ-C-004; REQ-ORD-F-016 / REQ-MAT-F-016 |
| Refit exhaustion | Hold the last-drawn axis, reconstruct the scenario (ordering) or case-set (matching). Never substitute the trial type | REQ-ORD-E-003 / REQ-MAT-E-003, unchanged semantics |
| `BATCH_SIZE` | Parameterized. Bounded session sets `BATCH_SIZE = N` and produces exactly one batch, `batch_index: 0`. No endless-mode windowing | Parent §Design decisions (Batch sizing); issue #8 non-goals |
| Prompt load | Once, in the Generation Phase, before pass 2. All four, unconditionally | Parent §Background (prompt load "unchanged by this issue") — and pass 2's fit checks cite `ORDERING_PROMPT` / `MATCHING_PROMPT`, so the load must precede them |
| I5/I6 gates | Unchanged. `--exclude ordering` / `--exclude matching` / `--exclude ordering,matching` now applies to every pass-1 slot draw rather than every trial | REQ-C-002; REQ-ORD-F-010 / REQ-MAT-F-010 |
| Artifact location | In-context only. No path constant, no file, no writer script | Parent §Design decisions (Artifact location); #7 non-goal |
| Artifact field names | Verbatim from the parent schema (`batch_index`, `trials[]`, `trial_index`, `question_type`, `axis`, `axis_rejected`, `probe_target`, `stem`, `choices`, `key`, `explanation.{axis_statement,key_survival,distractor_failures,near_duplicate_differentiator}`). No renaming | Parent §Artifact schema ("field names are binding") |
| `probe_target` timing | Authored in pass 2 and stored per slot — it is an artifact field, so it cannot be authored after presentation as today's Trial Loop step 7 does | Parent §Artifact schema. Authorship *ownership* is OQ-6 |
| Announcement | The Generation Phase opens with a learner-visible announcement; generation is never silent | REQ-C-011; FM-C-5 |
| Difficulty invariant | Untouched. The per-slot internal-validation checklist in each generation prompt still gates every slot, and runs before the slot is written to the artifact. This issue moves *when* work happens, never *what a distractor must satisfy* | `CLAUDE.md`; parent FM-C-1 |
| Split-friendliness | Both new sections start on `##` headings and no section is split across the Generation/Delivery boundary, preserving #18's seam-map property | `plans/18-plugin-bundle-restructure.md` §Seam map |

---

## 4. Requirements

Owned by this issue, verbatim from the parent plan.

| ID | Requirement | Scope |
|---|---|---|
| REQ-C-001 | A Generation Phase produces the full batch artifact before any trial is presented | `SKILL.md` — new `## Generation Phase` |
| REQ-C-002 | Pass 1 draws type+axis for all `BATCH_SIZE` slots, honoring the I5/I6 gates and the no-reuse-within-session axis rule | `SKILL.md` — Generation Phase, pass 1 |
| REQ-C-003 | Pass 2 generates content per slot; ordering/matching axis refit runs here, re-drawing only from axes assigned to no other slot, up to 3 attempts, then hold-and-reconstruct | `SKILL.md` — Generation Phase, pass 2; Error Handling REQ-ORD-E-003 / REQ-MAT-E-003 |
| REQ-C-004 | A rejected axis is not added to the session's used-axes list; it stays available to other slots | `SKILL.md` — Generation Phase, pass 2; Active Constraints |
| REQ-C-010 | The Delivery Loop presents, parses, grades against the stored key, and assembles the breakdown from stored atoms — it authors no new rationale and reads no generation prompt | `SKILL.md` — new `## Delivery Loop` + Response Protocol (form of edit is OQ-4) |
| REQ-C-011 | Batch generation is announced ("Preparing your trials…"), never silent | `SKILL.md` — Generation Phase opening |

**Non-goals, explicit.** No edit to any file under `prompts/` (#9). No edit to
`mcq-probe/.claude-plugin/plugin.json` — the version bump is the orchestrator's, at merge time. No
consistency pass (#10). No on-disk persistence (#7). No file split (#6). No endless-mode
windowing (#4) beyond parameterizing `BATCH_SIZE`. **No change to question difficulty, distractor
construction, near-duplicate/orthodox-but-wrong construction, or any internal-validation
checklist.**

---

## 5. Line-range disposition in `SKILL.md`

Line numbers are current (785-line file), pre-edit.

| Lines | Section | Disposition |
|---|---|---|
| 1–10 | Frontmatter | **Untouched** |
| 12–21 | Title + intro prose | **Untouched.** "gives full breakdowns after every response" stays true — the breakdown is assembled, not authored, but it is still delivered after every response |
| 23–64 | File Path Constants + Environment note | **Untouched.** No new path constant: the artifact is in-context |
| 67–81 | Active Constraints | **Rewritten in place.** L71 prompt-load "on Trial 1" → Generation Phase. L72/L73 "before every trial" → once per slot in pass 1. L74/L75 refit bullets → pass 2, plus the "assigned to no other slot" clause. **L76 deleted** — "Generate one trial at a time…" is the in-file contradiction of REQ-C-001. L77 probe-target timing → pass 2. L78–L80 untouched. New bullets: batch-artifact-never-rendered, and the REQ-C-011 announcement |
| 84–98 | Intake I1 | **Untouched** |
| 99–128 | Intake I2 (trial count → N) | **One-line addition** setting `BATCH_SIZE = N` for a bounded session (placement is minor; see OQ-8) |
| 130–192 | Intake I3, I4 | **Untouched** |
| 193–232 | Intake I5, I6 | **Two cross-reference edits only.** L208 and L226 both read "see Trial Loop, Step 2" and must repoint to the Generation Phase's pass-2 refit step. The determinations themselves are untouched |
| **236–358** | **`## Trial Loop`** | **Replaced.** Becomes `## Generation Phase` + `## Delivery Loop`. Step-level fate: step 1 (240–256) → pass 1 type draw; step 2 (258–304) → split, base draw to pass 1 and both refit blocks to pass 2; step 3 (306–312) → Generation Phase prompt load, "Trial 1 only" → "once, before pass 2"; step 4 (314–317) → pass 2 construction, with presentation removed; steps 5–7 (319–355) → Delivery Loop, step 7's record split between the artifact (generation-time fields) and the delivery-time result record (OQ-5) |
| 359–513 | `## Response Protocol`, 8 blocks (MCQ/MSQ/Ordering/Matching × correct/incorrect) | **Rewritten to consume atoms** under REQ-C-010. Each numbered step maps to one artifact field: "state the axis" → `explanation.axis_statement`; "why the correct answer survives" → `explanation.key_survival`; "address each wrong answer individually" → `explanation.distractor_failures[<label>].failure`; "name the orthodox-but-wrong choice" → `.orthodox_but_wrong`; "explain the near-duplicate differentiator" → `.near_duplicate_of` + `explanation.near_duplicate_differentiator`. The *form* of this edit is OQ-4. **Coverage, ordering, and no-nudge discipline are preserved exactly** — the atoms cover every wrong choice by the parent's coverage rule |
| 517–531 | `## Tangent Handling` | **Untouched.** REQ-ORD-F-015 / REQ-MAT-F-015 re-presentation stability becomes structurally guaranteed once the trial is fixed in the artifact — a free strengthening, requiring no edit |
| 533–566 | `## Analysis Phase` | **Untouched**, conditional on OQ-5. Its inputs (`grade`, `gap_summary`) must exist wherever OQ-5 lands them |
| 569–726 | `## Report Format` | **Untouched.** Axis Coverage still reads finally-used axes; Trial Log still reads `probe_target` |
| 728–750 | Error Handling REQ-MCQ-E-001/E-002/E-003 | **Minor rewording**: fallbacks now apply per **slot** in pass 1 rather than per trial. E-001's halt is unchanged, and now fires before any generation rather than before trial 1 |
| 752–757 | REQ-ORD-E-002 | **Untouched** — delivery-time parse validity |
| 758–766 | REQ-ORD-E-003 | **Rewritten** — refit exclusion set gains "assigned to no other slot"; "later trials" → "other slots". Semantics preserved |
| 768–775 | REQ-MAT-E-002 | **Untouched** |
| 777–785 | REQ-MAT-E-003 | **Rewritten** — same change as REQ-ORD-E-003 |

---

## 6. Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-8-1 | **Prompt cadence rules override the Generation Phase** | All four prompts are loaded in full and each says batching is "not optional — structurally required" to avoid; `SKILL.md` says the opposite | The model generates one trial at a time anyway. #8 merges, changes nothing at runtime, and #9/#10 are built on a seam that does not hold | **No.** Blocking — OQ-1. Not fixable inside #8's file scope |
| FM-8-2 | **Pass 2 presents while constructing** | Every prompt's construction sequence ends in a `<step name="output">` that says "Present the question to the learner… Stop. Wait." (MCQ step 9, MSQ step 7, ORD step 8, MAT step 9) | The entire batch is dumped to the learner before trial 1, or generation stalls waiting for a response that will not come. Session destroyed | **No.** The Generation Phase must state that the output step's content is *captured into the artifact, not emitted*. Whether that override is sufficient against the prompt text is OQ-2 |
| FM-8-3 | **Atoms absent at delivery** | #8 merges before #9; the artifact's `explanation` block is unpopulated because no prompt emits it yet | Delivery either halts or silently re-authors rationale live — the reasoning cost never moves, invisibly | **No.** Needs a defined interim behavior — OQ-3 |
| FM-8-4 | Batch artifact rendered to the learner | Generation "produces" an artifact and produced things default to visible | Full answer key plus every rationale leaked before trial 1 | **No.** Parent FM-C-2. New Active Constraint mirroring `probe_target`'s existing never-reveal discipline |
| FM-8-5 | Refit has zero candidate axes | `BATCH_SIZE` ≥ 9 — every axis is assigned to some slot, so "assigned to no other slot" is the empty set | Refit degenerates to 0 attempts rather than 3; slot goes straight to hold-and-reconstruct | **Accepted.** Parent FM-C-4; hold-and-reconstruct is the existing terminal behavior and always succeeds. Reachable at N=9 today |
| FM-8-6 | Axis-uniqueness relaxation fires silently in pass 1 | `select_mcq_axis.py` relaxes to blocking only the last-used axis once all 9 are excluded | Duplicate axes within a batch | **Accepted for #8** — unreachable at `BATCH_SIZE` ≤ 9, and N is capped 1–9 at intake I2. Becomes live at #4's `BATCH_SIZE` = 10. Flagged for #4 |
| FM-8-7 | Distractor softening under frontloading pressure | Generating `BATCH_SIZE` trials in one stretch rewards trials that are quick to construct | Distractors become rejectable on sight — the exact defect `CLAUDE.md` forbids | **No.** Parent FM-C-1. Pass 2 runs the type's internal-validation checklist per slot *before* the slot is written to the artifact; a failing slot is regenerated, never written. Non-delegable review item on the stage-2 diff |
| FM-8-8 | Early report request wastes a batch | Learner asks for the report at trial 2 of 9 | 7 fully constructed slots discarded | **Accepted.** Analysis Phase behavior is unchanged; the Delivery Loop states that unpresented slots are abandoned |
| FM-8-9 | Context compaction drops the in-context artifact mid-session | Long session; artifact holds `BATCH_SIZE` × (stem + choices + key + full atom set) | Remaining trials lose their keys and atoms; delivery cannot grade or explain | **Accepted for #8** — parent FM-C-7 accepts the context-pressure trade, and #7's persistence is the structural fix. Recorded because the failure is silent and worse than FM-C-7's framing suggests. See OQ-9 |
| FM-8-10 | Pass 1 draws types that the I5/I6 gates should have excluded | `--exclude` argument constructed per slot and one slot's construction omits it | An `ordering` slot on a non-procedural concept, which has no valid construction | **No.** The exclude string is a session constant, derived once at intake, and passed identically to every pass-1 slot draw |

---

## 7. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-8-1 | FM-8-1 lands unmitigated: prompt text silently wins over `SKILL.md` | **High** | **High** — nullifies Feature C | OQ-1 must be resolved before stage 2 ships. Verification is behavioral (run a bounded session, confirm generation completes before trial 1 is presented), not textual |
| R-8-2 | #8 and #9 are file-disjoint but semantically coupled: #8 writes the consumer of atoms #9 produces | High | Medium | Field names are fixed by the parent schema and quoted verbatim in both plans. OQ-3 defines the interim window; OQ-6 fixes `probe_target` ownership |
| R-8-3 | #10 re-cuts the Generation Phase to insert the consistency pass | High | Low | Accepted — inherited sequencing. Pass 2 is written as a numbered step list so #10 appends a step rather than restructuring (OQ-7) |
| R-8-4 | #6's split becomes non-mechanical | Medium | Medium | Both new sections begin on `##` headings; no section spans the Generation/Delivery boundary; a fresh seam map is recorded at stage 2 |
| R-8-5 | Response Protocol rewrite drifts from the atoms' shape | Medium | Medium | Each protocol step is mapped to exactly one field (see §5, lines 359–513). Any step with no field is a coverage gap and blocks the PR |
| R-8-6 | Batch context growth (parent FM-C-7 / parent OQ 1) | Medium | Medium | Measure a full-N batch at stage 2 and report the token figure; parent OQ 1 is closed on #8's measurement. Flag if a 10-slot batch exceeds ~15k tokens |
| R-8-7 | Loss of trial-to-trial adaptivity | Low | Low | The prompts claim batching "destroys the ability to adapt subsequent trials"; the orchestrator does not in fact adapt on performance (Active Constraints: "Run all N trials regardless of intermediate performance"), and type/axis are script-randomized. The loss appears nominal — confirmed as OQ-2's companion, recorded so it is a decision and not an oversight |

---

## 8. Open questions

None resolved. Every one is a fork the inputs do not settle; per the issue brief, none is
resolved unilaterally.

| # | Question | Blocker for? |
|---|---|---|
| OQ-1 | All four generation prompts forbid exactly what Feature C requires — `<generation-cadence>` ("Do NOT pre-generate all trials before the learner has responded") at MCQ:36, MSQ:34, ORD:47, MAT:57, and `<trial-sequence-rules><rule id="1-at-a-time">` ("not optional — structurally required") at MCQ:531, MSQ:535, ORD:701, MAT:775. Who removes or amends them — #9, a new issue, or the orchestrator at merge? Neither #8's nor #9's requirement set (REQ-C-005/006/007) mentions them | **Feature C functioning at all** (FM-8-1). Blocks #8's acceptance criteria being verifiable |
| OQ-2 | Each prompt's construction sequence terminates in a `<step name="output">` that presents and waits (MCQ 9, MSQ 7, ORD 8, MAT 9). Does `SKILL.md`'s Generation Phase override it ("capture, do not emit"), or does #9 amend the output steps under REQ-C-007? | FM-8-2; the wording of pass 2's construction step |
| OQ-3 | #8 and #9 merge independently. What does the Delivery Loop do in the window where the artifact has no `explanation` atoms — halt, or author live? Or must #8 and #9 merge together? | Merge order; whether `main` is functional between the two PRs (FM-8-3) |
| OQ-4 | Does #8 rewrite the eight Response Protocol blocks (359–513) in place, or leave them and prepend a single atom-consumption preamble plus a step→field mapping table? The first is ~155 lines rewritten and duplicates the atom names eight times; the second is smaller but leaves eight blocks whose imperative voice ("Explain why…") still reads as author-now | REQ-C-010's blast radius; #6's split of Response Protocol into `mcq-probe-2-delivery` |
| OQ-5 | The parent artifact schema has no `grade` and no `gap_summary` field, but the Analysis Phase and the report's Trial Log and Gap Inventory require both. Does the Delivery Loop write results back into the batch artifact's trial entries (extending the schema, which #7 persists verbatim), or keep a separate delivery-side result record alongside it? | Analysis Phase input; #7's persisted shape; today's Trial Loop step 7 record schema |
| OQ-6 | `probe_target` is an artifact field, so it must be authored at generation time — but REQ-C-005 has the prompts emitting only `explanation` alongside stem/choices/key, and no prompt's output step emits `probe_target` today. Does #8's pass 2 author it in `SKILL.md`, or does #9 add it to the prompt outputs? | Cross-PR consistency; whether §5's Intake/Delivery edits are complete |
| OQ-7 | Does the Generation Phase reserve an explicitly named, numbered step for #10's consistency pass (a documented no-op in #8), or does #10 insert its own? A reserved step reduces merge friction; a no-op step in shipped instructions is the kind of stub `plans/18-plugin-bundle-restructure.md` FM-3 rejected | #10's merge friction |
| OQ-8 | REQ-C-011's announcement wording and cadence: one message at Generation Phase start, or per-slot progress? And may it state the count ("Preparing your 5 trials…") given the standing constraint "Do not display trial numbers, scores, or running totals to the learner during the trial loop" (L79)? | Announcement text; possible amendment of L79's scope |
| OQ-9 | Is silent loss of the in-context artifact to context compaction mid-session (FM-8-9) accepted until #7, or does #8 owe a detection/regeneration behavior? Parent FM-C-7 accepts context *pressure* but does not address artifact *loss* | Nothing in #8 if accepted; informs #7's priority |
| OQ-10 | `trial_index` is "position within the batch"; the report's Trial Log `#` is a session-global trial number. Identical for a bounded one-batch session, divergent under #4. Does #8 record the mapping now, or leave it to #4? | #4 only. Cheap to record now |

---

## 9. Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `mcq-probe/skills/mcq-probe-0-router/SKILL.md` | Modify | Active Constraints rewrite; I2 `BATCH_SIZE`; I5/I6 cross-reference repoint; Trial Loop (236–358) → `## Generation Phase` + `## Delivery Loop`; batch-artifact schema block; Response Protocol atom consumption; Error Handling E-002/E-003 and ORD/MAT E-003 rewording | REQ-C-001/002/003/004/010/011 |
| `plans/8-batch-type-axis-sequencing.md` | Create | This document | Repo precedent (#2, #3, #5, #18) |
| `mcq-probe/skills/mcq-probe-0-router/prompts/*.md` | **None** | — | #9's scope. Touching them conflicts with the parallel worktree |
| `mcq-probe/.claude-plugin/plugin.json` | **None** | — | Version bump is the orchestrator's at merge, to avoid a #8/#9 conflict. Note: without it the installed plugin serves stale cached content (#18 OQ-1) |
| `mcq-probe/skills/mcq-probe-0-router/scripts/*.py` | **None** | — | Both selectors are call-site agnostic; the two-pass draw changes only who calls them and with what `--exclude` |

---

## 10. Implementation order

1. **Resolve OQ-1 through OQ-6 with the orchestrator.** OQ-1 and OQ-3 are hard blockers — an
   implementation that is textually correct and behaviorally inert is worse than none, because
   #9 and #10 build on it.
2. Rewrite **Active Constraints** (67–81): retime the prompt-load, type-draw, axis-draw and refit
   bullets; delete L76; retime the probe-target bullet; add the never-render and announcement
   bullets.
3. Add the **batch artifact schema** block to `SKILL.md`, field-for-field from the parent plan,
   with the never-render statement attached.
4. Write **`## Generation Phase`**: announcement → `BATCH_SIZE = N` → prompt load (halt on
   unreadable, REQ-MCQ-E-001) → pass 1 (per-slot type draw with the I5/I6 exclude string, per-slot
   axis draw with the assigned-axes exclude list) → pass 2 (per-slot construction, ordering/matching
   refit, per-slot internal-validation, `probe_target`, write slot to artifact).
5. Write **`## Delivery Loop`**: per trial, present from the artifact → wait → parse → grade
   against the stored `key` → Response Protocol → record the result. State explicitly: authors no
   new rationale, reads no generation prompt, abandons unpresented slots on an early report request.
6. Repoint the **I5/I6 cross-references** (L208, L226) and add `BATCH_SIZE` at I2.
7. Rework the **Response Protocol** per the OQ-4 resolution, verifying each numbered step maps to
   exactly one artifact field.
8. Reword **Error Handling** REQ-MCQ-E-002/E-003 (per slot) and REQ-ORD-E-003 / REQ-MAT-E-003
   (pass-2 refit, "assigned to no other slot", "other slots" not "later trials").
9. **Verification gate — behavioral, not textual.** Run a bounded session end to end and confirm:
   (a) nothing is presented until the whole batch is generated; (b) the announcement fires; (c) no
   artifact content leaks; (d) axes are unique across slots and refit rejections did not consume
   any; (e) the breakdown for a wrong answer covers every distractor. This is the FM-8-1 / FM-8-2
   check and it cannot be satisfied by reading the diff.
10. **Measure** the full-batch artifact's token cost and report it — this closes parent open
    question 1 (R-8-6).
11. Record a fresh **seam map** (post-edit line ranges for router / generation / delivery /
    analysis) for #6.
