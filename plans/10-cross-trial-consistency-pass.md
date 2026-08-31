# Plan — C3: Cross-trial consistency pass (#10)

**Status:** Stage 1 — plan authored, **not implemented**. 14 open questions block stage 2 (§8).
**Parent plan:** `plans/5-frontload-question-generation.md`, **as amended** — the Amendments
section wins on conflict. Its artifact schema, two-pass draw, and REQ-C-001…015 are binding and
are not revisited here.
**Branch:** `feat/10-cross-trial-consistency`
**Target file:** `mcq-probe/skills/mcq-probe-0-router/SKILL.md` (single file; the split is #6).
**Requirements owned:** REQ-C-008, REQ-C-009. **Failure mode owned:** FM-C-6.
**Siblings:** #8 (Generation Phase / Delivery Loop — landed) · #9 (explanation baking — landed).
This is the last open sub-issue of Feature C (#5).

---

## 0. Readback — the defining interpretation

1. **This is a second gate, never a substitute.** Each prompt's `internal-validation` checklist
   runs per slot inside G5 rule 3, *before* the slot is written. G6 runs after every slot is
   written, over the finalized set, and checks a property no per-slot gate can see. G5 rule 3 is
   untouched.
2. **The pass is a rejection mechanism, and rejection creates pressure.** Regenerating for
   distinctness rewards trials that are easy to make *different* over trials that are hard to
   answer. A regenerated slot clears the identical `internal-validation` checklist, with **no
   allowance made because it is a retry**. FM-10-1 carries this; it is non-delegable.
3. **Three checks are named; none is defined.** REQ-C-008 names "no repeated scenario", "no
   clustered correct-answer position", and "domain-anchor variety". Each of the three needs an
   operational definition that no input supplies, and one of the three (domain) has no artifact
   field and no supporting rule anywhere in the prompts. §8 is the deliverable of this stage.

---

## 1. Background / context

### Key globals

| Global | Value before #10 | Value after #10 |
|---|---|---|
| Cross-trial checking | None. Nothing compares a finalized batch against itself | `G6` over the finalized batch, before delivery |
| Scenario-freshness enforcement | Per-slot `internal-validation` item only — MCQ:283, MSQ:282, ORD:392, MAT:437 | Per-slot item **plus** a batch-level re-check (scope: OQ-1, OQ-3) |
| Correct-answer position across trials | Construction-step instruction only. **No `internal-validation` item in any of the four prompts** — verified, §3 | Batch-level check (definition: OQ-4…OQ-7) |
| Domain anchor | `DOMAIN`, a session constant set at intake I3; `<domain-anchoring>` directs every trial to it | Blocked on OQ-8 — no artifact field, and no cross-trial variety rule exists to inherit |
| Regeneration on a cross-trial defect | n/a | Offending slot only, ≤3 attempts, then accept and log — REQ-C-009, FM-C-6 |
| Generation Phase steps | G1 announce · G2 batch size · G3 prompt load · G4 pass 1 · G5 pass 2 | + **G6 consistency pass** |
| Batch axis uniqueness | Guaranteed by G4 pass 1 + REQ-C-004 | Must survive regeneration — OQ-10 |
| `SKILL.md` size | 953 lines / **10,929 tokens** (measured, `token-counter`) | +G6; measure at stage 2, do not estimate |
| `plugin.json` version | `1.1.0` | `1.2.0` — required for cache re-sync |
| Type draw | Uniform, independent, with replacement over the non-excluded types (`select_question_type.py`) | Unchanged — no script edit |

### Seam verification (verified against the live file, not inherited)

`mcq-probe/skills/mcq-probe-0-router/SKILL.md`, 953 lines:

| Line | Content |
|---|---|
| 310 | `## Generation Phase` |
| 378 | `### G5. Pass 2 — content, slot by slot` |
| 424 | `**Write the slot** into the batch artifact, with `grade` and `gap_summary` null.` |
| 426 | `When every slot is written, the batch is complete. Proceed to the Delivery Loop.` |
| 428 | `---` |
| 430 | `## Delivery Loop` |

The insertion point named in the brief is confirmed: a new `### G6` between line 426 and the
line-428 rule. Line 426 is the sentence that must be repointed — it currently hands control
straight to the Delivery Loop and would otherwise route around G6.

Per plan 8's as-built seam map, the Generation Phase block is lines 243–429. G6 lands inside it,
so #6's split stays a cut at a `##` boundary.

### Pipeline after this change

Intake I1–I6 → Generation Phase (**G1** announce → **G2** `BATCH_SIZE = N` → **G3** prompt load →
**G4** pass 1: type+axis for every slot → **G5** pass 2: construct, validate, write each slot →
**G6** consistency pass over the finalized batch, regenerating offending slots and re-running) →
Delivery Loop D1–D5 → Analysis Phase → Report.

---

## 2. Problem statement

Before #8, each trial was generated blind to the others: `SCRIPT_AXIS --exclude` saw only
*completed* trials, and no record of an unfinished trial existed to compare against. Every
cross-trial quality rule in the four prompts was therefore an instruction the generator could
only honor from memory, and no gate anywhere could verify it. #8 made the whole batch exist
before delivery. This issue is the first consumer of that fact.

Three concrete gaps, each verified in §3:

1. **Every cross-trial position rule in all four prompts is ungated.** MCQ step 7, MSQ step 5 and
   `<answer-position>`, `<label-and-shuffle>` in ORDERING and MATCHING all instruct the generator
   to vary placement *across trials*. Not one of them has a corresponding `internal-validation`
   checklist item in any of the four files. The two label items that *are* gated (ORD:389,
   MAT:431) are **within**-trial properties — "not in label order", "not the identity diagonal" —
   and say nothing about the batch.

2. **Scenario non-reuse is gated per slot, but only pairwise-backwards.** Each prompt carries an
   `internal-validation` item ("This scenario was not used in any prior trial or exchange this
   session") and a `<trial-sequence-rules><rule id="no-question-reuse">`. Both are written for
   the sequential case: slot *k* judges itself against slots 0…*k*−1 from memory, under
   construction pressure, with no committed record. Whether G6's re-check is redundancy or a
   genuinely different aggregate test is OQ-3.

3. **Domain-anchor variety has no basis to build on.** `<domain-anchoring>` (MCQ:253, MSQ:252,
   ORD:351, MAT:384) tells every trial to use the *same* `DOMAIN` from intake I3. The only
   "change the domain" instruction in the corpus is session-level and fires on a re-run of an
   exhausted concept (MCQ:1036, MSQ:1113, MAT:1916 — "Change the domain anchor for the **new
   session**"). REQ-C-008's third check has no rule to inherit, no artifact field to read, and
   a plausible direct conflict with an explicit learner preference. OQ-8.

---

## 3. What the pass can check today — verified per-type inventory

Load-bearing evidence for §2 and for the open questions. Every citation checked in the working
tree at `mcq-probe/skills/mcq-probe-0-router/prompts/`.

| Type | `key` shape | Within-trial placement rule | Gated? | Cross-trial placement rule | Gated? | Scenario item |
|---|---|---|---|---|---|---|
| mcq | one label, A–D | step 7 `position-assignment` | No | *"Vary the position of the correct answer across the trials"* (step 7, MCQ:653) | **No** | MCQ:283 |
| msq | set ⊆ A–E, size 1–4 | step 5 `position-assignment`; `<answer-position>` MSQ:378 | No | *"Vary their distribution across the trials in this session"* (step 5, MSQ:655) | **No** | MSQ:282 |
| ordering | ordered list over pool A–H, P = K+D, K∈[3,5], D∈[1,3] | *"correct sequence is not in label order"* | **Yes** ORD:389 | *"Vary the shuffle and the distribution of correct-vs-distractor labels across trials … do not let distractors cluster predictably at the end of the alphabet"* (`<label-and-shuffle>`, ORD:525) | **No** | ORD:392 |
| matching | injective 1…n → A…m, n∈[3,7], m∈[4,10], D∈[1,3] | *"correct pairing is NOT the identity diagonal"* | **Yes** MAT:431 | *"Vary the shuffle across trials … do not cluster distractor letters at the end of the alphabet"* (`<label-and-shuffle>`, MAT:585) | **No** | MAT:437 |

**The non-reuse unit is already type-specific, and already wider than "scenario"** —
`<rule id="no-question-reuse">`:

| File:line | Unit forbidden from reuse within a session |
|---|---|
| MCQ:567 | question, **scenario**, or **answer choice** |
| MSQ:571 | question, **scenario**, or **answer choice** |
| ORD:743 | **task scenario**, **step**, or **distractor** |
| MAT:824 | **case set**, **prompt**, or **response** |

REQ-C-008 says "no repeated *scenario*", which is narrower than all four. Nothing settles which
reading G6 enforces (OQ-1, OQ-2).

### Clustering figures — why the threshold is a decision, not a default

Exact enumeration over all 4^m assignments of the correct label for *m* MCQ slots, uniform:

| m (MCQ slots) | Pigeonhole floor ⌈m/4⌉ | E[max label count] | P(some label ≥ 3) |
|---|---|---|---|
| 3 | 1 | 1.69 | 0.062 |
| 4 | 1 | 2.12 | 0.203 |
| 5 | 2 | 2.48 | 0.414 |
| 7 | 2 | 3.19 | 0.846 |
| 9 | 3 | 3.87 | **1.000** |

Two consequences that any threshold decision must respect:

- **A "no label appears 3+ times" rule is unsatisfiable at m = 9.** The pigeonhole floor is 3, so
  every all-MCQ 9-trial batch would regenerate to the FM-C-6 cap on every slot and then be
  accepted anyway — 27 wasted constructions, zero effect. FM-10-4.
- **At m = 5 that same rule fires on 41.4% of batches.** Regeneration stops being exceptional and
  becomes the normal path, which is precisely when FM-10-1's pressure turns continuous. R-10-2.

Type draw is uniform and independent per slot, so *m* is itself random: E[m] = N/4 with all four
types available, N/2 when both the I5 and I6 gates fire. Whether the threshold scales on N or on
the per-type sub-count *m* is OQ-6/OQ-7.

---

## 4. Design decisions

Every row is inherited — from the parent plan, issue #10, the coordinator's brief, or the live
file. **Nothing is originated here.** Every fork the inputs do not settle is in §8 instead.

| Decision | Resolution | Source |
|---|---|---|
| Where the pass runs | A new `### G6` in `## Generation Phase`, after G5 writes the last slot, before control passes to the Delivery Loop | Issue #10; brief; verified at `SKILL.md`:426/428/430 |
| What G6 sees | The **finalized** batch — every slot written, validated, and carrying its atoms | REQ-C-008 |
| Relationship to per-slot validation | **Additive second gate.** G5 rule 3 stays the primary gate and is untouched; G6 never substitutes for it, never reorders around it, and never relaxes it | Brief non-goals; parent FM-C-1; `CLAUDE.md` |
| Regeneration granularity | The **offending trial only**, never the batch | REQ-C-009; parent §Design decisions, "Consistency-pass granularity" |
| After a regeneration | **Re-run the pass** over the batch | REQ-C-009 |
| Regeneration cap | **3 attempts per slot**, then accept the trial and log internally. Mirrors the existing 3-attempt refit convention (REQ-ORD-E-003 / REQ-MAT-E-003) | FM-C-6 |
| Bar for a regenerated slot | Identical. It clears the same `internal-validation` checklist and the same `explanation-baking` emission gate as an original. **No allowance for being a retry** | `CLAUDE.md`; parent FM-C-1; brief |
| Prompt access during regeneration | No reload. All four prompts are held in context from G3 for the whole session, and REQ-C-010's no-prompt-reading constraint binds **delivery**, not generation | `SKILL.md` G3; Active Constraints; REQ-C-010 |
| Learner-visible output | **None.** G6 emits nothing. The G1 announcement already fired and states no count; the batch artifact and every finding over it are internal | REQ-C-011; `SKILL.md` Batch Artifact never-render; FM-C-2 |
| Artifact field names | Binding. #10 adds no field without coordinator sign-off — OQ-8 and OQ-12 both need one and are therefore blocked, not resolved | Parent §Artifact schema |
| G6's internal form | A numbered step list, so #4 and #7 append rather than restructure | Plan 8 §R-8-3 / OQ-7 precedent; `plans/18-…` FM-3 |
| Citation discipline in new text | Refer to prompt elements **by name** (`internal-validation`, `explanation-baking`, `<label-and-shuffle>`, `<rule id="no-question-reuse">`) — never by step number or line number, which #9 already shifted and #24 will shift again | Plan 8 FM-8-2 precedent; #24 |
| Files under `prompts/` | **Not touched.** #9 just landed there; #24 restructures them | Brief; #24 |
| Version bump | `mcq-probe/.claude-plugin/plugin.json` `1.1.0` → `1.2.0`, in stage 2. #22/#23 omitted it only to avoid a parallel-worktree conflict | Brief; parent §Files touched |
| Split-friendliness | G6 lands inside the Generation Phase block (`SKILL.md` 243–429) — no section spans the Generation/Delivery boundary | Plan 8 §5 as-built seam map |

---

## 5. Requirements

Owned by this issue, verbatim from the parent plan.

| ID | Requirement | Scope |
|---|---|---|
| REQ-C-008 | A consistency pass runs over the finalized batch: no repeated scenario, no clustered correct-answer position, domain-anchor variety | `SKILL.md` — new `### G6`; one Active Constraints bullet |
| REQ-C-009 | A consistency failure regenerates only the offending trial, then re-runs the pass | `SKILL.md` — G6 step list; possibly a new Error Handling entry for the cap |

**Derived, from FM-C-6:** regeneration is capped at 3 attempts per slot; on exhaustion the trial
is accepted and the waiver logged internally. Where the log lives is OQ-12.

**Non-goals, explicit.** No edit to any file under `prompts/` (#9 landed there; #24 restructures).
No on-disk persistence (#7). No file split (#6). No endless-mode windowing (#4). No change to
`select_question_type.py` or `select_mcq_axis.py`. **No change to what a distractor must satisfy
— no construction rule, viability rule, pool/grid law, required construct, banned-language list,
or `internal-validation` item is weakened, reordered around, or made conditional.**

---

## 6. Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| **FM-10-1** | **Distractor quality traded for distinctness under regeneration pressure** | G6 rejects a slot for a cross-trial reason. The cheapest way to make a trial *different* is to make it *easier* — a further-flung scenario with looser distractors clears the collision faster than a tight one | Distractors become rejectable on surface reading. The premise of the skill collapses, and it collapses **invisibly**, because the trial that ships is the one that passed a distinctness check, not a difficulty check | **No.** The regenerated slot re-runs the type's full construction sequence, `internal-validation` checklist, and `explanation-baking` emission gate — identical bar, no retry allowance. `viability_account` is the load-bearing guard (#9 Gate 2): a weakened distractor has **no viability account to write**, so it cannot be emitted. G6 text must state that a collision is fixed by re-authoring the scenario, never by loosening a choice. **Non-delegable review item on the stage-2 diff.** |
| FM-10-2 | Cap exhaustion silently ships a colliding trial | 3 regenerations still collide | A repeated scenario or a clustered key reaches the learner with no signal | **Accepted** — inherited from FM-C-6. Logged internally; where, is OQ-12 |
| FM-10-3 | Regeneration churn — fixing slot *i* creates a collision at slot *j* | Any check whose violation is a relation over slots; a fresh scenario can land on another slot's | Work bounded per slot but not per batch: worst case 3 × `BATCH_SIZE` = 27 constructions at N = 9 | **Partly.** Per-slot cap is FM-C-6 and holds. A batch-level cap is not specified — OQ-11 |
| FM-10-4 | Threshold set below the pigeonhole floor | A "no label 3+ times" rule at m = 9 MCQ slots, where ⌈9/4⌉ = 3 | Every slot burns 3 regenerations, is accepted anyway, and the batch takes ~4× as long for zero effect | **No.** Any threshold must be ≥ ⌈m/4⌉ for the relevant label alphabet. §3 figures; blocked on OQ-6 |
| FM-10-5 | Regeneration re-draws the slot's axis | Regeneration re-enters G5's construction path, which contains an axis-refit step | Batch axis-uniqueness (REQ-C-002/004) breaks, and the report's Axis Coverage silently misstates what was tested | **No.** Must be settled before stage 2 — OQ-10 |
| FM-10-6 | G6 read as making G5 rule 3 optional | Two gates exist; the later one looks authoritative | Per-slot `internal-validation` is skipped or softened. This is the doctrine failure `CLAUDE.md` names | **No.** G6 text states explicitly that it runs strictly after, and adds to, the per-slot gate. G5 rule 3 is not edited |
| FM-10-7 | Regenerated slot ships without atoms | Regeneration is implemented as a patch of the stem rather than a re-run of the construction sequence | Delivery falls back to authoring rationale live (REQ-C-015) and the reasoning cost silently returns — parent FM-C-3 | **No.** Regeneration re-runs the full sequence through `explanation-baking`; a slot is rewritten whole, never edited in place |
| FM-10-8 | G6 findings rendered to the learner | A "pass" that finds problems defaults to reporting them | A collision report naming stems and keys leaks the answer key before trial 1 | **No.** Parent FM-C-2; `SKILL.md`'s never-render constraint already covers the artifact, and G6 adds no learner-visible output |
| FM-10-9 | Latency compounds past FM-C-5's expectation | Up to 27 extra constructions at N = 9, on top of the 9 originals | The learner waits ~4× the already-accepted batch latency, with a single announcement made long before | **Accepted, measure.** No new announcement — the G1 line states no count and stays true. Stage 2 measures a worst-case batch |
| FM-10-10 | The domain check overrides the learner's intake choice | The learner picked "Aviation" at I3; a variety check demands the batch not be uniformly aviation | The generator drifts off an explicitly chosen domain, contradicting `<domain-anchoring>` in all four prompts | **No.** Blocked on OQ-8. A check that overrides an explicit learner preference must not ship |

---

## 7. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-10-1 | A stage-2 implementer closes an open question by picking a reasonable default | **Medium** | **High** — three of the fourteen change what ships to the learner | §8 is the stage-1 deliverable. Stage 2 does not begin until OQ-1, OQ-2, OQ-4…OQ-8, OQ-10, OQ-12 and OQ-13 are resolved by the coordinator |
| R-10-2 | A tight threshold makes regeneration the normal path, not the exception | Medium | **High** | Measured: at m = 5, P(max ≥ 3) = 0.414. FM-10-1's pressure is proportional to how often G6 fires — the threshold decision *is* a difficulty decision, and OQ-6 must be answered with the §3 figures in hand |
| R-10-3 | Schema drift — a `domain_anchor` field or a waiver field breaks #7's persistence shape | Medium | Medium | Parent declares field names binding. Both needs (OQ-8, OQ-12) are raised, not resolved; if a field is added it is added to the parent schema first |
| R-10-4 | New text cites prompt step or line numbers, which #9 already shifted and #24 will shift again | Low | Medium | Citation-by-name discipline is a §4 decision. Plan 8 FM-8-2 set the precedent for exactly this reason |
| R-10-5 | `SKILL.md` on-invoke cost grows; the file is read on every invocation | Realized | Low | Baseline measured: 10,929 tokens. Stage 2 measures the delta with `token-counter`, never estimates |
| R-10-6 | #6's split becomes non-mechanical | Low | Low | G6 is a `###` inside the existing Generation Phase `##` block; no section spans the phase boundary |
| R-10-7 | G6 is written as prose judgment and becomes unverifiable, repeating the exact defect §2 identifies in the prompts' cross-trial rules | Medium | Medium | Each check must land as a stated, checkable predicate over artifact fields. A check that cannot be stated as a predicate is an open question, not an implementation detail |

---

## 8. Open questions

**None are resolved.** Every one is a fork the inputs do not settle. Nine are hard blockers.

| # | Question | Blocker for? |
|---|---|---|
| OQ-1 | **"Repeated scenario" has no operational definition anywhere.** Two trials on one concept necessarily share the concept and, under a concrete I3 choice, the domain. `<scenario-freshness>` says "substantively distinct"; `<rule id="no-question-reuse">` forbids reuse of a wider, type-specific unit set (§3). Which does G6 enforce — the narrow "scenario" of REQ-C-008, the prompts' full non-reuse unit, or a new operational test (e.g. same setting + same actors + same triggering condition)? | G6 check 1. Stage 2 cannot write the check |
| OQ-2 | **Which artifact field is compared, and it differs by type.** The artifact stores `stem`; it has no `scenario` field. The prompts' unit is the *scenario* (MCQ/MSQ), the *task scenario* (ORD), and the *case set* (MAT) — none of which is the whole stem. Is the comparison over `stem`, over `probe_target`, or over something not currently recorded? | G6 check 1 |
| OQ-3 | **Is check 1 redundant with the per-slot gate?** Each prompt's `internal-validation` already carries "This scenario was not used in any prior trial or exchange this session", and under slot-order construction that is pairwise-backwards over the whole batch by induction. Is G6's scenario check intended as (a) deliberate redundancy against a judgment made under construction pressure, or (b) a genuinely different *aggregate* test — e.g. three trials that are each pairwise-fresh but collectively monotone? The two produce different checks and different firing rates | G6 check 1's framing; whether it can ever fire |
| OQ-4 | **"Correct-answer letter/position" does not map onto Ordering or Matching.** Ordering's answer is a sequence; Matching's is an injective map. Neither has a "correct-answer letter". `<label-and-shuffle>` supplies a *candidate* cross-trial analogue in both — distractor-label placement ("do not cluster distractor letters at the end of the alphabet") — but that is not the correct answer's position. Does check 2 run on ORD/MAT slots at all, and if so against which property? | G6 check 2 on ORD and MAT slots |
| OQ-5 | **MSQ's analogue is ambiguous.** `key` is a *set* of 1–4 labels from A–E, so there is no single position. Candidates: per-label appearance frequency across the batch's key sets; key **size** clustering (four trials all keyed 2-of-5 is a real pattern leak, and is named nowhere); the `<answer-position>` "top or bottom" framing; or all three | G6 check 2 on MSQ slots |
| OQ-6 | **No clustering threshold exists.** All four prompt rules are qualitative — "do not consistently place", "do not cluster predictably". A batch check needs a decision rule. §3 shows the choice is consequential and constrained: any threshold must be ≥ the pigeonhole floor ⌈m/4⌉ or it is unsatisfiable, and a threshold of 3 fires on 41.4% of 5-slot MCQ batches. What is the rule, per type? | G6 check 2, all types. **Also gates R-10-2** |
| OQ-7 | **Whole batch, or per-type sub-batches?** A 9-trial batch holds on average 2.25 MCQ slots. A letter-frequency check over "all slots" is not well-defined across four different label alphabets; a per-type check often runs on 1–3 slots, where clustering is close to meaningless (P(max ≥ 3) = 0.062 at m = 3). Which is it, and is there a minimum sub-count below which check 2 is skipped? | G6 check 2 |
| OQ-8 | **"Domain-anchor variety" has no field, no rule, and a probable conflict.** (a) The artifact schema carries **no** domain-anchor field — confirmed against `SKILL.md`'s Batch Artifact block. (b) `DOMAIN` is a session constant from intake I3, and `<domain-anchoring>` tells every trial to use it — the corpus pushes toward *sameness*, and the only "change the domain anchor" instruction is session-level, for re-runs (MCQ:1036, MSQ:1113, MAT:1916). (c) When the learner picks a concrete domain, "variety" either contradicts I3 or must mean **operational-setting** variety *within* it — the reading MSQ:1113 hints at ("only the operational setting changes") and that I3's own option text enumerates ("NTSB causal chains, flight envelope, MRO operations"). (d) A Matching trial's prompts may **span several domains by design** (MAT:1285), so a matching slot has no single anchor. Options, none chosen: add a `domain_anchor` field (parent schema change); derive the anchor from `stem` at check time with no new field; scope the check to `DOMAIN = "No preference"` sessions only; or drop check 3 | **G6 check 3 entirely.** Highest-value question here |
| OQ-9 | **Which slot is "the offending trial"?** REQ-C-009 says "the offending trial", singular, but a scenario repeat is a symmetric relation over two slots and a letter cluster is a property of a set of 3+. Does the later `trial_index` regenerate on seniority? For a cluster of *k*, do *k*−1 slots regenerate, or one, or the minimum needed to clear the threshold? | REQ-C-009 implementation |
| OQ-10 | **Does regeneration hold `question_type` and `axis`?** Holding both is the conservative reading and mirrors G5's hold-and-reconstruct — but a scenario collision may be *caused* by the type+axis pairing, making 3 held attempts futile. Re-drawing the axis would break batch axis-uniqueness (REQ-C-002/004) and silently change the report's Axis Coverage. Also unspecified: what happens to `axis_rejected` on a regenerated slot | REQ-C-009 + REQ-C-002/004 interaction; **FM-10-5** |
| OQ-11 | **Is there a batch-level regeneration cap?** FM-C-6 caps per slot at 3, bounding worst-case work at 3 × `BATCH_SIZE` = 27 constructions at N = 9. Fixing one slot can collide with another, so the pass can re-run many times within that bound. Is the per-slot cap the only cap, or is a batch-level ceiling wanted? | FM-C-6 completeness; FM-10-3 |
| OQ-12 | **"Accept the trial and log internally" — log where?** The artifact has no field for a waived collision, and the report has no section for one. Adding a field (e.g. `consistency_waived`) is a parent-schema change and affects what #7 persists. Alternatively the log is transient reasoning with no record — in which case the waiver is invisible to #7 and to the report | FM-C-6 implementation; #7's persistence shape |
| OQ-13 | **Parent-plan incoherence: is atom coverage a fourth G6 check?** Parent FM-C-3's disposition reads "REQ-C-006 coverage rule, **checked in the consistency pass**", and #9's FM-9-3 reads "`<emission-gate>` blocks output; **#10 re-checks over the batch**". Both assign a fourth check to #10 that **REQ-C-008 does not carry**. Worse, it conflicts with REQ-C-015: in the window where #8 has merged and #9 has not, every slot legitimately lacks atoms, and a coverage check would fail all of them and burn the cap on each. Is coverage a G6 check, and if so what does it do when atoms are absent by design? | G6 scope. Two plan rows currently promise a check REQ-C-008 does not authorize |
| OQ-14 | **Does check 1's scope include non-trial exchanges?** The prompts' wording is "any prior trial **or exchange** in this session" — which reaches tangent-handling conversation and the intake exchange, neither of which is in the batch artifact. Does G6 compare slots against slots only, or is the exchange half simply out of reach for a batch-level check? | G6 check 1 scope |

---

## 9. Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `mcq-probe/skills/mcq-probe-0-router/SKILL.md` | Modify | New `### G6` after G5 (insert between lines 426 and 428); repoint line 426's "Proceed to the Delivery Loop" through G6; one Active Constraints bullet stating the pass and the 3-attempt cap; an Error Handling entry for cap exhaustion if OQ-12 lands there | REQ-C-008, REQ-C-009, FM-C-6 |
| `mcq-probe/.claude-plugin/plugin.json` | Modify | `version` `1.1.0` → `1.2.0` | The plugin installs as a version-keyed cache copy and will not re-sync without a bump (#18 OQ-1) |
| `plans/10-cross-trial-consistency-pass.md` | Create | This document | Repo precedent (#2, #3, #5, #8, #9, #18) |
| `mcq-probe/skills/mcq-probe-0-router/prompts/*.md` | **None** | — | #9 just landed there; #24 restructures. Out of scope by directive |
| `mcq-probe/skills/mcq-probe-0-router/scripts/*.py` | **None** | — | G6 adds no draw and changes no selector behavior |

---

## 10. Implementation order

Stage 1 ends at step 1. **Steps 2–9 do not begin without an explicit execute signal.**

1. **Resolve §8 with the coordinator.** Hard blockers: OQ-1, OQ-2, OQ-4, OQ-5, OQ-6, OQ-7, OQ-8,
   OQ-10, OQ-13. OQ-3, OQ-9, OQ-11, OQ-12 and OQ-14 shape the text but do not prevent it.
   Amendments to the parent plan (schema field, or REQ-C-008 scope) land there first, not here.
2. Write `### G6` as a numbered step list: the enumerated checks, the per-check predicate, the
   offending-slot rule, regeneration, the 3-attempt cap, the accept-and-log terminal, and the
   re-run. Prompt elements cited **by name only**.
3. Repoint `SKILL.md`:426 so control reaches the Delivery Loop through G6, not around it.
4. Add the Active Constraints bullet, and the Error Handling entry if OQ-12 requires one.
5. Bump `plugin.json` to `1.2.0`.
6. **Gate 1 — the anti-softening diff gate.** Verify mechanically that no `internal-validation`
   item, viability rule, pool/grid law, required construct, or banned-language list changed —
   `git diff` must show zero bytes altered under `prompts/`, and no edit to G5 rule 3. FM-10-1,
   FM-10-6. **Non-delegable.**
7. **Gate 2 — behavioral, post-merge.** Re-sync the plugin cache, restart, run a bounded session
   at N = 5 and confirm: (a) nothing is presented until G6 completes; (b) G6 emits nothing to the
   learner; (c) a regenerated slot carries a full `explanation` block; (d) axes stay unique
   across slots after any regeneration; (e) no artifact content leaks. Cannot be satisfied by
   reading the diff.
8. **Measure.** `SKILL.md` delta against the 10,929-token baseline with `token-counter`, and the
   worst-case regeneration latency at N = 9 (FM-10-9). Figures, never estimates.
9. Report the measurements and any check that fired in the dry run, with its threshold.
