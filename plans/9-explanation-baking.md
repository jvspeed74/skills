# Plan: Explanation-baking in generation output (#9 — Feature C / C2)

**Status:** Implemented — 2026-08-30. All 8 open questions resolved by the coordinator; scope expanded by REQ-C-012. Both mandatory gates passed.
**Date:** 2026-08-30
**Branch:** `feat/9-explanation-baking`
**Parent plan:** `plans/5-frontload-question-generation.md` **as amended in PR #21** — the coordinator's resolutions below are authoritative and supersede the version as it read at planning time.
**Requirements owned:** REQ-C-005, REQ-C-006, REQ-C-007, **REQ-C-012** (scope expansion)
**Sibling issues:** #8 (SKILL.md Generation Phase / Delivery Loop, parallel) · #10 (consistency pass, gated on both)

---

## Readback — the defining interpretation

1. **The atom shape is fixed; the mapping was not.** Mapping six fields onto four choice
   structures was this issue's actual work. Three shape amendments came out of it and are
   now settled: `key_survival` is type-specific, `near_duplicate_differentiators` is a
   list, and each distractor entry carries a `viability_account`.
2. **Baking is a recording operation, not an authoring operation.** Every atom field
   corresponds to a determination the existing internal-validation checklist already
   forces the generator to make before output. #9 persists those determinations; it does
   not ask for new judgment. Worked in full in *Additivity*.
3. **#9 changes generation output, not generation.** No construction rule, viability rule,
   pool/grid law, required construct, banned-language list, or checklist item is weakened,
   reordered around, or made conditional. Verified mechanically — see *Gate results*.

---

## Background / context

### Key globals

| Global | Before | After #9 |
|---|---|---|
| Generation cadence | One trial at a time; *"Do NOT pre-generate all trials"* — 8 sites across the 4 prompts | Batched generation, sequential presentation — REQ-C-012 |
| Prompt output | The trial, rendered to the learner | Trial record **plus** `explanation` atoms, emitted internally as JSON; presentation retained |
| Rationale authoring | At delivery, after the learner answers | At generation — REQ-C-005 |
| Rationale coverage | Whatever delivery produced live | Every wrong choice, enforced pre-output — REQ-C-006 |
| Atom visibility | n/a | Internal only, never rendered — REQ-C-007 |
| Construction sequence | MCQ 9 steps, MSQ 7, ORD 8, MAT 9 | +1 each: `explanation-baking`, inserted after `internal-validation`, before `output` |
| Internal-validation checklists | MCQ 14, MSQ 13, ORD 17, MAT 17 | +1 each (a choice-level statability check); atom-completeness lives in the new step's emission gate |

### Measured sizes

| Prompt | Lines | ~Tokens before | ~Tokens after |
|---|---|---|---|
| `MCQ_GENERATION_PROMPT.md` | 913 → 1,069 (+156) | 10,850 | 13,012 |
| `MSQ_GENERATION_PROMPT.md` | 949 → 1,120 (+171) | 11,276 | 13,707 |
| `ORDERING_GENERATION_PROMPT.md` | 1,215 → 1,418 (+203) | 14,996 | 17,961 |
| `MATCHING_GENERATION_PROMPT.md` | 1,714 → 1,923 (+209) | 21,504 | 24,572 |
| **Total** | **4,791 → 5,530 (+739)** | **58,626** | **69,251 (+18.1%)** |

Growth came in at +10.6k tokens against a planned ~5k. The overrun is concentrated in the
per-field forcing citations and the emission gates — both deliberate, both doctrine-carrying.
Recorded as a variance, not absorbed silently.

### Pipeline

#8 splits `SKILL.md`'s Trial Loop into a Generation Phase (all `BATCH_SIZE` trials produced
up front into an in-context batch artifact) and a Delivery Loop (present, parse, grade
against the stored key, assemble the breakdown from stored atoms — REQ-C-010). #9 makes the
second half of REQ-C-010 possible: the atoms have to exist and be complete, or delivery
silently authors the missing rationale live and the reasoning cost never moved (FM-C-3).

### What the atoms must reconstruct

`SKILL.md`'s Response Protocol (lines 359–513) and each prompt's own response protocols.
Two properties drive the design:

- **The correct and incorrect branches carry identical content**, differing only in
  ordering and framing. Atoms serve both with no duplication.
- **The incorrect branch varies by which wrong choice was taken.** Generation cannot know
  the learner's pick, so `distractor_failures` must cover **every** wrong choice —
  REQ-C-006.

---

## Problem statement

The generation prompts establish, internally, every fact the breakdown needs — then throw
it away. `ORDERING` step 4 is explicit: *"establish and write down (internally) the forcing
dependency under the axis."* MCQ step 4 requires *"Verify: does it fail under the axis?"*;
MSQ step 4 requires *"Verify it fails for a distinct reason from all other wrong answers"*;
MAT step 6 requires the same plus the no-elimination-shortcut simulation. Each checklist
re-asserts these as gates. None of it was emitted.

Three consequences: delivery cannot be made low-reasoning by relocation alone;
re-derivation at delivery is silent and lossy, since nothing checks that the reconstructed
mechanism is the one generation validated; and coverage is unenforceable, because "address
each wrong answer individually" has no pre-committed target at delivery time.

**The hazard this issue creates** (parent FM-C-1, R-C-1): requiring a written failure
rationale for every distractor could make *weak* distractors cheaper to produce than strong
ones — and a distractor that is easy to explain away is one a reviewer can discard without
projecting the axis. *Additivity* and the ordering constraint close it structurally; the
`viability_account` field, added by the OQ-6 resolution, inverts the pressure outright
(*Gate results*).

---

## Additivity — every atom field is a determination the checklist already forces

**This is the load-bearing section**, and it is what the implementation encodes: each
prompt's `explanation-baking` step opens with a `<what-this-step-is>` block naming, field
by field, the construction step and checklist item that already forced that determination.

| Atom field | Already forced by (MCQ) | (MSQ) | (Ordering) | (Matching) |
|---|---|---|---|---|
| `axis_statement` | Steps 1–2; the axis is the determining factor in evaluation | same | same, doubled (forcing dependency **and** distractor failure mode) | same, doubled (role semantic **and** wrong-attachment mode) |
| `key_survival` | Step 3; checklist *"The correct answer only wins when evaluated forward"* | Step 3, per correct answer | Step 4 — forcing dependency per adjacency, **already written down internally**; ≥2 order-sensitive pairs | Step 5 — cross-viability ≥2 per response, unique bijection |
| `failure` | Step 4 verify-fails-under-axis; Step 6 distinct reasons | Step 4 *"fails for a distinct reason from all other wrong answers"* | Step 5 *"fails SELECTION for a distinct reason under the axis"* | Step 6 *"must match NO prompt under projection"* |
| `viability_account` | `<viability-requirement>`; Step 4 *"Is it viable in isolation?"*; checklist *"All four answers are independently viable"* | Step 4 *"Construct it to be independently viable in isolation"* | `<pool-design-law>` *"must read as a legitimate, plausible step in THIS task"* | `<grid-design-law>` part 1 cross-viability; Step 6 *"plausible for ≥2 prompts"* |
| `orthodox_but_wrong` | `<orthodox-but-wrong>`, exactly one | at least one | `minimum="1"` | `minimum="1"` |
| `near_duplicate_of` | `<near-duplicate-pair>`, exactly one pair | `<similarity-construction>` | `<near-duplicate-distractor>`, twinned with a correct step | `<near-duplicate-cell>` — twins two *correct* responses; normally null |
| `near_duplicate_differentiators` | Step 5 *"Identify one phrase that will differentiate it"* | `<similarity-construction>` | rule 2 *"Identify one phrase that differentiates them"* | rules 1–2, prompt-side **and** response-side phrase |

Every cell is populated. **The atom is a transcript of a passed gate, not a new gate.**

Corollary, encoded in each prompt as an `<the-absolute-rule>` block: **if an atom is hard
to write, the defect is in the choice, not in the atom.** A distractor whose `failure` or
`viability_account` cannot be stated already failed `<viability-requirement>` /
`<pool-design-law>` / `<grid-design-law>` — it is regenerated under the *existing* rule,
never softened to make the atom easier.

### The ordering constraint that enforces it

The `explanation-baking` step sits **after** `internal-validation` and **before** `output`
in all four prompts. This is the parent plan's FM-C-1 resolution rendered as sequence: a
distractor that has not yet passed the checklist has no atom written for it, so the atom
can never be the thing that shapes it. Placing atom authoring earlier would let the
generator compose rationale while distractors are still malleable — the precise mechanism
of FM-C-1. Rejected.

This is also why the appended checklist item is a check on the **choice**, not on the
record: at `internal-validation` time no atom exists yet, so an atom-completeness check
there would be unsatisfiable. The checklist asks whether the failure mechanism and the
viability account *can be stated*; the new step's `<emission-gate>` checks that they *were*.

---

## Atom mapping per type

| | **MCQ** | **MSQ** | **Ordering** | **Matching** |
|---|---|---|---|---|
| Choice structure | 4 choices, A–D | 5 choices, A–E | pool P = K+D (4–8), A–H; K disclosed, D hidden | n prompts `1…n` (3–7) × m responses `A…` (4–10) |
| `key` | one label | array of 1–4 labels | ordered array of the K correct-step labels | injective map, n pairs |
| `distractor_failures` keys | the 3 labels not in `key` | the 5 − \|key\| labels **not in `key`** | the D distractor labels | the D **unused** response labels |
| Entry count | exactly 3 | 1–4 | 1–3 | 1–3 |
| `key_survival` | `{<key label>: str}` — 1 entry | `{<label>: str}` — one per correct label | `{adjacency_forcings: [str], reverse_order_failures: [str]}` — K−1 forcings, ≥2 reversals | `{<prompt label>: str}` — one per pairing, each with rule-outs |
| `orthodox_but_wrong: true` | exactly 1 | ≥1 | ≥1 | ≥1 |
| `near_duplicate_of` | pair twin — **may be the key label** | nearest similarity twin — may be a correct label | the correct step twinned with — **always a key label** | **normally null** — the cell twins two correct responses |
| `near_duplicate_differentiators` | 1 entry | one per similarity cluster | one per near-duplicate distractor | one per cell, each naming **both** phrases |
| Incorrect-branch content outside `distractor_failures` | — | missed correct picks → `key_survival` | omissions + transposed forced pairs → `key_survival` | transpositions between two *genuine* responses → the rule-outs inside `key_survival` |

Two structural facts the implementation states explicitly in each prompt:

- **`near_duplicate_of` names a choice label, not a `distractor_failures` key.** It legitimately
  points at the key (MCQ), always at a correct step (Ordering), or is null (Matching).
- **Matching's transposition errors have no distractor entry.** Two genuine responses
  swapped involves no distractor, so the rule-out half of each `key_survival` entry is the
  *only* place that error is explained. The prompt says so in as many words.

---

## Design decisions

| Decision | Resolution | Source |
|---|---|---|
| Atom field names and nesting | Verbatim from the amended parent schema. No renames, no additions beyond the three resolved amendments. | Parent Artifact schema (PR #21) |
| One shape across four prompts | Identical field set, nesting, and semantics; only label vocabulary differs. | Parent R-C-2 |
| Wire format | **JSON**, one object per trial, emitted as a fenced code block, internal-only. Templates inside the prompts are shown unfenced and the fence described in prose — the prompt files are themselves wrapped in an outer ` ```xml ` fence, and a nested backtick fence would terminate it. | OQ-2 resolution |
| Where atoms are authored | New step after `internal-validation`, before `output`. | Parent FM-C-1, rendered as sequence |
| Whether any existing check moves | No. Verified mechanically over 32 element types across all four files. New checklist lines appended only. | `CLAUDE.md`; coordinator's binding bar |
| Hard-to-write atom | Regenerate the choice under the existing rule. Never soften the choice. Encoded as `<the-absolute-rule>` in each prompt. | `CLAUDE.md`; parent FM-C-1 |
| Atom visibility | Internal only; `<internal-only>` block in each step plus a never-render line in each `output` step. | REQ-C-007, FM-C-2 |
| Does `output` still present? | **Yes.** Both PRs must be independently safe in either merge order; stopping presentation in #9 would break the skill in the window before #8 lands. #8 suppresses the step from its side. | OQ-4 resolution / REQ-C-015 |
| Cadence | Batched **generation**, sequential **presentation**. Amended positively at all 8 sites; `rule id="1-at-a-time"` renamed to `batch-generation`. | REQ-C-012 |
| Checklist append semantics | The appended item is a **choice-level statability check**, satisfiable where it runs. Atom completeness is checked in the new step's `<emission-gate>`. | Ordering constraint — see *Additivity* |
| Step renumbering | New step takes the old `output` number; `output` shifts (MCQ 9→10, MSQ 7→8, ORD 8→9, MAT 9→10). Verified safe: all 18 intra-prompt step references point at steps ≤ `internal-validation`, and nothing outside the prompts references a prompt step number. | Measured; coordinator-approved |

---

## Requirements

| ID | Requirement | Scope | Parent |
|---|---|---|---|
| REQ-EXP-F-001 | Each prompt gains an `explanation-baking` step after `internal-validation`, before `output`, emitting the trial record with `explanation` populated | all 4 | REQ-C-005 |
| REQ-EXP-F-002 | Field names verbatim: `axis_statement`, `key_survival`, `distractor_failures`, `failure`, `viability_account`, `orthodox_but_wrong`, `near_duplicate_of`, `near_duplicate_differentiators` | all 4 | REQ-C-005, R-C-2 |
| REQ-EXP-F-003 | `distractor_failures` has one entry per wrong choice — 3 (MCQ), 5 − \|key\| (MSQ), D (Ordering), D unused responses (Matching). "Not in the key" is the test; it is never learner-relative | all 4 | REQ-C-006 |
| REQ-EXP-F-004 | `orthodox_but_wrong` true on every entry satisfying that prompt's construct; ≥1 true per trial | all 4 | REQ-C-006 |
| REQ-EXP-F-005 | `near_duplicate_of` names a choice label or null — explicitly not a key into `distractor_failures` | all 4 | REQ-C-006 |
| REQ-EXP-F-006 | Each prompt states that a hard-to-write atom is a construction defect in the choice, resolved by regeneration under the existing rule — never by weakening the choice | all 4 | FM-C-1, R-C-1 |
| REQ-EXP-F-007 | Each `internal-validation` checklist gains an appended **choice-level** statability check. No existing item edited, reordered, removed, or made conditional. Atom completeness is gated in the new step | all 4 | FM-C-1 |
| REQ-EXP-F-008 | `key_survival` is type-specific per the OQ-1 resolution and addresses every graded unit individually | all 4 | REQ-C-005 |
| REQ-EXP-F-009 | `near_duplicate_differentiators` is a list, one entry per construct; Matching entries name both the prompt-side and response-side phrase | all 4 | REQ-C-005 |
| REQ-EXP-F-010 | Each `distractor_failures` entry carries `viability_account`: why the choice reads as correct on first pass — a statement distinct from `failure` and not derivable from it | all 4 | OQ-6 resolution |
| REQ-EXP-F-011 | The `<generation-cadence>` and `<trial-sequence-rules>` cadence blocks permit batched generation and state the new cadence positively; sequential presentation preserved | all 4 | **REQ-C-012** |
| REQ-EXP-E-001 | The `explanation` record is never rendered, quoted, summarized, or hinted at; each `output` step carries the prohibition alongside its existing ones | all 4 | REQ-C-007, FM-C-2 |
| REQ-EXP-E-002 | Output is blocked if any wrong choice lacks an entry, or if any `failure` restates the conclusion rather than a mechanism | all 4 | REQ-C-006, FM-C-3 |

**Non-goals.** No edit to `SKILL.md` (#8). No edit to `plugin.json` (orchestrator, at merge).
No consistency pass (#10). No persistence (#7). No change to any construction rule,
viability rule, pool/grid law, required construct, banned-language list, or existing
checklist item.

---

## Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-9-1 | **Distractor softening under baking pressure** | Weak distractors cheaper to explain than strong ones | Distractors become rejectable on surface reading; the skill's premise collapses | **No.** Four-layer guard: atom step runs strictly after validation; every field is an already-forced determination; `<the-absolute-rule>` states the inverse; and `viability_account` **inverts the pressure gradient** — a weak distractor is *harder* to bake, not easier (*Gate results*) |
| FM-9-2 | Atoms rendered to the learner | Output defaults to visible | Key plus rationale leaked with the question | **No** — `<internal-only>` block plus a never-render line in each `output` step |
| FM-9-3 | Incomplete `distractor_failures` | Atoms written for the interesting distractors only | Delivery silently authors the rest live | **No** — `<emission-gate>` blocks output; #10 re-checks over the batch |
| FM-9-4 | Atom authoring drifts before validation | A later edit folds baking into an earlier step | Reintroduces FM-9-1 | **No** — placement is REQ-EXP-F-001, not a convention |
| FM-9-5 | `key_survival` collapses n statements into one | A single `str` invites a single sentence | Delivery cannot address each unit individually; Ordering/Matching incorrect branches lose coverage | **Closed by OQ-1** — `key_survival` is now type-specific and keyed/split per unit; the field-rules block forbids merged statements explicitly |
| FM-9-6 | Atom semantics diverge across the four prompts | Four files edited separately | #7 cannot persist one shape; #8 needs four code paths | **No** — one canonical block, label vocabulary substituted; verified by cross-diff |
| FM-9-7 | `failure` restates the conclusion | Tautology satisfies the field's type | Breakdown prose degrades invisibly | **No** — REQ-EXP-E-002; each prompt names the exact tautology it rejects |
| FM-9-8 | `near_duplicate_of` dereferenced as a `distractor_failures` key | It names the key (MCQ), a correct step (Ordering), or is null (Matching) | Consumer lookup misses | **No** — stated in each prompt's field-rules |
| FM-9-9 | Matching's orthodox-but-wrong in **matched** form | The construct permits a cross-attracting matched response | A used response cannot carry the bool | **Accepted, and handled** — the checklist independently guarantees ≥1 distractor-form, so the bool always has a carrier; the matched form's pull is recorded as a rule-out inside the relevant `key_survival` entry. Stated in MATCHING's field-rules |
| FM-9-10 | Prompts instruct one-at-a-time generation | 8 sites contradicting REQ-C-001 | Undefined behavior under batching | **Closed by REQ-C-012** — all 8 amended; zero residual directives |
| FM-9-11 | Presentation removed before #8 lands | REQ-C-010 gives presentation to the Delivery Loop | Skill broken between merges | **Closed by OQ-4** — `output` keeps presenting; #9 is additive-only |
| FM-9-12 | Batch context growth | Atoms add ~250–900 tokens/trial | A 10-trial batch runs ~7.5k–22.5k | **Accepted** — parent threshold raised to 25k and handed to #4 as a window-size input |
| FM-9-13 | Prompt growth exceeds estimate | Forcing citations and emission gates are verbose | +10.6k tokens (+18.1%) against a planned ~5k | **Accepted, reported.** The overrun is doctrine-carrying text; trimming it would trim the FM-9-1 guard |

---

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-9-1 | An implementer treats baking as licence to simplify distractors | Medium | **High** | Mechanical gate: zero edits inside 32 protected element types, verified across all four files; `internal-validation` proven append-only. Plus the `viability_account` inversion |
| R-9-2 | Atom schema drift across the four prompts | Medium | Medium | One canonical block; cross-diffed |
| R-9-3 | Wire-format mismatch with #8's consumer | Low | High | **Closed** — JSON, fenced, one object per trial (OQ-2) |
| R-9-4 | Merge conflict with #8 or #10 | Low | Medium | #9 touches only the four prompts; #8 only `SKILL.md`; `plugin.json` is the orchestrator's |
| R-9-5 | Step renumbering breaks a cross-reference | Low | Low | **Closed** — measured; only `output` shifts and nothing references it |
| R-9-6 | Prompt growth inflates per-session read volume | Realized | Low | +18.1%; reported as FM-9-13 |
| R-9-7 | Matching forces a per-type schema exception | Low | Medium | Both known points (null `near_duplicate_of`, two-phrase differentiator) handled inside the binding shape; no third divergence found |

---

## Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `plans/9-explanation-baking.md` | Modify | This document, updated for the resolutions, REQ-C-012, and gate results | Traceability |
| `.../prompts/MCQ_GENERATION_PROMPT.md` | Modify | Cadence ×2; checklist +1; new step 9 `explanation-baking`; `output` 9→10 + never-render | REQ-EXP-F-001…011, E-001…002 |
| `.../prompts/MSQ_GENERATION_PROMPT.md` | Modify | Same; new step 7; `output` 7→8 | as above |
| `.../prompts/ORDERING_GENERATION_PROMPT.md` | Modify | Same; new step 8; `output` 8→9 | as above |
| `.../prompts/MATCHING_GENERATION_PROMPT.md` | Modify | Same; new step 9; `output` 9→10 | as above |
| `.../SKILL.md` | **None** | — | #8's file, edited in parallel |
| `mcq-probe/.claude-plugin/plugin.json` | **None** | — | Version bump is the orchestrator's at merge |

Diff: 4 files, +797 / −58. Every one of the 58 deletions is accounted for: 4× cadence body,
4× `1-at-a-time` rule block, 4× `output` opening tag (renumbering). Zero deletions inside
any protected element.

---

## Open questions

All resolved by the coordinator on 2026-08-30.

| # | Question | Resolution |
|---|---|---|
| 1 | `key_survival` cardinality — one `str` cannot carry 1–7 statements | **Type-specific.** mcq `{<key label>: str}`; msq `{<label>: str}` per correct label; ordering `{adjacency_forcings: [str], reverse_order_failures: [str]}`; matching `{<prompt label>: str}` per pairing |
| 2 | Wire format undefined | **JSON**, one object per trial, fenced, internal-only. What #7 persists |
| 3 | `near_duplicate_differentiator` singular vs. plural | **List** — `near_duplicate_differentiators: [str]`, empty when none; Matching supplies both phrases |
| 4 | Does `output` still present? | **Yes** — REQ-C-015, both PRs independently safe in either merge order |
| 5 | Who owns the cadence contradiction? | **#9** — scope expansion, REQ-C-012 |
| 6 | Is the "not visible on first read" account covered? | **No — new field.** `viability_account: str` per distractor entry. Doctrine-load-bearing: it makes the every-wrong-answer-viable invariant auditable at generation time |
| 7 | Parent's "every unselected choice for MSQ" | **Corrected** — "every choice not in the key." "Unselected" is learner-relative and unknowable at generation |
| 8 | Response-protocol annotations | **Skip** — out of scope; #8 owns the consumption side |

---

## Gate results

**Gate 1 — the R-9-1 diff gate (implementation step 8). PASS.**
Mechanically verified that 32 element types are byte-identical between `HEAD` and the
working tree across all four prompts, including every protected element named in the bar
(`<viability-requirement>`, `<pool-design-law>`, `<grid-design-law>`, `<required-constructs>`,
`<similarity-construction>`, `<near-duplicate-pair>`, `<orthodox-but-wrong>`,
`<near-duplicate-cell>`, `<near-duplicate-distractor>`, `<order-sensitive-pairs>`) and, beyond
the bar, `<stem-structure>`, `<abstraction-boundary>`, `<order-model>`, `<judgment-axes>`,
`<worked-examples>`, `<edge-cases>`, and both response protocols. Every `<internal-validation>`
block proven append-only. Step numbering contiguous in all four; no nested backtick fence
introduced.

**Gate 2 — the difficulty check (implementation step 9). PASS, with a finding.**
A full trial plus atom set was authored for each type. The invariant held in all four: every
distractor remained independently viable and failed only under projection.

The finding: **`viability_account` inverts FM-9-1's pressure gradient.** The field asks why a
wrong choice reads as *correct* on first pass. For a strong distractor this is easy to write —
the MCQ dry-run's orthodox-but-wrong choice was the canonical database-monitoring package, and
its near-duplicate was the canonical pool-utilization metric; both accounts wrote themselves.
For a weak distractor it is impossible: a choice rejectable on sight has no viability account,
because there is nothing to explain. The same holds per type — Ordering's account is
`<pool-design-law>` restated per item, and Matching's requires *naming which ≥2 prompts the
response pulls at*, which a surface-locked response cannot satisfy.

So the field a generator might have been tempted to route around is the one that makes weak
distractors *harder* to ship, not easier. The risk the issue created is now load-bearing
against itself. This was not designed in — it fell out of the OQ-6 resolution, and it is the
single strongest structural argument that baking is safe.

---

## Implementation order

Completed in this sequence.

1. Resolutions received for OQ 1–8; REQ-C-012 added to scope.
2. Canonical atom block authored once, label vocabulary parameterized.
3. `MCQ_GENERATION_PROMPT.md` — reference instantiation.
4. `MSQ_GENERATION_PROMPT.md` — variable key size, multiple `orthodox_but_wrong`, similarity clusters.
5. `ORDERING_GENERATION_PROMPT.md` — split `key_survival`, `near_duplicate_of` on a correct step.
6. `MATCHING_GENERATION_PROMPT.md` — per-pairing `key_survival` with rule-outs, two-phrase differentiator, null `near_duplicate_of`, matched-form orthodox exception.
7. REQ-C-012 cadence amendments at all 8 sites; `1-at-a-time` renamed `batch-generation`.
8. **Gate 1** — protected-element diff gate. Passed.
9. **Gate 2** — difficulty check, one trial per type. Passed; see the finding above.
10. Sizes measured and reported (FM-9-13, FM-9-12).
11. Rebase onto `main`. PR opened by the coordinator, not by this branch.
