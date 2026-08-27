# Plan — Ordering Question Type (mcq-probe)

**Status:** Draft — reads confirmed (OQ 1–5) and OQ 6 resolved (re-draw axis + intake gate) on 2026-08-27. Awaiting execute signal. No implementation until an explicit go.
**Date:** 2026-08-27
**Branch:** `claude/ordering-question-type-ce13aa`
**Target skill:** `mcq-probe`

---

## 0. Readback — the defining interpretation

Everything below rests on three reads of the spec (*"Has a list of 3–5 responses to complete a specified task. You must select the correct responses and place the responses in the correct order to receive credit for the question."*). If any is wrong, large parts of this plan change.

1. **Selection has teeth.** "Select the correct responses" only means something if the pool contains distractors. Pool = K correct steps + D distractors; the learner must reject distractors *and* order the survivors.
2. **Credit is binary.** "To receive credit" = all-or-nothing, consistent with the existing MCQ/MSQ correct/incorrect grade. No partial credit.
3. **3–5 bounds the correct sequence** (the steps that complete the task), not the pool. The pool is larger.

Open Questions 1–3 confirmed by the user on 2026-08-27.

---

## 1. Background / context

`mcq-probe` is a judgment-probe evaluation skill. An orchestrator (`SKILL.md`) runs an intake phase, an N-trial loop, and an analysis phase producing a Markdown report. Per trial, `select_question_type.py` draws the type (currently `mcq`/`msq`, 50/50) and `select_mcq_axis.py` assigns one of 9 judgment axes (no consecutive repeat, no reuse within session). Two XML generation prompts govern construction and are loaded once on Trial 1.

**The skill's central property — the thing this feature must preserve:** difficulty is a *structural* property of the answer pool, not a setting. Every wrong answer is independently viable in isolation and fails **only** under forward projection along the assigned axis. Two devices enforce it — the **near-duplicate pair** and the **orthodox-but-wrong** choice. A wrong answer eliminable by surface reading is a construction **defect** and is regenerated.

### Globals after this change

| Global | Value | Note |
|---|---|---|
| Type token (script stdout) | `ordering` | joins `mcq`, `msq` |
| Display label | **ORD** | on its own line, matching MCQ/MSQ |
| K — correct steps | 3–5, scenario-driven | the ordered procedure length |
| D — distractors | 1–3 | ≥1 so selection is a real operation; 3 is a hard ceiling |
| P — pool size | K + D = 4–8 | labeled A…H |
| Grade | binary | exact ordered-sequence match |
| K disclosure | disclosed in prompt | "Arrange the 4 steps…" — D is never disclosed |
| Order model | strict total order, **axis-forced, surface-sort resistant** | every adjacency forced under the axis; not recoverable by generic procedural intuition |
| Axes | 9, reused unchanged | `select_mcq_axis.py` is axis-type-agnostic |
| Type distribution | 1/3 each (procedural concepts) | non-procedural concepts exclude `ordering` at intake → mcq/msq 50/50 |
| Signature constructs | orthodox-but-wrong **inclusion** (≥1), near-duplicate **distractor** (≥1), order-sensitive **pairs** (≥2) | ordering analogues of the MCQ/MSQ devices |

### Pipeline

Intake (now includes a one-time procedural determination — see REQ-ORD-F-010) → trial loop. Per trial: `select_question_type.py` now returns `mcq`/`msq`/`ordering`; `select_mcq_axis.py` assigns the axis; the matching generation prompt (loaded once on Trial 1) constructs the trial. An ordering trial presents a task scenario plus a shuffled labeled pool; the learner replies with an **ordered** list of labels; evaluation decomposes the response into selection errors and ordering errors, then the binary grade feeds the same analysis phase and report as MCQ/MSQ.

---

## 2. Problem statement

MCQ and MSQ probe judgment among *parallel* choices — the axis discriminates which option survives. Neither probes whether the learner commands a **procedure**: which steps belong, and in what forced order. Ordering fills that gap and makes the axis *structural* — the axis dictates the forcing dependency between steps (a `risk` gate, a `time` precedence, a `boundary-condition` precondition, an `observability` detection window) rather than merely separating alternatives.

The hard constraint is preserving the binary grade under the skill's difficulty bar. Two ways it can fail:

- **Grading breaks** if the correct sequence contains an order-independent adjacency — two valid orders, no single correct answer.
- **Difficulty leaks** if distractors are rejectable on sight (out-of-scope) or if the order is recoverable by generic procedural intuition ("setup first, cleanup last"). Either makes the trial surface-solvable and violates the skill's whole premise.

Ordering is therefore the hardest of the three types by construction. That is intended.

---

## 3. Hardness transfer — one-to-one mapping (the load-bearing section)

This is the justification for every construction rule that follows. Each MCQ/MSQ difficulty mechanism maps to an ordering analogue that must hold with equal force.

| MCQ/MSQ mechanism | What it forces | Ordering transfer | Status |
|---|---|---|---|
| Every wrong answer independently viable | No surface elimination | **Every pool item is a plausible step in *this* task.** No out-of-scope items. Distractors are *false inclusions*. | Governs the whole pool |
| Wrong fails only under forward projection | Reasoning, not recall | **Both** operations projection-gated: which steps to reject *and* the order | Extended to two operations |
| Near-duplicate pair | Precision under one decisive phrase | (a) **selection**: a distractor twinned with a correct step, same surface action, diverging at one embedded qualifier/precondition decidable only under projection; (b) **ordering**: order-sensitive pairs that look swappable but are projection-forced | Preserved, twice |
| Orthodox-but-wrong | Punishes convention over reasoning | **Orthodox-but-wrong inclusion**: a step from the *textbook* version of this procedure that expertise pulls you to include, but that breaks under this scenario's axis | Preserved; stronger — expertise actively misleads toward a wrong pick |
| Surface features aren't the differentiator | Defeats pattern-matching | **Correct order must resist generic procedural heuristics.** The axis, not intuition, decides the order. Counterintuitive precedence preferred. | New explicit requirement |
| No banned language / quality signals | No heuristic shortcuts | Unchanged; same banned lists | Preserved |

**Correction from the initial design:** the first draft included a "plausible-but-out-of-scope distractor" construct. That is itself a transfer failure — an out-of-scope step is rejectable on first read without projecting the axis. It is **removed**. All distractors are now false inclusions.

---

## 4. Pool-design law + required constructs

**Law.** Every pool item — correct step or distractor — must read as a legitimate step in this task. No item is rejectable as unrelated, broken, or obviously misplaced. Selection and ordering are both decidable only by forward projection under the axis.

**Required constructs (per trial):**

1. **Orthodox-but-wrong inclusion** (≥1) — a standard, professionally recognized step for this class of task that fails under *this* scenario's axis. Expertise pulls you to include it.
2. **Near-duplicate distractor** (≥1) — twinned with a correct step: same surface action, diverging at one embedded phrase (target, precondition, qualifier) that matters only under projection. The learner must pick the correct twin and reject the distractor twin.
3. **Order-sensitive pairs** (≥2) — adjacencies in the correct sequence whose relative order looks arbitrary on first read but is forced under the axis. The sequence as a whole must resist common-sense sorting.

**Forbidden (transfer failures):** out-of-scope/unrelated steps · factually broken steps · orderings recoverable by generic "setup-first/cleanup-last" intuition.

---

## 5. Design decisions

| Decision | Resolution |
|---|---|
| Pool composition | K correct + D distractors (1–3). Selection is graded. |
| Grade model | Binary. Correct iff learner's ordered list exactly equals the correct sequence — right items, no distractors, none missing, exact order. |
| Order model | Strict total order: every adjacent pair forced by an axis-driven dependency; no two correct steps order-independent. Keeps the binary grade defensible. |
| Order difficulty | Forcing must be **axis-projection-decidable, not common sense.** The sequence must resist generic procedural sorting. Strict total order is necessary but not sufficient for difficulty; surface-sort resistance is the added requirement. |
| Disclose K | Yes. Prompt states the step count ("Arrange the 4 steps…"), mirroring MSQ's `(Select N.)`. D is never disclosed. |
| Distractor policy | All distractors are **false inclusions** (plausible steps in this task). No out-of-scope distractors. |
| Signature constructs | Orthodox-but-wrong inclusion (≥1), near-duplicate distractor (≥1), order-sensitive pairs (≥2). |
| Step substance | 1–2 sentences, action-oriented, carrying enough embedded detail (targets, preconditions, qualifiers) to support near-duplicate construction. A bare action verb is insufficient. |
| Axis source | Reuse `select_mcq_axis.py` unchanged. All 9 axes apply; the axis defines the forcing dependency and the distractor failure mode. |
| Intake procedural gate | At intake, determine once whether the concept affords an ordered, dependency-bearing procedure. If **non-procedural**, exclude `ordering` from the type draw for the whole session (`select_question_type.py --exclude ordering`). No ordering trial is ever attempted for such a concept. See REQ-ORD-F-010. |
| Axis re-draw (no type substitution) | For a procedural concept, if the assigned axis cannot force *this* trial's order, **re-draw the axis** (`select_mcq_axis.py --exclude [used + rejected]`, up to 3 attempts). If re-draws exhaust, hold the axis and reconstruct the scenario to one the axis can force. The trial type is **never** substituted mid-trial. See REQ-ORD-E-003. |
| Near-duplicate ambiguity | If a near-duplicate cannot be made genuinely wrong without over-specifying the stem to the point of leaking the answer, regenerate the pair or the trial. See edge case + FM-8. |
| Type distribution | Equiprobable 1/3. Revisit after observing pass rates. |
| Display token | **ORD**. Matches MCQ/MSQ three-letter pattern. |

---

## 6. Construction sequence (core of `ORDERING_GENERATION_PROMPT.md`)

1. **axis-confirmation** — use the axis from `select_mcq_axis.py`; do not signal it.
2. **axis-fit / re-draw** — confirm the assigned axis can force this trial's order for the concept. If not, re-draw the axis via `select_mcq_axis.py --exclude [used + rejected axes]` (up to 3 attempts); on exhaustion, hold the axis and reconstruct the scenario to one the axis can force. Never substitute the trial type here — the non-procedural-concept case is already excluded at intake (REQ-ORD-F-010). A rejected axis is not marked used and only the finally-used axis is recorded (REQ-ORD-F-016).
3. **task-scenario-construction** — a scenario specifying a *task* whose correct completion is an ordered procedure of K steps, the ordering forced by the axis. Neutral prompt, banned language excluded. Disclose K, not D. Where the near-duplicate depends on a gating frame (see FM-2), the stem must state that the gate is *the* decision the next step fires on.
4. **correct-sequence-construction** — write the K steps *as an ordered list first*. For each adjacency, establish the forcing dependency under the axis. Verify strict total order — no order-independent pair. Plant ≥2 order-sensitive pairs that look swappable on first read. Verify the whole sequence resists generic procedural sorting.
5. **distractor-construction** — write D distractors (1–3), each a plausible inclusion. Each fails **selection** for a distinct reason under the axis. Include ≥1 orthodox-but-wrong inclusion and ≥1 near-duplicate distractor twinned with a correct step.
6. **label-and-shuffle** — assign pool items to labels A…P in shuffled order; the correct sequence must not be in label order; vary across trials.
7. **internal-validation** — run the checklist; regenerate on any failure.
8. **output** — **ORD** on its own line, task scenario, pool, closing prompt: *"Arrange the [K] steps that complete this task, in order (ordered list of letters)."* Stop. Wait.

### Internal-validation checklist

- [ ] Assigned axis used and not signaled.
- [ ] Concept affords a forcing structure under the axis (else fallback taken).
- [ ] Topic keyword unavoidable in the task and the pool.
- [ ] Correct sequence is a strict total order — every adjacency forced under the axis; no order-independent pair.
- [ ] ≥2 order-sensitive pairs; each looks swappable on first read; correct order decidable only under projection.
- [ ] The correct order is **not** recoverable by generic procedural heuristics (surface-sort resistant).
- [ ] Every pool item is a plausible inclusion in this task — no out-of-scope item.
- [ ] Each distractor fails selection for a distinct reason, only under projection.
- [ ] ≥1 orthodox-but-wrong inclusion present.
- [ ] ≥1 near-duplicate distractor twinned with a correct step; differentiator decisive only under projection.
- [ ] Each near-duplicate is genuinely wrong to include without the stem leaking the answer (else regenerate — FM-8).
- [ ] K ∈ [3,5]; D ∈ [1,3]; pool P = K+D labeled contiguously from A.
- [ ] Correct sequence is not in label order.
- [ ] K disclosed, D not.
- [ ] No banned language (reuse MCQ/MSQ banned lists).
- [ ] Scenario fresh this session.

---

## 7. Feedback protocol

**Correct** (exact ordered match):
1. Acknowledge briefly ("Correct." / "Right." / "That's it.").
2. State the axis in one sentence.
3. Why the sequence survives — each forced precedence individually.
4. Each distractor's selection failure, individually; name the orthodox-but-wrong inclusion.
5. Resolve the order-sensitive pairs — why the reverse order fails under projection; resolve the near-duplicate — what one phrase differentiates the twins.
6. Proceed to next trial, or to analysis if this was trial N.

**Incorrect** (any deviation):
1. State the axis first.
2. Decompose the error:
   - **Selection** — for each distractor wrongly included, why it fails selection under the axis; for each correct step omitted, why it belongs.
   - **Ordering** — for each transposed forced pair among correctly-selected steps, why the order is forced and why the learner's order fails projection.
3. State the correct sequence directly: `X → Y → Z → W`.
4. Why the correct sequence survives — each precedence individually.
5. Each distractor individually; name the orthodox-but-wrong inclusion; resolve the near-duplicate.
6. No nudge, no recovery exchange. Proceed.

---

## 8. Worked example (canonical)

**Axis:** risk · **Concept:** zero-downtime column rename (expand-contract) · **K=5, D=2, pool A–G.**

> Task: rename a heavily-read column `email` → `email_address` on a live, high-traffic service with no downtime and no lost writes. Arrange the **5** steps that complete this task, in order.
>
> A. Add `email_address` as `NOT NULL` with a default value, to enforce integrity from creation. · B. Add a nullable `email_address` column; no backfill yet. · C. Deploy code that writes **both** columns and reads the **old** one. · D. Backfill `email_address` from `email` in batches. · E. Take a brief exclusive lock on the table and rename the column atomically. · F. Deploy code that reads the **new** column, still writing both. · G. Drop `email` and stop writing to it.

**Correct sequence: B → C → D → F → G.** Reject A, E.

**Forcing chain (strict total order under risk):**

| Adjacency | Why forced | Surface read |
|---|---|---|
| B → C | Can't dual-write to a column that doesn't exist. | Hard dependency. |
| C → D | Dual-writes must be live before backfill, else writes arriving in the gap update only `email`, leaving `email_address` stale. | **Order-sensitive** — inverts the "migrate data first, then update code" intuition. |
| D → F | Reading the new column requires backfill complete, else old rows return null. | Order-sensitive. |
| F → G | Dropping old requires readers already switched to new; dropping while reads still hit old = outage. | Forced. |

**Distractors:**
- **E (orthodox-but-wrong inclusion).** Locking for an atomic rename is the textbook consistency-safe move — competent, rigorous. It fails because the lock *is* the downtime the task forbids. Independently viable; silent until projected against the zero-downtime constraint.
- **A (near-duplicate of correct step B).** Same action — add the column — diverging at `NOT NULL + default` vs `nullable`. A looks *more* rigorous. Under projection, `NOT NULL` on a large populated table triggers a rewrite/long lock (downtime) and breaks the additive-expand pattern. Pick B, reject A. Differentiator decisive only under projection.

Every one of the seven items is a real migration step; nothing is rejectable on sight. Unique valid sequence — nothing can precede B, nothing reads before backfill, nothing drops before reads switch.

---

## 9. Limit-test example (justifies edge cases in §11)

Built to break the type: hostile axis (**observability**, weakest natural fit to a procedure), the order-independence trap (FM-1), max size (K=5, D=3, pool of 8), and a near-duplicate pushed to the defensibility boundary (FM-2 / R-3).

**Axis:** observability · **Concept:** canary release of a payment-settlement change · **K=5, D=3, pool A–H.**

> Task: roll out a change to the settlement calculation in a live payment service using a canary, so that a settlement-mismatch regression is caught while it affects the fewest transactions. Arrange the **5** steps that complete this task, in order.
>
> A. Replay full production traffic against the new code as shadow requests and diff outputs offline before any live canary. · B. Route 1% of live traffic to the canary. · C. Emit the settlement-mismatch metric from the new path and confirm it is flowing before any traffic reaches the canary. · D. Hold at 1% and watch error-rate and latency dashboards for five minutes, then widen. · E. Widen to 50% once the observed signal stays clean through the hold. · F. Hold at 1% and watch the settlement-mismatch metric across a full settlement cycle, then widen. · G. Enable verbose debug logging on the canary so any anomaly is captured for later analysis. · H. Promote to 100% and decommission the old path.

**Correct sequence: C → B → F → E → H.** Reject A, D, G.

**Forcing chain:**

| Adjacency | Why forced under observability | Surface read |
|---|---|---|
| C → B | Route traffic *after* the regression metric is confirmed flowing; traffic before the signal means the canary runs blind. | **Looks parallel** ("instrument and route are both setup") — the FM-1 trap. Strictly forced. |
| B → F | Cannot observe the canary's signal before the canary has traffic. | Hard dependency. |
| F → E | Widen only after an observation window sized to the failure's latency; settlement mismatches settle slowly, so widening early blinds you. | **Looks reorderable** ("set threshold, then watch") — forced. |
| E → H | 100% only after the 50% stage holds clean. | Forced. |

**Distractors:**
- **A (orthodox-but-wrong inclusion).** Shadow/mirror-and-diff is a rigorously recommended pre-rollout practice. It fails here because shadow requests don't commit real settlements, so a settlement-mismatch regression produces no observable settlement outcome — the signal is structurally invisible under shadowing.
- **G (untimely-observation distractor).** Verbose logging "for later analysis" surfaces the fault *after* the damage, with no timely signal to gate widening. Observation that doesn't observe in time to act.
- **D (near-duplicate at the defensibility boundary).** D and F are the same surface action — hold at 1%, observe, widen — diverging at *what* is observed and *for how long*. D watches golden signals for 5 minutes; F watches the settlement-mismatch metric across a settlement cycle. D looks *more* concrete. It fails because error-rate/latency never surface a settlement-*correctness* regression and 5 min ≪ settlement latency, so D's widen decision fires on evidence that cannot contain the fault.

**Limit finding.** D is the ceiling. "Watch the golden signals too" is never bad advice, so D risks reading as a legitimate *extra* step (two valid readings → ungradeable). The hole is closable only by framing the hold in the stem as *the gate the widen decision fires on* — under which framing, including D is gating on the wrong evidence, a genuine error. This proves two things the type needs codified: (1) the stem must sometimes over-specify the gate to preserve a single answer, and (2) if it can't be over-specified without leaking the answer, regenerate. Both become edge cases in §11.

---

## 10. Requirements

| ID | Requirement | Scope |
|---|---|---|
| REQ-ORD-F-001 | `select_question_type.py` returns one of `mcq`/`msq`/`ordering` | script |
| REQ-ORD-F-002 | On Trial 1, load `ORDERING_PROMPT` alongside MCQ/MSQ prompts; unreadable → halt | SKILL.md |
| REQ-ORD-F-003 | Ordering trial presents **ORD** on its own line, a task scenario, a shuffled labeled pool (A…P), and a closing prompt disclosing K but not D | ORDERING_PROMPT |
| REQ-ORD-F-004 | Correct sequence is a strict total order under the axis; ≥2 order-sensitive pairs; the sequence resists generic procedural sorting | ORDERING_PROMPT |
| REQ-ORD-F-005 | Every pool item is a plausible inclusion (no out-of-scope); ≥1 orthodox-but-wrong inclusion; ≥1 near-duplicate distractor twinned with a correct step; each distractor fails selection for a distinct reason, only under projection | ORDERING_PROMPT |
| REQ-ORD-F-006 | Parse response as an **ordered** list of labels; order is significant; repeated or out-of-pool label → resubmit | SKILL.md |
| REQ-ORD-F-007 | Grade correct iff ordered selected sequence == correct sequence exactly | SKILL.md |
| REQ-ORD-F-008 | Feedback decomposes error into selection (false inclusions, omitted steps) and ordering (transposed forced pairs); each addressed individually; name the orthodox-but-wrong inclusion; resolve the near-duplicate | SKILL.md / ORDERING_PROMPT |
| REQ-ORD-F-009 | Internal record uses `question_type: ordering` and populates `probe_target` (the procedure aspect tested) and, on error, `gap_summary` (inclusions, omissions, transpositions); report Trial Log `Type` = ORD | SKILL.md |
| REQ-ORD-E-001 | `ORDERING_PROMPT` unreadable → halt (extend existing REQ-MCQ-E-001) | SKILL.md |
| REQ-ORD-E-002 | Response with an out-of-pool label, a repeated label, or unparseable as a list → ask to resubmit; do not count | SKILL.md |
| REQ-ORD-F-010 | At intake, the orchestrator determines once whether the concept affords an ordered procedure. If non-procedural, exclude `ordering` from the session's type draw (`select_question_type.py --exclude ordering`) | SKILL.md |
| REQ-ORD-F-011 | `select_question_type.py` accepts `--exclude` (comma-delimited) and draws from the remaining types | script |
| REQ-ORD-F-012 | Ordering construction consumes the intake `DOMAIN` preference (Step I3) and prioritized focus areas (Step I4), identically to MCQ/MSQ | ORDERING_PROMPT |
| REQ-ORD-F-013 | Ordering stems and steps obey the MCQ/MSQ banned-language lists and abstraction-boundary rules — topic keyword unavoidable in task and pool; no reliance on adjacent concepts | ORDERING_PROMPT |
| REQ-ORD-F-014 | Each ordering task is fresh within the session and across prior sessions on the same concept | ORDERING_PROMPT |
| REQ-ORD-F-015 | On re-presentation (tangent resume, or after a clarification), the trial is shown with the same pool and the same labels — no re-shuffle, no regeneration | SKILL.md |
| REQ-ORD-F-016 | Axis re-draw bookkeeping: a rejected axis is not recorded as used and stays available to later trials; only the finally-used axis enters the session's axis-exclusion list and Axis Coverage | SKILL.md |
| REQ-ORD-F-017 | The report's Gap Inventory entry for an ordering trial states the Chosen sequence, the Correct sequence, Selection errors (false inclusions, omissions), and Ordering errors (transposed forced pairs), each decomposed | SKILL.md |
| REQ-ORD-F-018 | Analysis-phase classification interprets ordering's dual error structure: a transposition with otherwise-correct selection reads as a surface gap; repeated selection of the orthodox-but-wrong inclusion, or errors spanning both selection and ordering across trials, reads as a fundamental gap | SKILL.md |
| REQ-ORD-F-019 | Presentation and parsing: present the pool one label per line; accept the learner's ordered response in common formats (comma, space, arrow, numbered), case-insensitive; order is significant | SKILL.md |
| REQ-ORD-E-003 | For a procedural concept, if the assigned axis cannot force this trial's order, re-draw the axis (exclude used + rejected); on exhaustion, hold the axis and reconstruct the scenario. No mid-trial type substitution | SKILL.md / ORDERING_PROMPT |

---

## 11. Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-1 | Order-independent steps → multiple valid orders | Generator leaves an unforced adjacency | Binary grade marks a valid order wrong | **No** — strict-total-order validation forbids; fix pre-output |
| FM-2 | Distractor genuinely belongs | A distractor is a defensible extra step | Learner penalized for a valid pick | **No** — sharpen the distractor or frame the stem's gate so inclusion is a genuine error |
| FM-3 | Order arbitrary under the axis | Axis maps poorly to an ordering task | Degenerates toward pure selection | **Partial** — allowed only if selection itself is axis-forced; else fallback (REQ-ORD-E-003) |
| FM-4 | Learner submits wrong length despite disclosed K | Learner error | Treated as incorrect with decomposed feedback | **Yes** — intended |
| FM-5 | Compact response ("ACEB") order ambiguity | Learner format | Interpreted strictly left-to-right | **Yes** — documented parse rule |
| FM-6 | `ordering` drawn but ORDERING_PROMPT unreadable | Missing file | Halt (REQ-ORD-E-001) | **Yes** — halt is correct |
| FM-7 | Distribution shifts 50/50 → 33/33/33 | Adding to TYPES | Fewer MCQ/MSQ per session | **Yes** — intended; note for calibration |
| FM-8 | Near-duplicate so faithful the stem can't disambiguate without leaking the answer | Over-subtle near-duplicate construction | Either two valid readings, or an answer-leaking stem | **No** — regenerate the pair or the trial |
| FM-9 | Assigned axis can't force this trial's order (procedural concept) | Bad axis×scenario pairing | Ordering unforced or surface-sortable | **Yes, via guard** — re-draw axis; on exhaustion reconstruct scenario (REQ-ORD-E-003) |
| FM-10 | Concept is non-procedural — no orderable steps at all | Concept has no procedure | No valid ordering trial exists | **Yes, via guard** — intake gate excludes ordering from the type draw (REQ-ORD-F-010) |

---

## 12. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | Strict-total-order + surface-sort resistance strains generation | High | Med | K=3 floor; axis-fit determination; per-axis dry run made mandatory (impl step 4); abstract-domain fallback |
| R-2 | Ordering harder than MCQ/MSQ → skews pass rate | Med | Low | Binary grade consistent; threshold unchanged; reweight distribution if data warrants |
| R-3 | Grading disputes / near-duplicate ambiguity | Med | Med | Total-order validation; regenerate-on-ambiguity (FM-8); construction-defect replace protocol |
| R-4 | `select_mcq_axis.py` name now serves 3 types | High | Low | Accept as debt; rename out of scope |
| R-5 | Pools up to 8 inflate cognitive load | Med | Low | Cap D≤3; steps 1–2 sentences |
| R-6 | Axis-fit is concept-dependent (observability/recognition may not afford ordering for some concepts) | Med | Med | Intake procedural gate (REQ-ORD-F-010) excludes ordering for non-procedural concepts; trial-time axis re-draw (REQ-ORD-E-003) handles an unfit axis×scenario. No mid-trial type substitution |

---

## 13. Edge cases (for `ORDERING_GENERATION_PROMPT.md`)

| Edge case | Resolution |
|---|---|
| order-independent-steps | Tighten the scenario to introduce a forcing dependency under the axis, or replace a step. Do not output until strict total order holds. |
| distractor-actually-belongs | Sharpen the distractor, or frame the stem's gate so inclusion is a genuine error (see limit-test D). Do not output while a distractor is a defensible extra pick. |
| near-duplicate-forces-ambiguity **(new)** | If a near-duplicate cannot be made genuinely wrong without over-specifying the stem to the point of leaking the answer, regenerate the pair or the trial. |
| unfit-axis-for-scenario **(new)** | Procedural concept, but the assigned axis can't force this trial's order → re-draw the axis (exclude used + rejected); on exhaustion, reconstruct the scenario to one the axis can force. No type substitution (REQ-ORD-E-003). |
| non-procedural-concept **(new)** | Concept affords no orderable procedure at all → excluded at intake: `ordering` is dropped from the session's type draw (REQ-ORD-F-010). Never reaches construction. |
| learner-wrong-length (K disclosed) | Treat as incorrect (selection error); give decomposed feedback; not invalid. |
| invalid-response | Out-of-pool or repeated label, or unparseable → ask to resubmit; do not count. |
| learner-challenges-question | If a genuine second valid order exists, it is a construction defect — acknowledge, replace, do not count. Otherwise hold the evaluation and explain the axis. |
| repeated-probe-scenario-availability | Change the domain anchor for the new session; axis and concept unchanged. |

---

## 14. Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `mcq-probe/prompts/ORDERING_GENERATION_PROMPT.md` | Create | Full XML generation prompt mirroring MSQ + ordering constructs | Governs ordering construction/eval |
| `mcq-probe/scripts/select_question_type.py` | Modify | Add `"ordering"` to `TYPES`; add `--exclude` support (mirror `select_mcq_axis.py`) | Enables ordering selection; lets the intake gate drop ordering for non-procedural concepts |
| `mcq-probe/SKILL.md` | Modify | Intake procedural gate, Constants, Active Constraints, prompt-load, trial-loop present/wait/evaluate + axis re-draw (+ bookkeeping), re-presentation stability, Response Protocol (Ordering), record schema, Report (Type col + Gap Inventory format + analysis classification), Error Handling (extend E-001, add E-002/E-003) | Wire ordering into orchestration |
| `mcq-probe/scripts/select_mcq_axis.py` | None | — | Axis-agnostic; reused as-is |

---

## 15. Open questions

All resolved on 2026-08-27.

| # | Question | Blocker for? | Resolution |
|---|---|---|---|
| 1 | Pool carries distractors (select + order), not pure permutation | Whole design | **Confirmed** — distractors present |
| 2 | Disclose K to the learner | Prompt wording + parse | **Confirmed** — K disclosed, D not |
| 3 | Strict total order vs partial-order/topological grading | Grading model | **Confirmed** — strict total order |
| 4 | Equiprobable vs weighted type distribution | select_question_type | **Confirmed** — equiprobable |
| 5 | Display token ORD vs ORDERING | Cosmetic | **Confirmed** — ORD |
| 6 | Axis-fit fallback: substitute type vs re-draw axis | Orchestration + records | **Resolved** — re-draw the axis (REQ-ORD-E-003); non-procedural concepts gated out at intake (REQ-ORD-F-010); no mid-trial type substitution |

---

## 16. Implementation order

1. Author `ORDERING_GENERATION_PROMPT.md` — full XML: purpose, 9 axes reframed for ordering, question/step requirements, the three signature constructs (§4), construction sequence + validation checklist (§6), feedback protocols (§7), the canonical worked example (§8), edge cases (§13).
2. Modify `select_question_type.py` — add `"ordering"` to `TYPES` and add `--exclude` support (mirror `select_mcq_axis.py`).
3. Modify `SKILL.md` in section order: Intake Phase (procedural determination → `select_question_type.py --exclude ordering` when non-procedural) → File Path Constants → Active Constraints → prompt-load (Trial-loop step 3) → Trial-loop present/wait/evaluate + axis re-draw (steps 4–6) → Response Protocol (Ordering correct/incorrect) → internal record schema → Report Format (Type column + Gap Inventory) → Error Handling (extend E-001; add E-002, E-003).
4. **Mandatory gate:** dry-run one ordering trial per axis (all 9) to confirm strict-total-order + surface-sort resistance is constructable, and to exercise the axis-fit fallback on the hostile axes (recognition, observability). This is the R-1/R-6 validation — do not ship without it.
5. Optional: reweight type distribution after observing pass rates.
