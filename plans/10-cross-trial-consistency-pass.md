# Plan — C3: Cross-trial consistency pass (#10)

**Status:** Implemented — stage 2 complete. #10 was **re-scoped** after the stage-1 planning pass:
all three checks REQ-C-008 named were withdrawn and replaced. See §0 and parent amendment **A-12**.
**Parent plan:** `plans/5-frontload-question-generation.md`, **as amended** — the Amendments
section wins on conflict. A-12 is this issue's authority.
**Branch:** `feat/10-cross-trial-consistency`
**Target files:** `mcq-probe/skills/mcq-probe-0-router/SKILL.md`, one new script, `plugin.json`.
**Requirements owned:** ~~REQ-C-008~~ (withdrawn) · **REQ-C-016** · **REQ-C-017** · REQ-C-009.
**Failure mode owned:** FM-C-6.
**Siblings:** #8 (Generation Phase / Delivery Loop) · #9 (explanation baking). Both merged.
Last open sub-issue of Feature C (#5).

---

## 0. The re-scope — what changed and why

Stage 1 planned REQ-C-008 as written and surfaced 14 open questions. The coordinator's
resolution withdrew the requirement rather than defining it. **All three of its checks fail, for
three different reasons**, and the evidence is §3:

| REQ-C-008 check | Verdict | Why |
|---|---|---|
| No repeated scenario | **Redundant** | Already gated per slot in all four `<internal-validation>` checklists — MCQ:283, MSQ:282, ORD:392, MAT:437 — plus `<rule id="no-question-reuse">` in all four |
| Domain-anchor variety | **Incoherent** | `<domain-anchoring>` binds every trial to intake I3's single `DOMAIN`. The check contradicts the architecture rather than extending it. No artifact field exists, and none should |
| No clustered correct-answer position | **Statistically inert** | With four types drawn uniformly, E[MCQ slots] = 0.75 at N=3, 1.25 at N=5, 2.25 at N=9. P(≥3 MCQ slots) is **1.6% at N=3**. A clustering check needs ≥3 items to separate signal from noise, so it almost never has anything to judge |

As specified, #10 would have added regeneration pressure while catching essentially nothing —
the worst possible trade against FM-10-1. Two replacements, per A-12:

1. **`select_answer_position.py`** — the positional-bias concern is real; the *rejection* mechanism
   was the wrong tool. `MCQ_PROMPT`'s `position-assignment` step and `<answer-position>` both ask
   the **model** to "vary the position of the correct answer across the trials," which is exactly
   the randomization models are unreliable at, and exactly why `select_question_type.py` and
   `select_mcq_axis.py` exist. Fix it **by construction, in Pass 1** — nothing is regenerated, so
   FM-10-1's pressure is removed entirely rather than mitigated.
2. **G6 becomes an atom-completeness sweep** — stage-1 OQ-13's finding. Parent FM-C-3 and #9's
   FM-9-3 both promise atom coverage is verified in the consistency pass; REQ-C-008 never carried
   it. That is the check with real signal, and REQ-C-015's merge-window objection is moot now
   that #8 and #9 are both merged.

### Readback — the defining interpretation

1. **G6 is a second gate, never a substitute.** The per-slot `internal-validation` checklist runs
   inside G5 rule 3, before a slot is written, and is untouched. G6 runs after the last slot and
   checks a property no per-slot gate can see.
2. **The regeneration bar is identical.** A regenerated slot clears the same checklist as an
   original, with **no allowance because it is a retry**. A missing atom is evidence of a defect
   in the *choice* — regenerate the choice, never soften it. FM-10-1.
3. **The position draw constrains placement, never construction.** It fixes *where* the correct
   answer sits. The near-duplicate pair, the orthodox-but-wrong choice, and the independent
   viability of all four choices are unchanged.

---

## 1. Background / context

### Key globals

| Global | Before #10 | After #10 |
|---|---|---|
| MCQ correct-answer position | Assigned by model judgment at `MCQ_PROMPT` step `position-assignment`; "vary across the trials" ungated (§3) | Drawn by `SCRIPT_POSITION` in Pass 1; written to `key`; Pass 2 constructs around it |
| Positional balance over a batch | Unmeasured; model-dependent | **Exactly the pigeonhole floor ⌈m/4⌉, zero variance** (measured, §3) |
| Externalized randomization | 2 scripts — type, axis | 3 scripts — type, axis, **answer position** |
| Cross-trial checking | None | G6 atom-completeness sweep over the finalized batch |
| Atom coverage enforcement | `<emission-gate>` per slot, inside the prompt (#9) | Per-slot gate **plus** a batch-level sweep — the check FM-C-3 and FM-9-3 both promised |
| Regeneration on a G6 failure | n/a | Offending slot only; type, axis, `axis_rejected` and MCQ position held; ≤3 attempts; then accept and log internally |
| Generation Phase steps | G1–G5 | **G1–G6** |
| `SKILL.md` | 953 lines / 10,929 tokens | **1,046 lines / 13,009 tokens** (+93 lines, **+2,080 tokens, +19.0%**) — measured, `token-counter` |
| `plugin.json` version | `1.1.0` | `1.2.0` |

### Seam verification (verified against the live file, not inherited)

Pre-edit, `SKILL.md` was 953 lines: `## Generation Phase` 310, `### G5` 378, slot written 424,
**line 426** "When every slot is written, the batch is complete. Proceed to the Delivery Loop.",
`---` 428, `## Delivery Loop` 430.

**Line 426 routed around G6** — as written it handed control straight to delivery. It is
repointed: "When every slot is written, proceed to G6. The batch is not final until G6 has
passed it." This was the single edit most likely to be missed, and it would have made the whole
section dead text.

Post-edit: `## Generation Phase` 322, `### G6` 465, `## Delivery Loop` 512. G6 sits inside the
Generation Phase `##` block, so #6's split stays a cut at a `##` boundary.

### Pipeline after this change

Intake I1–I6 → Generation Phase (**G1** announce → **G2** `BATCH_SIZE = N` → **G3** prompt load →
**G4** Pass 1: type, axis, and MCQ answer position for every slot → **G5** Pass 2: construct,
validate, write → **G6** atom-completeness sweep, regenerating incomplete slots) → Delivery Loop
D1–D5 → Analysis Phase → Report.

---

## 2. Problem statement

Two defects, both of which only became addressable once #8 made the whole batch exist before
delivery.

1. **Positional bias is assigned by judgment and gated by nothing.** `MCQ_PROMPT` step
   `position-assignment` says "Vary the position of the correct answer across the trials. Do not
   consistently place the correct answer in the same position." There is **no corresponding
   `internal-validation` item in any of the four prompts** (§3) — so the instruction is
   unverifiable, and it asks the model for uniform randomness across a sequence, which is the
   failure mode this repo already solved twice by externalizing the draw to a script.

2. **Atom coverage is gated per slot but never over the batch.** #9's `<emission-gate>` blocks a
   slot's output when an atom is missing. Nothing checks the assembled batch. A gap is invisible
   at delivery: REQ-C-015's fallback silently authors the missing rationale live, the reasoning
   cost this feature exists to move quietly returns, and no signal is produced anywhere —
   parent FM-C-3.

---

## 3. Evidence — verified per-type inventory

Citations checked in the working tree at `mcq-probe/skills/mcq-probe-0-router/prompts/`. This
section is the basis for the withdrawal in §0 and is retained for traceability.

| Type | `key` shape | Within-trial placement rule | Gated? | Cross-trial placement rule | Gated? | Scenario item |
|---|---|---|---|---|---|---|
| mcq | one label, A–D | step `position-assignment` | No | *"Vary the position of the correct answer across the trials"* (MCQ:653) | **No** | MCQ:283 |
| msq | set ⊆ A–E, size 1–4 | step `position-assignment`; `<answer-position>` MSQ:378 | No | *"Vary their distribution across the trials in this session"* (MSQ:655) | **No** | MSQ:282 |
| ordering | ordered list over pool A–H, P = K+D, K∈[3,5], D∈[1,3] | *"correct sequence is not in label order"* | **Yes** ORD:389 | `<label-and-shuffle>` ORD:525 | **No** | ORD:392 |
| matching | injective 1…n → A…m, n∈[3,7], m∈[4,10], D∈[1,3] | *"correct pairing is NOT the identity diagonal"* | **Yes** MAT:431 | `<label-and-shuffle>` MAT:585 | **No** | MAT:437 |

Scenario non-reuse is separately gated by `<rule id="no-question-reuse">` in all four —
MCQ:567, MSQ:571, ORD:743, MAT:824 — over a type-specific unit set already **wider** than
"scenario" (answer choice, step, distractor, prompt, response). Hence "redundant" in §0.

Domain: `<domain-anchoring>` at MCQ:253, MSQ:252, ORD:351, MAT:384 directs every trial to intake
I3's `DOMAIN`. The only "change the domain anchor" instruction in the corpus is session-level,
for a re-run of an exhausted concept — MCQ:1036, MSQ:1113, MAT:1916. Hence "incoherent".

### Why the position fix is construction, not rejection

Exact enumeration over all 4^m assignments of the correct label for *m* MCQ slots, uniform —
the model's unconstrained behavior at best:

| m | pigeonhole floor ⌈m/4⌉ | E[max label count] | P(some label ≥ 3) |
|---|---|---|---|
| 3 | 1 | 1.69 | 0.062 |
| 5 | 2 | 2.48 | 0.414 |
| 9 | 3 | 3.87 | **1.000** |

A rejection-based check is trapped between these: a threshold of 3 is **unsatisfiable** at m=9
(the floor is 3) and fires on **41.4%** of batches at m=5, making regeneration the normal path
and FM-10-1's pressure continuous. And *m* is itself small — E[m] = N/4 with all four types
available.

`select_answer_position.py` sidesteps the trade. Measured over 20,000 simulated batches per size,
drawing uniformly from the least-used positions:

| m | pigeonhole floor | observed max | mean max | P(slot 0 = A) |
|---|---|---|---|---|
| 3 | 1 | **1** | 1.00 | 0.248 |
| 5 | 2 | **2** | 2.00 | 0.251 |
| 9 | 3 | **3** | 3.00 | 0.245 |
| 10 | 3 | **3** | 3.00 | 0.251 |

The floor is hit exactly, every time, with **zero variance** — against the model's E[max] of
1.69 / 2.48 / 3.87 — while the first slot stays uniform at 0.25, so balance costs no
predictability. Nothing is regenerated to achieve it.

---

## 4. Design decisions

| Decision | Resolution | Source |
|---|---|---|
| REQ-C-008's three checks | **Withdrawn** — redundant, incoherent, and statistically inert respectively (§0, §3) | Coordinator; parent **A-12** |
| Positional bias | Fixed **by construction** in Pass 1, never by rejection. Nothing is regenerated for position | A-12 |
| Script scope | **MCQ only.** Ordering and Matching have no assignable correct-answer position — their `<label-and-shuffle>` is within-trial and already gated. MSQ's correct set is content-constrained; recorded as a follow-up, not implemented | A-12; coordinator |
| Where the drawn position is stored | Written straight to **`key`**. For MCQ the key label *is* the correct answer's position, so the existing binding field carries it and **no schema field is added** | Parent §Artifact schema ("field names are binding"); minimal-change principle |
| Script argument | **`--assigned`**, not `--exclude` — see §8 OQ-A. Deliberate, documented divergence | This implementation; flagged for review |
| Script fallback | Assign the label used by fewest earlier MCQ slots, ties in `A,B,C,D` order. Mirrors REQ-MCQ-E-002's "first not yet assigned" structure; registered as **REQ-MCQ-E-004** | Coordinator ("mirroring E-002/E-003") |
| G6's substance | Atom-completeness sweep over the finalized batch, per the type's coverage rule | A-12; stage-1 OQ-13 |
| G6 vs. per-slot validation | **Additive second gate.** G5 rule 3 stays primary and is untouched, never bypassed or softened | `CLAUDE.md`; parent FM-C-1; brief |
| Regeneration granularity | Offending slot only; complete slots untouched | REQ-C-009 |
| **Regeneration holds type and axis** | A regenerated slot keeps `question_type`, `axis`, `axis_rejected`, and (MCQ) its Pass-1 position. Re-drawing the axis would break batch axis-uniqueness and silently corrupt the report's Axis Coverage | Coordinator, stage-1 OQ-10 |
| Regeneration form | Slot rewritten **whole** through the type's prompt including `explanation-baking`; never patched in place | FM-10-7 |
| Regeneration bar | Identical to an original. No retry allowance | `CLAUDE.md`; parent FM-C-1 |
| Cap | 3 per slot, then accept and log internally. **No batch-level cap** — the per-slot cap already bounds the worst case | FM-C-6; coordinator, stage-1 OQ-11 |
| Cap-exhaustion record | **Internal only.** No schema field, no report section. Delivery's atoms-absent fallback (REQ-C-015) already handles the residue, so the log is diagnostic, not load-bearing | Coordinator, stage-1 OQ-12 |
| Line 426 | Repointed through G6 | Stage-1 finding; coordinator |
| Citation discipline | Prompt elements cited **by name** (`position-assignment`, `internal-validation`, `explanation-baking`), never by step or line number — #9 already shifted them and #24 will again | Plan 8 FM-8-2 precedent |
| `prompts/` | **Not touched.** MCQ step `position-assignment` and `<answer-position>` stay as written; the script supplements them | Coordinator; #24 |
| Version | `plugin.json` `1.1.0` → `1.2.0` | Coordinator; #18 OQ-1 |

---

## 5. Requirements

| ID | Requirement | Scope |
|---|---|---|
| ~~REQ-C-008~~ | ~~A consistency pass runs over the finalized batch: no repeated scenario, no clustered correct-answer position, domain-anchor variety~~ — **withdrawn by A-12** | — |
| **REQ-C-016** | `SCRIPT_POSITION` is drawn in Pass 1 for every `mcq` slot and fixes that slot's `key`; Pass 2 constructs the choices around it. MCQ only | New script; `SKILL.md` File Path Constants, Active Constraints, G4 step 3, G5 rule 4, REQ-MCQ-E-004 |
| **REQ-C-017** | G6 sweeps the finalized batch and verifies every slot's `explanation` block against its type's coverage rule; an incomplete slot is regenerated, a complete slot untouched | `SKILL.md` — new `### G6`; Active Constraints |
| REQ-C-009 | A consistency failure regenerates only the offending trial, then re-runs the pass | `SKILL.md` — G6 regeneration block |
| REQ-MCQ-E-004 | `SCRIPT_POSITION` non-zero exit falls back to the least-used label, ties in `A,B,C,D` order, logged internally | `SKILL.md` — Error Handling |

**Derived, FM-C-6:** 3 regeneration attempts per slot; on exhaustion accept and log internally.

**Non-goals.** No edit to any file under `prompts/` (#9 landed there; #24 restructures). No MSQ
position draw (§8 OQ-B). No on-disk persistence (#7). No file split (#6). No endless-mode
windowing (#4). **No change to what a distractor must satisfy** — no construction rule, viability
rule, pool/grid law, required construct, banned-language list, or `internal-validation` item is
weakened, reordered around, or made conditional.

---

## 6. Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| **FM-10-1** | **Distractor quality traded for distinctness under regeneration pressure** | A rejection mechanism rewards trials that are easy to make *different* over trials that are hard to answer | Distractors become rejectable on surface reading, invisibly — the trial that ships passed a distinctness check, not a difficulty check | **No, and structurally removed.** The re-scope deleted the mechanism: position is fixed by construction, so **nothing is regenerated for distinctness**. What regeneration remains (G6) fires on a *missing atom*, and #9's Gate-2 finding shows that pressure runs the right way — a weakened distractor has **no `viability_account` to write**, so softening makes the slot *harder* to ship, not easier. G6 states this in as many words |
| FM-10-2 | Cap exhaustion ships a slot with incomplete atoms | 3 regenerations still incomplete | That slot's breakdown is authored live at delivery | **Accepted** — FM-C-6. REQ-C-015's fallback covers it with full coverage; only provenance degrades. Logged internally |
| FM-10-3 | G6 regeneration churn | A rewritten slot fails the sweep again | Bounded: ≤3 per slot, ≤3 × `BATCH_SIZE` = 27 at N=9 | **Accepted.** Per-slot cap only; no batch-level cap needed, since G6's check is per-slot and a rewrite cannot invalidate another slot |
| FM-10-4 | ~~Threshold below the pigeonhole floor~~ | ~~m=9 with a "no label 3+" rule~~ | ~~27 wasted constructions for zero effect~~ | **Moot** — no threshold exists. The clustering check is withdrawn; §3's figures are why |
| FM-10-5 | Regeneration re-draws the slot's axis | Regeneration re-enters the construction path, which contains an axis-refit step | Batch axis-uniqueness (REQ-C-002/004) breaks; the report's Axis Coverage silently misstates what was tested | **No.** G6 step 1 holds `question_type`, `axis`, `axis_rejected` and the MCQ position explicitly, with the reason stated inline |
| FM-10-6 | G6 read as making G5 rule 3 optional | Two gates exist; the later looks authoritative | Per-slot `internal-validation` skipped or softened — the doctrine failure `CLAUDE.md` names | **No.** G6 opens by stating it is a second gate, that G5 rule 3 is unchanged and primary, and that G6 never substitutes for it |
| FM-10-7 | Regenerated slot's atoms patched rather than rebuilt | Regeneration implemented as filling in the missing field | The atom exists but was authored detached from the choice it describes — FM-9-4 by another route | **No.** G6 step 2 requires the slot be rewritten **whole** through `internal-validation` and `explanation-baking`; patching in place is forbidden by name |
| FM-10-8 | G6 findings rendered to the learner | A "pass" that finds problems defaults to reporting them | A completeness report naming stems and keys leaks the answer key before trial 1 | **No.** Parent FM-C-2; G6 states it presents nothing and reports nothing |
| FM-10-9 | The position draw is applied to non-MCQ slots | The draw sits in a per-slot loop | An Ordering slot gets a meaningless `key`, corrupting grading | **No.** G4 step 3 is explicitly gated "`mcq` slots only" and says "Skip this draw entirely" for the other three |
| FM-10-10 | Pre-set `key` mistaken for a constructed answer | Pass 1 writes `key` before content exists | A reader assumes the correct answer's *content* was decided in Pass 1 | **No.** The Batch Artifact section states that the drawn label fixes the *position* and that Pass 2 constructs the choices around it. Nothing about choice content moves |
| FM-10-11 | `SCRIPT_POSITION` unreachable on every call | Broken interpreter or missing script | The fallback fires on every slot: balance holds, but the *order* becomes the fixed cycle A, B, C, D, … | **Accepted, flagged.** REQ-MCQ-E-004 says so explicitly and tells the reader to treat it as a broken environment, not a normal path — the same discipline as the launcher note under File Path Constants |

---

## 7. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-10-1 | `--assigned` diverges from the two sibling scripts' `--exclude` and a later reader "fixes" it | Medium | Medium | The divergence is deliberate and documented in the script docstring, §4, and §8 OQ-A. `--exclude` would be a lie: with >4 MCQ slots every position must recur, so nothing is excluded |
| R-10-2 | ~~A tight threshold makes regeneration the norm~~ | — | — | **Moot** — the threshold and the check are withdrawn |
| R-10-3 | Schema drift | **Closed** | — | No field added. The drawn position rides in the existing `key`; the cap-exhaustion log is internal only |
| R-10-4 | New text cites prompt step or line numbers, which #9 already shifted and #24 will shift again | Low | Medium | Citation-by-name discipline applied throughout; verified — the new text names `position-assignment`, `internal-validation`, `explanation-baking` and no numbers |
| R-10-5 | `SKILL.md` on-invoke cost | **Realized** | Low | +2,080 tokens (+19.0%), 10,929 → 13,009. Measured, not estimated. #6's gating is the structural relief |
| R-10-6 | #6's split becomes non-mechanical | Low | Low | G6 is a `###` inside the existing Generation Phase `##` block; no section spans the phase boundary |
| R-10-7 | G6 written as prose judgment, hence unverifiable | **Closed** | — | Each of the six checks is a stated predicate over named artifact fields with explicit per-type counts |
| R-10-8 | The model ignores the drawn position and places the correct answer elsewhere | Medium | Medium | Stated twice — Active Constraints ("Never assign an MCQ correct-answer position by judgment") and G5 rule 4. **Behavioral verification required** (§10 step 9); it cannot be confirmed by reading the diff |

---

## 8. Open questions

Stage-1's 14 are all resolved or moot; the disposition is recorded so the withdrawal is visibly a
decision rather than an omission.

| Stage-1 # | Disposition |
|---|---|
| OQ-1, OQ-2, OQ-3, OQ-14 | **Dropped** — the scenario check is withdrawn as redundant (§0). Already gated in all four `<internal-validation>` checklists and by `<rule id="no-question-reuse">` |
| OQ-6, OQ-7 | **Dropped** — the clustering check is withdrawn as statistically inert (§0, §3) |
| OQ-8 | **Dropped** — domain-anchor variety is withdrawn as incoherent; it contradicts `<domain-anchoring>` and intake I3 |
| OQ-4, OQ-5 | **Resolved** by scoping `SCRIPT_POSITION` to MCQ. Ordering and Matching have no assignable position; MSQ is OQ-B below |
| OQ-9 | **Moot** — an atom sweep is per-slot, so the offending slot is never ambiguous |
| OQ-10 | **Resolved: hold.** Type, axis and `axis_rejected` are preserved across regeneration |
| OQ-11 | **Resolved:** per-slot cap of 3 stands; no batch-level cap |
| OQ-12 | **Resolved:** internal only — no schema field, no report section |
| OQ-13 | **Resolved:** it is now the substance of G6 |

Carried forward:

| # | Question | Blocker for? |
|---|---|---|
| OQ-A | `select_answer_position.py` takes **`--assigned`**, where `select_question_type.py` and `select_mcq_axis.py` take `--exclude`. Position assignment is a balancing problem, not an exclusion one — with >4 MCQ slots every position must recur, so an `--exclude` argument would not exclude, and the axis script's exhaustion-relaxation produces *unbalanced* draws, which is the opposite of what is wanted here. Recorded as a deliberate, documented divergence. Confirm, or direct a rename | Nothing — implemented and working. Interface-consistency review only |
| OQ-B | **MSQ positional bias is unaddressed.** `<answer-position>` (MSQ:378) and step `position-assignment` carry the same ungated "vary across trials" instruction as MCQ, and MSQ has the same expected slot share. Its correct *set* is content-constrained, so a free draw is not available — but a draw over set **size**, or over which labels carry the key, may be. Explicitly out of scope per A-12 | A follow-up issue. Not this one |
| OQ-C | **Ordering and Matching cross-trial `<label-and-shuffle>` variation stays ungated** (§3). "Do not cluster distractor letters at the end of the alphabet" is a real property with no checklist item and no script. Not in A-12's scope | A follow-up issue, if the leak is judged material |

---

## 9. Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `mcq-probe/skills/mcq-probe-0-router/scripts/select_answer_position.py` | **Create** | Balanced MCQ correct-answer position draw; `--assigned`; exit 0/1; unknown-label error | REQ-C-016 |
| `mcq-probe/skills/mcq-probe-0-router/SKILL.md` | Modify | `SCRIPT_POSITION` constant + environment-note bullet ("six paths" → "seven"); 2 Active Constraints bullets; Batch Artifact note on the pre-drawn MCQ `key`; G4 heading + step 3; G5 rule 4 (three rules → four); **new `### G6`**; line-426 repoint; Error Handling `REQ-MCQ-E-004` | REQ-C-016, REQ-C-017, REQ-C-009, FM-C-6 |
| `mcq-probe/.claude-plugin/plugin.json` | Modify | `1.1.0` → `1.2.0` | Version-keyed cache; the plugin will not re-sync without it (#18 OQ-1) |
| `plans/5-frontload-question-generation.md` | Modify | Amendment **A-12** appended verbatim; REQ-C-008 struck in the Requirements table and REQ-C-016 / REQ-C-017 registered | The parent must not still read REQ-C-008 as live while `SKILL.md` cites IDs that appear nowhere in it |
| `plans/10-cross-trial-consistency-pass.md` | Modify | This document, rewritten for the re-scope | Traceability |
| `mcq-probe/skills/mcq-probe-0-router/prompts/*.md` | **None** | — | #9 landed there; #24 restructures. Zero bytes changed |

---

## 10. Implementation order

Steps 1–8 executed. Step 9 is a post-merge behavioral gate.

1. Coordinator resolutions received; #10 re-scoped; A-12 authored.
2. `select_answer_position.py` written and smoke-tested — first slot, partial batch, full cycle, unknown label, unknown argument.
3. Balance verified over 20,000 simulated batches at m = 3, 5, 9, 10 (§3).
4. `SKILL.md` — `SCRIPT_POSITION` constant, environment-note bullet, "six paths" → "seven".
5. `SKILL.md` — Active Constraints: position-draw bullet and G6 bullet.
6. `SKILL.md` — Batch Artifact note; G4 heading and step 3; G5 rule 4; **`### G6`**; line-426 repoint; `REQ-MCQ-E-004`.
7. `plugin.json` → `1.2.0`; parent plan amended.
8. **Gate 1 — the anti-softening diff gate. Passed.** `git diff --stat` shows zero bytes changed under `prompts/`; no `internal-validation` item, viability rule, pool/grid law, required construct or banned-language list touched; G5 rule 3 unedited; no prompt step or line number cited in new text. **Non-delegable.**
9. **Gate 2 — behavioral, post-merge.** Re-sync the plugin cache, restart, run a bounded session and confirm: (a) the correct answer lands at the drawn label on every MCQ slot (R-10-8 — the one risk a diff cannot close); (b) nothing is presented until G6 completes; (c) G6 emits nothing to the learner; (d) axes stay unique after any regeneration; (e) a wrong answer's breakdown covers every choice not in the key.
