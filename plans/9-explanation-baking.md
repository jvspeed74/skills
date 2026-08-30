# Plan: Explanation-baking in generation output (#9 — Feature C / C2)

**Status:** Planned — stage 1 (plan only). Not implemented.
**Date:** 2026-08-30
**Branch:** `feat/9-explanation-baking`
**Parent plan:** `plans/5-frontload-question-generation.md` (approved; its Artifact schema is binding)
**Requirements owned:** REQ-C-005, REQ-C-006, REQ-C-007
**Sibling issues:** #8 (SKILL.md Generation Phase / Delivery Loop, parallel) · #10 (consistency pass, gated on both)

---

## Readback — the defining interpretation

Three reads. If any is wrong, large parts of this plan change. All three are surfaced
again in Open questions where they are not settled by the parent plan.

1. **The atom shape is fixed, the mapping is not.** The parent plan's `explanation`
   block is binding down to field names. What is *not* fixed is how six fields absorb
   four different choice structures — one of which (`key_survival: str`) must carry
   between 1 and 7 distinct mechanism statements depending on type. Mapping is this
   issue's actual work.
2. **Baking is a recording operation, not an authoring operation.** Every atom field
   corresponds to a determination the existing internal-validation checklist already
   forces the generator to make before output. #9 persists those determinations; it
   does not ask for new judgment. This is the whole answer to FM-C-1 and is worked in
   full in *Additivity* below.
3. **#9 changes generation output, not generation.** No construction rule, viability
   rule, pool/grid law, required construct, banned-language list, or checklist item is
   weakened, reordered around, or made conditional. Every existing check stays where it
   is and keeps its current force.

---

## Background / context

### Key globals

| Global | Current | After #9 |
|---|---|---|
| Generation prompts | 4 XML files, loaded once on Trial 1, retained for the session | Unchanged in count and load discipline |
| Prompt output | The trial, rendered to the learner (MCQ step 9, MSQ step 7, ORD step 8, MAT step 9, all named `output`) | Trial record **plus** `explanation` atoms, emitted internally |
| Rationale authoring | At delivery, after the learner answers, per Response Protocol | At generation, per REQ-C-005 |
| Rationale coverage | Whatever delivery produces live | Every wrong choice, enforced pre-output — REQ-C-006 |
| Atom visibility | n/a | Internal only, never rendered — REQ-C-007, same discipline as `probe_target` |
| Internal-validation checklists | MCQ 14 checks, MSQ 13, ORD 17, MAT 17 | Unchanged, plus appended atom-coverage checks |
| Construction sequence length | MCQ 9 steps, MSQ 7, ORD 8, MAT 9 | +1 step each, inserted before `output` |

### Measured sizes (not estimated)

| Prompt | Lines | Chars | ~Tokens (chars/4) | Construction steps | Checklist items |
|---|---|---|---|---|---|
| `MCQ_GENERATION_PROMPT.md` | 913 | 43,523 | ~10.9k | 9 | 14 |
| `MSQ_GENERATION_PROMPT.md` | 949 | 45,243 | ~11.3k | 7 | 13 |
| `ORDERING_GENERATION_PROMPT.md` | 1,215 | 60,258 | ~15.1k | 8 | 17 |
| `MATCHING_GENERATION_PROMPT.md` | 1,714 | 86,644 | ~21.7k | 9 | 17 |
| **Total** | **4,791** | **235,668** | **~58.9k** | — | **61** |

The parent plan cites "~47k of generation prompts." That figure is stale post-Matching;
the measured total is ~58.9k, closer to the 56,540 per-session read volume the parent
also cites. Flagged, not corrected here — the parent plan is not this issue's file.

### Pipeline

Today: `SKILL.md`'s Trial Loop draws a type (step 1), draws an axis (step 2), loads the
four prompts on Trial 1 (step 3), constructs and presents one trial (steps 4–5), waits,
then applies the Response Protocol to author the breakdown live (step 6). The four
prompts each end their construction sequence with an `output` step that renders the
trial to the learner and stops.

After Feature C: #8 splits that loop into a Generation Phase (all `BATCH_SIZE` trials
produced up front, into an in-context batch artifact) and a Delivery Loop (present,
parse, grade against the stored key, assemble the breakdown from stored atoms —
REQ-C-010). #9 is what makes the second half of REQ-C-010 possible: the atoms the
Delivery Loop assembles from have to exist, and they have to be complete, or delivery
silently authors the missing rationale live and the reasoning cost never moved
(FM-C-3).

### What the atoms must reconstruct

`SKILL.md`'s Response Protocol (lines 359–513), and the equivalent
`<correct-response-protocol>` / `<incorrect-response-protocol>` in each prompt. Two
properties of those protocols drive the whole design:

- **The correct and incorrect branches carry identical content.** Both state the axis,
  both explain why the key survives, both address every wrong choice individually, both
  resolve the near-duplicate. They differ in ordering and framing only — the incorrect
  branch leads with the learner's specific failure and states the key before explaining
  it. Atoms serve both branches with no duplication. This is why the parent plan chose
  atoms over prose (Design decisions, "Explanation payload shape").
- **The incorrect branch varies by which wrong choice was taken.** Every type's
  incorrect protocol opens on the learner's own error before the general explanation.
  Generation does not know what the learner will pick. Therefore `distractor_failures`
  must cover **every** wrong choice, not the interesting ones — REQ-C-006.

---

## Problem statement

The generation prompts establish, internally, every fact the breakdown needs — and then
throw it away. `ORDERING_GENERATION_PROMPT.md` step 4 is explicit about this: *"establish
and write down (internally) the forcing dependency under the axis."* MCQ step 4 requires
*"Verify: does it fail under the axis?"*; MSQ step 4 requires *"Verify it fails for a
distinct reason from all other wrong answers"*; MAT step 6 requires the same plus the
no-elimination-shortcut simulation. Each checklist then re-asserts these as gates.

None of it is emitted. The `output` step in all four prompts renders stem/choices/key to
the learner and stops. So when the learner answers, delivery re-derives — from the
rendered artifact alone — the per-distractor failure mechanisms, the near-duplicate
differentiator, and the orthodox-but-wrong identification that generation had already
established and discarded. Three consequences:

1. **Delivery cannot be made low-reasoning by relocation.** Moving generation earlier
   (#8) does not move the *second* reasoning cost, which is authoring the breakdown.
   Without #9, the Delivery Loop reads the same prompts and does the same work, just
   later in the file.
2. **Re-derivation is silent and lossy.** Nothing checks that delivery's reconstructed
   failure mechanism is the one generation validated. A distractor that passed the
   checklist for reason X can be explained away at delivery for reason Y, and no signal
   distinguishes the two.
3. **Coverage is unenforceable.** "Address each wrong answer individually" is a delivery
   instruction with no pre-committed target. At generation time it is checkable; at
   delivery time it is a hope.

**The hazard this issue creates** (parent FM-C-1, R-C-1): requiring a written failure
rationale for every distractor makes *weak* distractors cheaper to produce than strong
ones. A distractor that is easy to explain away is, definitionally, one a reviewer can
discard without projecting the axis — the exact construction defect `CLAUDE.md` exists
to forbid. If that lands, the skill's premise collapses. Everything in *Additivity* and
*Ordering constraint* below exists to close it.

---

## Additivity — every atom field is a determination the checklist already forces

**This is the load-bearing section.** It is the answer to FM-C-1 and to R-C-1, and the
justification for every construction rule below. The claim: no atom field asks the
generator for judgment it did not already have to exercise and pass a gate on. Baking
persists an existing determination. It introduces zero new authoring pressure on
distractor design.

| Atom field | Already forced by (MCQ) | (MSQ) | (Ordering) | (Matching) |
|---|---|---|---|---|
| `axis_statement` | `<judgment-axes><overview>` — the axis is the determining factor in evaluation; step 2 builds the scenario around it | same | same, doubled (forcing dependency **and** distractor failure mode) | same, doubled (role semantic **and** wrong-attachment mode) |
| `key_survival` | step 3 `correct-answer-construction`: *"must survive projection under the assigned axis"*; checklist *"The correct answer only wins when evaluated forward"* | step 3 `correct-answers-construction`, per correct answer | step 4 `correct-sequence-construction`: forcing dependency per adjacency, **already written down internally**; checklist strict-total-order + ≥2 order-sensitive pairs | step 5 `key-construction`: cross-viability ≥2 per response, unique bijection; checklist *"The correct assignment is unique"* |
| `distractor_failures[*].failure` | step 4 verify-fails-under-axis; checklist *"Wrong answers fail under projection — not due to factual error"* | step 4 *"Verify it fails for a distinct reason from all other wrong answers"* | step 5 *"Each distractor must fail SELECTION for a distinct reason under the axis"* + `<pool-design-law>` | step 6 *"must match NO prompt under projection"*, *"Verify no two distractors fail for the same reason"* |
| `distractor_failures[*].orthodox_but_wrong` | `<orthodox-but-wrong>` — **exactly one** required; checklist gate | `<orthodox-but-wrong>` — at least one; checklist gate | `<orthodox-but-wrong minimum="1">`; checklist gate | `<orthodox-but-wrong minimum="1">`; checklist gate |
| `distractor_failures[*].near_duplicate_of` | `<near-duplicate-pair>` — **exactly one** pair; step 5/6 establish the twinning | `<similarity-construction>` — surface similarity is required, degree at generator discretion | `<near-duplicate-distractor minimum="1">` — twinned with a named correct step | `<near-duplicate-cell minimum="1">` — 2 twin prompts × 2 twin responses |
| `near_duplicate_differentiator` | step 5: *"Identify one phrase that will differentiate it from its pair"*; checklist *"the differentiating phrase only matters under forward projection"* | `<similarity-construction>`: *"The actual differentiator … must only reveal its importance under forward projection"* | `<near-duplicate-distractor>` rule 2: *"Identify one phrase that differentiates them"* | `<near-duplicate-cell>` rules 1–2: one phrase per twin pair, prompt-side and response-side |

Every cell is populated. There is no atom field for which the generator must originate
content it was not already required to establish and validate. **The atom is a
transcript of a passed gate, not a new gate.**

Corollary, and the operational rule: **if an atom is hard to write, the defect is in the
question, not in the atom.** A distractor whose `failure` cannot be stated as a specific
mechanism failed `<viability-requirement>` / `<pool-design-law>` / `<grid-design-law>`
already — it is regenerated under the *existing* rule, not softened to make the atom
easier. This is stated in the prompts as an explicit instruction (REQ-EXP-F-006), because
the inverse reading — soften the distractor until the atom is easy — is exactly FM-9-1.

### The ordering constraint that enforces it

The new atom-emission step is inserted **after** `internal-validation` and **before**
`output`, in all four prompts. This is not a placement preference; it is the parent
plan's own FM-C-1 resolution rendered as sequence: *"an atom is written because a
distractor already survives the checklist, never as a substitute for it."* A distractor
that has not yet passed the checklist has no atom written for it, so the atom can never
be the thing that shapes it.

Placing atom authoring *before* or *inside* validation would invert this: the generator
would be composing rationale while distractors are still malleable, which is the precise
mechanism of FM-C-1. That placement is rejected.

---

## Atom mapping per type

The shape is fixed. What varies is what the labels denote and what `key_survival` has to
carry. Terminology below is each prompt's own.

| | **MCQ** | **MSQ** | **Ordering** | **Matching** |
|---|---|---|---|---|
| Choice structure | 4 choices, A–D | 5 choices, A–E | pool P = K+D (4–8), labels A–H; K disclosed, D hidden | n prompts `1…n` (3–7) × m responses `A…` (m = n+D, 4–10) |
| `key` | one label | set of 1–4 labels | ordered list of the K correct-step labels | injective map, n prompt→response pairs |
| **Wrong choices** = `distractor_failures` keys | the 3 labels not in `key` | the 5 − \|key\| labels not in `key` | the D distractor labels | the D unused response labels |
| Count of entries | exactly 3 | 1–4 | 1–3 | 1–3 |
| `key_survival` carries | 1 mechanism (why the correct choice survives) | 1–4 mechanisms, one per correct label | K−1 adjacency forcings (2–4) **plus** the ≥2 order-sensitive pairs' reverse-order failures | n pairing justifications (3–7), each with the rule-out of the other surface-viable responses for that prompt |
| `orthodox_but_wrong: true` on | exactly 1 entry | ≥1 entry | ≥1 entry | ≥1 entry |
| `near_duplicate_of` anchor | the pair twin — **may be the key label**, which has no `distractor_failures` entry | the nearest similarity twin — may be a correct label | the correct step the distractor is twinned with — always a key label | typically **null for every entry**: the near-duplicate cell is 2 twin prompts × 2 twin *correct* responses; no distractor participates |
| `near_duplicate_differentiator` carries | the one phrase separating the pair | the differentiator across the similarity cluster (may span >2 choices) | the one embedded phrase separating the distractor twin from its correct step | **two** phrases: one separating the twin prompts, one separating the twin responses (protocol Component 4 requires both) |
| Incorrect-branch content not in `distractor_failures` | — | missed correct picks → `key_survival` | omitted correct steps and transposed forced pairs → `key_survival` | transpositions between two *genuine* responses → `key_survival` |

Three consequences follow, and all three are the substance of Open questions 1–3:

- **`key_survival` load varies 7× across types.** MCQ needs one statement; Matching at
  n=7 needs seven, each with rule-outs. A single `str` is the binding shape.
- **`near_duplicate_of` has no anchor in Matching.** Its near-duplicate construct
  involves no distractor at all, so the field is structurally null there while the
  construct is still mandatory (checklist: "≥1 near-duplicate confusion cell present").
- **`near_duplicate_of` can point at a label with no `distractor_failures` entry** in
  MCQ and always does in Ordering. A consumer that dereferences it as a key into
  `distractor_failures` will miss. The field names a *choice label*, not a distractor.

---

## Design decisions

Each row is either fixed upstream (parent plan / CLAUDE.md / existing prompt text) or is
listed in Open questions rather than settled here. Nothing in this table is an
independent design choice by this plan.

| Decision | Resolution | Source |
|---|---|---|
| Atom field names and nesting | Verbatim from the parent plan's Artifact schema. No renames, no additions, no restructuring. | Parent plan, "Artifact schema" — *"Field names are binding — sub-issues must not rename them"* |
| One shape across all four prompts | Identical field set, identical nesting, identical semantics. Divergence is a review reject. | Parent plan R-C-2 |
| Where atoms are authored | New construction-sequence step, inserted **after** `internal-validation`, **before** `output`. | Parent plan FM-C-1 resolution, rendered as sequence — see *Additivity* |
| Whether any existing check moves | No. Not one checklist item, construction step, viability rule, pool/grid law, required construct, or banned-language list is edited, reordered, softened, or made conditional. New checks are **appended** to each checklist. | `CLAUDE.md` invariant; parent plan Non-goals — *"No change to the difficulty invariant"* |
| What happens when an atom is hard to write | The question is regenerated under the existing rule (`<viability-requirement>` / `<pool-design-law>` / `<grid-design-law>`). The distractor is never softened to make the atom easier. Stated explicitly in each prompt. | `CLAUDE.md` — *"regenerated, never shipped"*; parent FM-C-1 |
| Atom visibility | Internal only. Never rendered, never summarized to the learner, never included in the presented trial. Mirrors the existing `probe_target` discipline. | REQ-C-007; parent FM-C-2 |
| `distractor_failures` coverage | Every wrong choice, no exceptions: 3 for MCQ, 5 − \|key\| for MSQ, D for Ordering, D for Matching. A missing entry blocks output. | REQ-C-006; parent Coverage rule |
| `failure` content standard | The specific point where the choice fails **under the axis**, stated as mechanism. A conclusion restatement ("it fails under the axis") does not satisfy it — the four protocols all say *"the mechanism, not just the conclusion."* | `SKILL.md` Response Protocol; all four prompts' Component 3 |
| Step numbering | The new step takes the current `output` step's number; `output` shifts by one (MCQ 9→10, MSQ 7→8, ORD 8→9, MAT 9→10). Verified safe: every existing intra-prompt step cross-reference points at a step at or before `internal-validation`, and no file outside the prompts references a prompt step number. | Measured — see Files touched |

---

## Requirements

| ID | Requirement | Scope | Parent |
|---|---|---|---|
| REQ-EXP-F-001 | Each generation prompt gains a construction-sequence step, inserted after `internal-validation` and before `output`, that emits the trial record with the `explanation` block populated | all 4 prompts | REQ-C-005 |
| REQ-EXP-F-002 | The emitted block uses the parent plan's field names verbatim: `axis_statement`, `key_survival`, `distractor_failures`, `failure`, `orthodox_but_wrong`, `near_duplicate_of`, `near_duplicate_differentiator` | all 4 prompts | REQ-C-005, R-C-2 |
| REQ-EXP-F-003 | `distractor_failures` has one entry per wrong choice, keyed by that choice's label — 3 for MCQ (A–D minus key), 5 − \|key\| for MSQ, the D distractor labels for Ordering, the D unused response labels for Matching | all 4 prompts | REQ-C-006 |
| REQ-EXP-F-004 | `orthodox_but_wrong` is `true` on the entry (or entries) satisfying that prompt's orthodox-but-wrong construct, `false` otherwise; at least one `true` entry exists per trial | all 4 prompts | REQ-C-006 |
| REQ-EXP-F-005 | `near_duplicate_of` names the choice label the entry is twinned with, or `null`. The named label may be the key / a correct step / absent from `distractor_failures` — it is a choice label, not a `distractor_failures` key | all 4 prompts | REQ-C-006 |
| REQ-EXP-F-006 | Each prompt states explicitly that a hard-to-write atom is evidence of a construction defect in the choice, resolved by regenerating the choice under the existing viability rule — never by weakening the choice to make the atom easier | all 4 prompts | FM-C-1, R-C-1 |
| REQ-EXP-F-007 | Each prompt's `internal-validation` checklist gains appended atom-coverage checks. No existing checklist item is edited, reordered, removed, or made conditional | all 4 prompts | FM-C-1, `CLAUDE.md` |
| REQ-EXP-F-008 | `key_survival` addresses every graded unit individually — the correct choice (MCQ), each correct label (MSQ), each forced adjacency plus each order-sensitive pair's reverse-order failure (Ordering), each prompt→response pairing with its rule-outs (Matching) | all 4 prompts | REQ-C-005; gated on OQ 1 |
| REQ-EXP-F-009 | `near_duplicate_differentiator` states the differentiating phrase(s) and why the difference is decisive **only** under forward projection. Matching states both the prompt-side and response-side phrase | all 4 prompts | REQ-C-005; gated on OQ 3 |
| REQ-EXP-E-001 | The `explanation` block is never rendered, quoted, summarized, or hinted at in the presented trial. The `output` step retains its existing "do not reveal the axis / do not mark the correct answer" prohibitions and adds the atoms to them | all 4 prompts | REQ-C-007, FM-C-2 |
| REQ-EXP-E-002 | Output is blocked if any wrong choice lacks a `distractor_failures` entry, or if any `failure` restates the conclusion rather than a mechanism | all 4 prompts | REQ-C-006, FM-C-3 |

**Non-goals.** No edit to `SKILL.md` (#8). No edit to `mcq-probe/.claude-plugin/plugin.json`
(orchestrator, at merge). No consistency pass (#10). No batching, Generation Phase, or
Delivery Loop (#8). No persistence (#7). No change to any construction rule, viability
rule, pool/grid law, required construct, banned-language list, or existing checklist item.

---

## Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-9-1 | **Distractor softening under baking pressure** | A generator required to write a failure rationale for every distractor finds weak distractors cheaper to explain than strong ones | Distractors become rejectable on surface reading — the exact defect `CLAUDE.md` forbids; the skill's premise collapses | **No.** Three-layer guard: (a) atom step runs strictly *after* `internal-validation`, so no distractor is malleable when its atom is written; (b) every atom field is already a forced determination (*Additivity*) so no new judgment is requested; (c) REQ-EXP-F-006 states the inverse rule explicitly in each prompt. Non-delegable review item — inherits parent FM-C-1 |
| FM-9-2 | Atoms rendered to the learner | Generation "outputs" a record and output defaults to visible | Full key plus rationale leaked with the question — trial destroyed | **No** — REQ-EXP-E-001. Explicit never-render instruction alongside the existing axis/key prohibitions in each `output` step |
| FM-9-3 | Incomplete `distractor_failures` | Generator writes atoms for the interesting distractors only | Delivery silently authors the missing rationale live; the cost never moved and the regression is invisible | **No** — REQ-EXP-F-003 + REQ-EXP-E-002 blocks output; #10 re-checks over the batch |
| FM-9-4 | Atom authoring drifts before validation | A later edit folds atom writing into an earlier construction step, or into `output` alongside presentation | Reintroduces FM-9-1 by removing the ordering guard | **No** — step placement is a requirement (REQ-EXP-F-001), not a convention |
| FM-9-5 | `key_survival` collapses n statements into one summary | A single `str` field invites a single sentence, at Matching n=7 most of all | Delivery cannot "address each pairing on its own" as all four protocols require; the incorrect branch loses transposition and omission coverage entirely | **No** — REQ-EXP-F-008, but the realization is **gated on OQ 1** |
| FM-9-6 | Atom semantics diverge across the four prompts | Four files edited separately; Matching's structure differs most | #7 cannot persist one shape; #10 cannot check one shape; #8's consumer needs four code paths | **No** — REQ-EXP-F-002; parent R-C-2 makes divergence a review reject |
| FM-9-7 | `failure` restates the conclusion | "D fails because it does not survive the axis" satisfies the field's type but carries no mechanism | Breakdown prose degrades to tautology; the degradation is invisible because the field is populated | **No** — REQ-EXP-E-002; the four protocols' *"mechanism, not just the conclusion"* is the standard |
| FM-9-8 | `near_duplicate_of` dereferenced as a `distractor_failures` key | It legitimately names the key label (MCQ), a correct step (Ordering, always), or is null (Matching, typically) | Consumer lookup misses; near-duplicate resolution dropped from the breakdown | **No** — REQ-EXP-F-005 states the field's domain is choice labels; the mapping table records the per-type anchor |
| FM-9-9 | Matching's orthodox-but-wrong realized in **matched** form | `<orthodox-but-wrong>` permits *"a cross-attracting MATCHED response — a prompt's conventional answer that is genuinely another prompt's true match"* | A used response cannot carry `orthodox_but_wrong: true`, since only distractors have entries | **Accepted.** Matching's checklist independently requires *"≥1 orthodox-but-wrong distractor response present"*, so the primary form is always present and the bool always has a carrier. A secondary matched-form instance is unrepresentable and is not surfaced in the breakdown |
| FM-9-10 | Prompts still instruct one-at-a-time generation | `<generation-cadence>` and `<trial-sequence-rules><rule id="1-at-a-time">` in all four prompts say *"Do NOT pre-generate all trials"* — 8 sites, directly contradicting REQ-C-001 | The generator is told to batch by `SKILL.md` and told not to by the prompt it is constructing under; behavior is undefined | **No, but unowned** — the parent plan assigns these files to #9 and this text to nobody. See OQ 5 |
| FM-9-11 | Presentation removed from the prompt before #8 lands | REQ-C-010 gives presentation to the Delivery Loop; the prompts' `output` steps currently present | Between the two merges, the skill either presents nothing or presents twice | **No** — see OQ 4; the safe form is additive-only in #9 (`output` keeps presenting) with removal owned by #8 or a follow-up |
| FM-9-12 | Batch context growth exceeds the parent's flag threshold | Atoms add ~250–760 tokens/trial; stems+choices ~500–1,500; a 10-trial batch measures ~7.5k–22.5k | Parent FM-C-7's "flag if a 10-batch measures beyond ~15k" is breached on Matching-heavy batches | **Accepted, with a measurement owed.** #9 does not fix it; the figures above close parent Open question 1 in the negative for the upper range and are reported to the orchestrator |

---

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-9-1 | An implementer treats "bake the explanation" as licence to simplify distractors (FM-9-1) | Medium | **High** | *Additivity* section is the standing argument; REQ-EXP-F-006 puts it in the prompts; the diff must show **zero** deletions or edits inside `<viability-requirement>`, `<pool-design-law>`, `<grid-design-law>`, `<required-constructs>`, `<similarity-construction>`, `<near-duplicate-pair>`, `<orthodox-but-wrong>`, and every `<internal-validation>` — appended lines only. Non-delegable review. Inherits parent R-C-1 |
| R-9-2 | Atom schema drifts across the four prompts (FM-9-6) | Medium | Medium | One canonical block authored once, pasted into all four with only the label vocabulary substituted; diff the four blocks against each other before the PR. Inherits parent R-C-2 |
| R-9-3 | Wire-format mismatch with #8's consumer | Medium | **High** | #8 and #9 run in parallel and neither the issue nor the parent plan fixes a serialization. See OQ 2 — blocking, must be settled with the orchestrator before implementation |
| R-9-4 | Merge conflict with #8 or #10 | Low | Medium | #9 touches only the four prompts; #8 touches only `SKILL.md`; the version bump in `plugin.json` is the orchestrator's. Disjoint by construction, provided FM-9-11 is not "fixed" inside #9 |
| R-9-5 | Step renumbering breaks a cross-reference | Low | Low | Measured: all 18 intra-prompt step references point at steps ≤ `internal-validation`; `SKILL.md` and all plan docs reference prompt *sections*, never prompt step numbers. Only `output` shifts, and nothing references it |
| R-9-6 | Prompt growth inflates per-session read volume | Medium | Low | Estimated +70–85 lines / ~1.2–1.4k tokens per prompt, ~5k total (+~8.5% on the measured ~58.9k). Acceptable against the delivery-side reasoning it removes; measure post-implementation |
| R-9-7 | Matching's structural divergence forces a per-type schema exception | Medium | Medium | `near_duplicate_of` null-for-all and the two-phrase differentiator are the two known points; both are handled inside the binding shape. Any *third* divergence found during implementation is a stop-and-report, not a local fix |

---

## Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `plans/9-explanation-baking.md` | Create | This document | Stage 1 deliverable; #8/#9/#10 build against the parent, this records #9's mapping and open questions |
| `mcq-probe/skills/mcq-probe-0-router/prompts/MCQ_GENERATION_PROMPT.md` | Modify | New construction step after step 8 `internal-validation`, before `output` (9→10); atom schema block with A–D label vocabulary; appended checklist items; never-render line in `output` | REQ-EXP-F-001…009, E-001, E-002 |
| `.../prompts/MSQ_GENERATION_PROMPT.md` | Modify | Same, after step 6 `internal-validation`, before `output` (7→8); A–E vocabulary; `distractor_failures` sized 5 − \|key\|; similarity-cluster differentiator | as above |
| `.../prompts/ORDERING_GENERATION_PROMPT.md` | Modify | Same, after step 7 `internal-validation`, before `output` (8→9); pool-label vocabulary; `key_survival` covers K−1 adjacencies + order-sensitive pairs; `near_duplicate_of` anchors on a correct step | as above |
| `.../prompts/MATCHING_GENERATION_PROMPT.md` | Modify | Same, after step 8 `internal-validation`, before `output` (9→10); prompt/response label vocabulary; `key_survival` covers n pairings with rule-outs; two-phrase differentiator; `near_duplicate_of` typically null | as above |
| `.../SKILL.md` | **None** | — | #8's file. Read for the Response Protocol contract only. Editing it causes a merge conflict |
| `mcq-probe/.claude-plugin/plugin.json` | **None** | — | Version bump is the orchestrator's job at merge, to avoid a conflict with #8's PR |

**Blast radius check.** Four files, one section-insert and one checklist-append each,
plus one line in each `output` step. No deletion anywhere. No existing rule text
modified. The full set of elements that must show zero edits is enumerated in R-9-1.

---

## Open questions

Every row is a fork the inputs do not settle. None is resolved in this plan.

| # | Question | Blocker for? |
|---|---|---|
| 1 | **`key_survival` is a single `str` but must carry 1 (MCQ) to 7 (Matching n=7) distinct mechanism statements, each of which the Response Protocol requires delivery to address individually** (*"Address each pairing on its own; do not summarize the whole key in one sentence"*). Adding per-label keys would restructure a binding field. Is the intent (a) one string with per-label internal segmentation, (b) `key_survival` keyed by label like `distractor_failures`, or (c) something else? Under (a), Ordering must also fit K−1 adjacency forcings **and** ≥2 reverse-order failures into the same string; Matching must fit n pairings each with rule-outs. | REQ-EXP-F-008; the shape of the atom block in all four prompts; whether Ordering's and Matching's incorrect branches (omissions, transpositions) are covered at all |
| 2 | **What serialization do the prompts emit, and what does #8's Generation Phase expect?** The parent plan shows the artifact in YAML-ish pseudo-schema; the prompts are XML documents; `SKILL.md`'s existing internal record is a brace-delimited pseudo-object. Neither the issue nor the parent fixes a wire format, and #8 is being built in parallel against the same unfixed boundary. | Implementation of all four prompts; interop with #8 |
| 3 | **`near_duplicate_differentiator` is one `str`, but the constructs it serves are not singular.** Matching's near-duplicate cell needs two phrases (prompt-side and response-side, both required by Component 4) and a trial may contain more than one cell (worked example 1 has two). Ordering permits more than one near-duplicate distractor when D=3. MSQ's similarity structure can span three or more choices, so `near_duplicate_of`'s single label cannot name the cluster. One string for all of it, or per-construct segmentation? | REQ-EXP-F-009; MSQ's and Matching's Component 4 coverage |
| 4 | **Does the prompt still present the trial, or only emit it?** REQ-C-010 gives presentation to the Delivery Loop, which implies the `output` step stops rendering. But #8 and #9 merge separately, so removing presentation in #9 leaves the skill broken in between (FM-9-11). Is #9 strictly additive (`output` keeps presenting, atoms emitted alongside, internal-only), with removal owned by #8 or a follow-up? | The `output` step edit in all four prompts; ordering of the two merges |
| 5 | **Who removes the one-at-a-time cadence directives from the four prompts?** `<generation-cadence>` and `<trial-sequence-rules><rule id="1-at-a-time">` in each prompt say *"Generate ONE trial at a time… Do NOT pre-generate all trials before the learner has responded"* — 8 sites, directly contradicting REQ-C-001. The parent's Files-touched table gives the prompts to #9 for atoms and internal-only discipline, and gives `SKILL.md` to #8; nobody owns this text. | REQ-C-001 actually holding; whether #9's scope is wider than the issue states |
| 6 | **Does `failure` have to carry the "why it was not visible on first read" account?** All four `<evaluation-framework>` sections require it as an identification feeding the incorrect branch (MCQ `<incorrect-answer-evaluation>` part 3; MSQ part 3; Ordering `<incorrect-sequence-evaluation>`; Matching `<incorrect-key-evaluation>`). The binding schema has no field for it, and `failure` is specified as *"the specific point where it fails under the axis"* — the failure, not the viability account. Either `failure` subsumes it, or the incorrect branch loses it, or a field is needed that I cannot add. | REQ-EXP-E-002's mechanism standard; incorrect-branch fidelity for all four types |
| 7 | **Parent Coverage-rule wording: "every unselected choice for MSQ."** Read literally, "unselected" is learner-relative and unknowable at generation. The only generation-time-coherent reading is "every choice not in the key." Confirm the reading, or correct the parent. | REQ-EXP-F-003's MSQ row |
| 8 | **Should the prompts' `<correct-response-protocol>` / `<incorrect-response-protocol>` sections gain a component→field mapping annotation?** It makes the reconstruction contract explicit and is cheap, but it edits sections outside the issue's stated scope ("output step"). | Scope of the prompt edits |

---

## Implementation order

Stage 2 only. Do not begin until the orchestrator issues an explicit execute signal, and
not before OQ 1, 2, 4 and 6 are resolved — each of them determines the literal content of
the block being inserted.

1. Resolve OQ 1, 2, 4, 6 with the orchestrator. OQ 3, 5, 7, 8 may be resolved in parallel
   but do not gate the first edit.
2. Author the canonical atom block **once**, in the settled serialization, with the
   label vocabulary parameterized. This is the single source the four prompts share
   (R-9-2).
3. `MCQ_GENERATION_PROMPT.md` first — the simplest structure (fixed 4 choices, exactly
   one near-duplicate pair, exactly one orthodox-but-wrong, exactly 3
   `distractor_failures` entries). It is the reference instantiation.
4. `MSQ_GENERATION_PROMPT.md` — adds a variable-size key, a variable-size
   `distractor_failures` (1–4), multiple permitted `orthodox_but_wrong: true` entries,
   and the similarity-cluster differentiator (OQ 3).
5. `ORDERING_GENERATION_PROMPT.md` — adds the adjacency-plus-order-sensitive-pair load on
   `key_survival` (OQ 1) and `near_duplicate_of` anchoring on a correct step.
6. `MATCHING_GENERATION_PROMPT.md` — the hardest: n pairings with rule-outs in
   `key_survival`, the two-phrase differentiator, `near_duplicate_of` typically null, and
   the matched-form orthodox exception (FM-9-9).
7. Diff the four atom blocks against each other. Any semantic divergence beyond label
   vocabulary is a defect (R-9-2).
8. **Mandatory gate — the R-9-1 check.** Diff each prompt against `main` and confirm
   **zero** deletions or modifications inside `<viability-requirement>`,
   `<pool-design-law>`, `<grid-design-law>`, `<required-constructs>`,
   `<similarity-construction>`, `<near-duplicate-pair>`, `<orthodox-but-wrong>`,
   `<near-duplicate-cell>`, `<near-duplicate-distractor>`, `<order-sensitive-pairs>`, and
   every `<internal-validation>` block. Appended lines only. Do not ship without it.
9. **Mandatory gate — the difficulty check.** Dry-run one trial per type (4 total),
   author the atoms, and confirm against `CLAUDE.md`'s invariant that every distractor is
   still independently viable in isolation and fails only under projection. A distractor
   that became easier to state is FM-9-1 in the act; regenerate it.
10. Measure the resulting prompt sizes and one full trial's atom payload per type; report
    the figures against parent FM-C-7 and parent Open question 1.
