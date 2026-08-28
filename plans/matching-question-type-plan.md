# Plan — Matching Question Type (mcq-probe)

**Status:** Implemented (commit `6715bc8`: `MATCHING_GENERATION_PROMPT.md`, `SKILL.md`, `select_question_type.py`, this plan). OQ 1–7 are resolved per §5 and already shipped as constructed — the recommendations below were not left pending; the generation prompt is built on them directly. The mandatory per-axis dry-run gate (§16 step 5) is now complete — see the Dry-Run Gate Results table at the end of §16. Ready for merge review.

*This status line originally read "Design — awaiting readback confirmation" when this plan was authored; it is corrected here for accuracy, since implementation landed in the same commit that introduced the plan.*
**Date:** 2026-08-27
**Branch:** `claude/mcq-probe-matching-questions-9d0f7a`
**Target skill:** `mcq-probe`
**Precedent:** `plans/ordering-question-type-plan.md` (Ordering was added the same way; this plan reuses its structure and its §3 hardness-transfer method).

---

## 0. Readback — the defining interpretation

The spec is one line: *"Matching: has a list of responses to match with a list of 3–7 prompts. You must match all the pairs correctly to receive credit for the question."* Everything below rests on three reads of it. If any is wrong, large parts of this plan change — confirm before implementation.

1. **The response list is larger than the prompt list (surplus responses).** "A list of responses to match with a list of 3–7 prompts" reads the two lists as separate and unequal. A pure equal-size bijection has a fatal property for this skill: once n−1 prompts are matched, the nth is forced by elimination with zero reasoning — a `1/n` difficulty leak (33% at n=3). The fix is **surplus responses**: `m = n + D` responses, `D ≥ 1` of which match no prompt. This is the matching analogue of Ordering's distractor pool — selection gets teeth, and elimination never hands the learner a free pairing. **This is the load-bearing interpretation.** (OQ 1)
2. **Credit is binary.** "Match all the pairs correctly to receive credit" = all-or-nothing, consistent with MCQ/MSQ/ORD. No partial credit for k-of-n correct. (OQ 2)
3. **The mapping is injective, one response per prompt, responses not reused.** Each prompt matches exactly one response; each response matches at most one prompt; `D` responses match nothing. Reusable responses were considered and rejected (OQ 3) — reuse dissolves the near-duplicate device and muddies the binary grade.

If instead you intend an **equal-size bijection with no surplus**, or **reusable responses**, say so now — §1, §4, §5, and the whole failure-mode analysis change.

---

## 1. Background / context

`mcq-probe` is a judgment-probe evaluation skill. An orchestrator (`SKILL.md`) runs an intake phase, an N-trial loop, and an analysis phase producing a Markdown report. Per trial, `select_question_type.py` draws the type and `select_mcq_axis.py` assigns one of 9 judgment axes (no consecutive repeat, no reuse within session). Generation prompts (one per type, loaded once on Trial 1) govern construction.

**The skill's central property — the thing this feature must preserve:** difficulty is a *structural* property of the answer set, not a setting. Every wrong answer is independently viable in isolation and fails **only** under forward projection along the assigned axis. Two devices enforce it — the **near-duplicate pair** and the **orthodox-but-wrong** choice. A wrong answer eliminable by surface reading is a construction **defect**, regenerated, never shipped.

**Why Matching is the acid test of that property.** Of the four types, Matching has the lowest-effort *default* form and the highest risk of shipping a knowledge quiz. "Match each protocol to its port," "match each term to its definition" — the canonical matching question is pure recall, every response keyword-locked to one prompt, every wrong cell rejectable on sight. That default form is the exact mistake `CLAUDE.md` forbids. Matching therefore demands the *strongest* explicit anti-surface machinery of any type: the difficulty must live in a **dense confusion grid**, not in an association table.

### Globals after this change

| Global | Value | Note |
|---|---|---|
| Type token (script stdout) | `matching` | joins `mcq`, `msq`, `ordering` |
| Display label | **MAT** | on its own line, matching MCQ/MSQ/ORD |
| n — prompts | 3–7, scenario-driven | the anchored set; the graded pairs |
| D — distractor responses | 1–3 | ≥1 so selection has teeth and elimination is defeated |
| m — response pool | n + D = 4–10 | the list matched *from* |
| Prompt labels | `1, 2, 3, …` (numeric) | distinguishes prompts from responses at a glance |
| Response labels | `A, B, C, …` (alpha) | the pool; D of them are unused in the key |
| Grade | binary | exact match of all n prompt→response pairs |
| Count disclosure | n and m both visible; D derivable | diverges from Ordering's hidden D — see OQ 7 / FM-7 |
| Mapping model | injective, unique, **surface-unresolvable** | every cell cross-viable; bijection recoverable only by projection |
| Axes | 9, reused unchanged | `select_mcq_axis.py` is axis-type-agnostic |
| Type distribution | 1/4 each (eligible concepts) | intake gates may exclude ordering and/or matching |
| Signature constructs | cross-viability law (global), near-duplicate confusion cell (≥1), orthodox-but-wrong distractor response (≥1), unique bijection | matching analogues of the MCQ/MSQ devices |

### Pipeline

Intake (now includes a one-time **matchable determination** alongside the existing procedural one — REQ-MAT-F-010) → trial loop. Per trial: `select_question_type.py` now returns `mcq`/`msq`/`ordering`/`matching`; `select_mcq_axis.py` assigns the axis; the matching generation prompt (loaded once on Trial 1) constructs the trial. A matching trial presents a prompt list (numeric) and a larger response pool (alpha); the learner replies with n prompt→response pairs; evaluation decomposes the response into **selection errors** (a prompt attached to a distractor response, or a correct response left unused) and **assignment errors** (two prompts' responses swapped), then the binary grade feeds the same analysis phase and report as the other three types.

---

## 2. Problem statement

MCQ/MSQ probe judgment among parallel choices; Ordering probes command of a forced procedure. None probes whether a learner can **discriminate confusable cases** — tell apart n near-identical conditions and attach each to its true outcome, when every outcome looks plausible for several conditions. That is a distinct and common competence (differential diagnosis, config-vs-behavior, symptom-vs-cause, edge-case classification), and Matching is the type that isolates it.

The hard constraint is preserving the binary grade under the skill's difficulty bar. Matching fails that bar in three specific ways, all of which must be engineered out:

- **Surface association leaks (the dominant defect).** If any response keyword-, category-, or textbook-matches exactly one prompt, that pairing is solvable without projecting the axis. This is the "hole in one" — and it is the *natural* state of a matching question. Defeating it is the whole job.
- **Elimination leaks (the parity defect).** In an equal-size bijection, correctly placing early pairs removes candidates and can unzip the grid; the last pair is always free. Surplus responses (`D ≥ 1`) plus a no-elimination-shortcut law close this.
- **Ambiguity leaks.** If two complete assignments are both defensible under the axis, the binary grade marks a valid answer wrong. The correct bijection must be unique.

Matching is therefore, like Ordering, harder than MCQ/MSQ by construction. That is intended, not a defect to soften.

---

## 3. Hardness transfer — one-to-one mapping (the load-bearing section)

This is the justification for every construction rule that follows. Each MCQ/MSQ difficulty mechanism maps to a matching analogue that must hold with equal force. Where Ordering doubled the projection burden across *selection + order*, Matching doubles it across *selection + assignment* (which responses are used, and which used response attaches to which prompt).

| MCQ/MSQ mechanism | What it forces | Matching transfer | Status |
|---|---|---|---|
| Every wrong answer independently viable | No surface elimination | **Every response reads as a plausible match for ≥2 prompts; every prompt has ≥2 plausible responses.** The whole n×m grid is dense with viable cells. No keyword/category/textbook cell. | Governs the whole grid |
| Wrong fails only under forward projection | Reasoning, not recall | **Both** operations projection-gated: which responses are distractors (selection) *and* which response attaches to which prompt (assignment). | Extended to two operations |
| Near-duplicate pair | Precision under one decisive phrase | **Near-duplicate confusion cell**: two twinned prompts × two twinned responses, forming a 2×2 sub-grid every cell of which is surface-viable; the correct diagonal is fixed by one embedded phrase decidable only under projection. Cross-wiring it is the canonical transposition error. | Preserved; the primary discrimination site |
| Orthodox-but-wrong | Punishes convention over reasoning | **Orthodox-but-wrong distractor response**: a distractor that is the textbook / conventionally-expected answer for one specific prompt. Expertise pulls you to attach that prompt to it; under projection the prompt resolves elsewhere and the orthodox response matches nothing. | Preserved; expertise actively misleads toward a wrong attachment |
| Surface features aren't the differentiator | Defeats pattern-matching | **No pairing recoverable by lexical/category overlap or by elimination.** The axis, not surface similarity or parity, resolves the grid. | New explicit requirement (two laws: cross-viability + no-elimination-shortcut) |
| No banned language / quality signals | No heuristic shortcuts | Unchanged; same banned lists, plus no sequencing/pointer cues that pre-wire a pairing. | Preserved |

**Correction carried over from Ordering's lesson.** Ordering's first draft included an out-of-scope distractor and had to remove it — an out-of-scope item is rejectable without projecting the axis. The matching analogue is a **response that is viable for only one prompt** (surface-locked). That is *also* a transfer failure and is forbidden. Every response must be cross-viable for ≥2 prompts, or it is a hole in one.

---

## 4. Grid-design law + required constructs

**Law (four parts).** Every pairing decision — used-vs-distractor and which-prompt — is decidable only by projecting each prompt forward under the assigned axis.

1. **Cross-viability (both directions).** Every response reads as a plausible match for **≥2 prompts** on first pass; every prompt has **≥2 plausible responses**. No response is surface-attachable (keyword, category, or textbook pairing) to exactly one prompt. The grid is dense; surface reading cannot resolve any cell.
2. **No-elimination-shortcut.** `D ≥ 1` surplus responses, each cross-viable. No prompt's correct match is recoverable by eliminating obviously-wrong responses. Validation simulates elimination: after *any* subset of prompts is correctly matched, every remaining prompt must still face **≥2 surface-viable responses**. Surplus is the means; this law is the end.
3. **Unique bijection.** Exactly one complete injective assignment survives projection. No second complete assignment is defensible under the axis. (The gradeability guarantee — analogue of Ordering's strict-total-order.)
4. **No free prompt.** Every prompt's correct response is contested by ≥1 other surface-viable response. No prompt is a giveaway. (The prompt-side complement of cross-viability — analogue of Ordering's surface-sort resistance.)

**Required constructs (per trial):**

1. **Near-duplicate confusion cell** (≥1) — two prompts twinned (diverging at one embedded phrase) and two responses twinned (diverging at one embedded phrase), forming a 2×2 sub-grid whose four cells are all surface-viable. Projection of the one differentiating phrase fixes the correct diagonal. The learner must not cross-wire the twins.
2. **Orthodox-but-wrong distractor response** (≥1) — a distractor (one of the `D` unused responses) that is the standard, professionally-expected answer for one specific prompt, written in language that signals rigor. Under the axis that prompt attaches elsewhere and this response matches no prompt. May alternatively be realized as a cross-attracting *matched* response (a prompt's conventional answer that is genuinely another prompt's match); the distractor form is primary and also justifies the surplus.

**Forbidden (transfer failures):** a response viable for only one prompt · any pairing recoverable by keyword/category/textbook overlap · a prompt whose match is forced by elimination · a second defensible complete assignment · sequencing/pointer language that pre-wires a pairing.

---

## 5. Design decisions

| Decision | Resolution |
|---|---|
| Response-set structure | **Surplus responses.** n prompts, m = n + D responses (D ∈ [1,3]), injective prompt→response. D responses are distractors, used by no prompt. Kills the parity/elimination leak; gives the orthodox-but-wrong lure a home. (OQ 1) |
| Grade model | **Binary.** Correct iff every one of the n prompt→response pairs equals the key. No partial credit. (OQ 2) |
| Response reuse | **None.** Each response matches ≤1 prompt. Reuse rejected: it dissolves the near-duplicate 2×2 device and complicates the binary grade. (OQ 3) |
| Mapping model | Injective, **unique** complete assignment. Every cell cross-viable; the bijection is recoverable only under projection, never by surface similarity or elimination. |
| n range | 3–7 prompts (per spec). n=3 is the difficulty floor (elimination pressure highest → surplus matters most); n=7 is the cognitive-load ceiling. |
| D range | 1–3 distractor responses, scenario-driven. m = n + D ∈ [4,10]. |
| Label scheme | Prompts numeric (`1…n`); responses alpha (`A…`). Two visibly distinct alphabets remove any prompt/response confusion in the learner's reply. (OQ 6) |
| Count disclosure | n and m are both visible (both lists are printed); D = m − n is derivable. Unlike Ordering (hidden D), this does not leak the answer — knowing *how many* responses go unused does not reveal *which*, since the unused ones are cross-viable. (OQ 7) |
| Signature constructs | Cross-viability law (global, four parts), near-duplicate confusion cell (≥1), orthodox-but-wrong distractor response (≥1), unique bijection. |
| Prompt/response substance | Prompts: 1–3 sentences, a concrete case/condition/symptom carrying one embedded distinguishing detail. Responses: 1–2 sentences, an outcome/behavior/cause/classification with enough detail to be cross-viable and to support the near-duplicate twin. A bare label ("bufferbloat") is insufficient; it must describe the mechanism. |
| Axis source | Reuse `select_mcq_axis.py` unchanged. All 9 axes apply; the axis defines the prompt-role→response-role semantic and the failure mode of a wrong attachment. |
| Intake matchable gate | At intake, determine once whether the concept affords **multiple confusable cases along a dimension** (≥3 conditions/symptoms/sub-types with distinct, cross-viable outcomes). If **not matchable** (a flat concept — one definition, no case structure), exclude `matching` from the session's type draw (`select_question_type.py --exclude matching`). Mirrors the procedural gate (REQ-MAT-F-010). (OQ 4) |
| Axis re-draw (no type substitution) | For a matchable concept, if the assigned axis cannot make this trial's grid projection-resolvable, **re-draw the axis** (`select_mcq_axis.py --exclude [used + rejected]`, up to 3 attempts). On exhaustion, hold the axis and reconstruct the case-set to one the axis can force. The trial type is **never** substituted mid-trial. Mirrors Ordering (REQ-MAT-E-003). |
| Near-duplicate ambiguity | If the near-duplicate cell cannot be made genuinely resolvable without over-specifying a prompt to the point of leaking the pairing, regenerate the cell or the trial. Mirrors Ordering FM-8 / edge case. |
| Type distribution | Equiprobable 1/4. Revisit after observing pass rates. (OQ 5) |
| Display token | **MAT**. Matches the three-letter pattern. |

---

## 6. Construction sequence (core of `MATCHING_GENERATION_PROMPT.md`)

1. **axis-confirmation** — use the axis from `select_mcq_axis.py`; do not signal it.
2. **axis-fit / re-draw** — confirm the assigned axis can make a dense, projection-resolvable grid for the concept (a prompt-role→response-role semantic under which every cell is cross-viable and one unique bijection survives). If not, signal an axis-fit failure to the orchestrator (re-draw axis, up to 3 attempts; on exhaustion, reconstruct the case-set). Never substitute the type. Non-matchable concepts are already excluded at intake (REQ-MAT-F-010).
3. **role-selection** — choose the prompt-role→response-role pairing the axis makes load-bearing (e.g., failure-diagnosis → symptom→cause; boundary-condition → condition→behavior; recognition → presentation→classification; transfer → new-domain-case→mechanism-instantiation). The role pairing is what makes surface association fail and projection necessary. **Transfer axis only:** apply domain-vocabulary inversion — phrase each response in a domain other than its correct prompt, so keyword cues point at the wrong pairing and only mechanism resolves (REQ-MAT-F-020; worked in §8.3).
4. **case-set construction (prompts)** — write n prompts (3–7) as minimal variants along one dimension of the concept, sharing a common frame so every response is topically plausible for every prompt, each diverging at one embedded distinguishing detail. Disclose n implicitly (they are numbered and all must be matched). Do not signal the axis.
5. **key construction (correct responses)** — write the n correct responses. For each, verify it is cross-viable for ≥2 prompts (not just its own) and that its correct prompt is fixed only under projection. Verify the complete assignment is **unique** — no second bijection survives. Plant the near-duplicate confusion cell (≥2 twin prompts × ≥2 twin responses).
6. **distractor construction** — write D distractor responses (1–3), each cross-viable (plausible for ≥2 prompts) and matching no prompt under projection. Include ≥1 orthodox-but-wrong distractor (the conventional answer for some prompt). Run the no-elimination-shortcut simulation.
7. **label-and-shuffle** — number prompts `1…n` and letter responses `A…` in shuffled order; the correct pairing must not run down the diagonal (1→A, 2→B, …); vary across trials; do not cluster distractor letters at the end.
8. **internal-validation** — run the checklist; regenerate on any failure.
9. **output** — **MAT** on its own line, the prompt list (numeric, one per line), the response pool (alpha, one per line), closing prompt: *"Match each of the [n] prompts to one response (e.g., 1-C, 2-A, …). Not every response is used."* Stop. Wait.

### Internal-validation checklist

- [ ] Assigned axis used and not signaled.
- [ ] Concept affords a dense projection-resolvable grid under the axis (else axis-fit fallback taken).
- [ ] Topic keyword unavoidable in the prompts and the responses.
- [ ] Every response is cross-viable for ≥2 prompts; no response is surface-attachable (keyword/category/textbook) to exactly one prompt.
- [ ] Every prompt has ≥2 surface-viable responses; no free prompt.
- [ ] No pairing is recoverable by lexical/category overlap — surface reading resolves no cell.
- [ ] No-elimination-shortcut: after any subset of prompts is correctly matched, every remaining prompt still faces ≥2 surface-viable responses.
- [ ] The correct assignment is unique — no second complete bijection survives projection.
- [ ] ≥1 near-duplicate confusion cell present (2 twin prompts × 2 twin responses; all four cells surface-viable; correct diagonal fixed only under projection).
- [ ] Each near-duplicate is genuinely resolvable without a prompt leaking its pairing (else regenerate — near-duplicate-forces-ambiguity edge case).
- [ ] ≥1 orthodox-but-wrong distractor response present (conventional answer for some prompt; matches nothing under projection).
- [ ] Each distractor fails for a distinct reason, only under projection.
- [ ] n ∈ [3,7]; D ∈ [1,3]; response pool m = n+D, prompts labeled 1…n, responses labeled A… contiguously.
- [ ] Correct pairing is not the identity diagonal (1→A, 2→B, …).
- [ ] No banned language; no sequencing/pointer cues that pre-wire a pairing.
- [ ] Transfer axis only: domain-vocabulary inversion applied — no response shares its correct prompt's domain vocabulary; keyword cues point away from the correct pairing (REQ-MAT-F-020).
- [ ] Case-set fresh this session.

---

## 7. Feedback protocol

**Correct** (all n pairs match the key):
1. Acknowledge briefly ("Correct." / "Right." / "That's it.").
2. State the axis in one sentence.
3. Why each pairing survives — each prompt→response individually: the projection that fixes it and rules out the other surface-viable responses.
4. Each distractor's failure, individually; name the orthodox-but-wrong distractor ("E is the conventional answer for prompt 1 — professionally sound in many contexts — but under [axis] prompt 1 resolves to A, and E matches nothing because [mechanism]").
5. Resolve the near-duplicate cell — the one phrase that separates the twin prompts and the twin responses, and why it is decisive only under projection.
6. Proceed to next trial, or to analysis if this was trial N.

**Incorrect** (any pair wrong):
1. State the axis first.
2. Decompose the error into its two classes, each addressed individually:
   - **Selection** — for each prompt the learner attached to a distractor response, why that response matches no prompt under the axis (name the orthodox-but-wrong lure if that is what they took); for each correct response left unused, why it belongs to its prompt.
   - **Assignment** — for each transposed pair (two prompts whose responses were swapped, the near-duplicate cross-wire being canonical), why each prompt's true response is fixed under projection and why the swap fails.
3. State the correct key directly: `1→A, 2→B, 3→C, 4→D` (E unused).
4. Why each pairing survives — each individually.
5. Each distractor individually; name the orthodox-but-wrong distractor; resolve the near-duplicate cell.
6. No nudge, no recovery exchange. Proceed.

---

## 8. Worked examples

Three axes proven constructible end to end — one per subsection. Each demonstrates the grid-design law (§4) in force: a dense cross-viable grid, a unique bijection, ≥1 near-duplicate confusion cell, and ≥1 orthodox-but-wrong distractor.

### 8.1 Canonical — failure-diagnosis (symptom → cause)

**Axis:** failure-diagnosis · **Concept:** TCP throughput anomalies (congestion control × flow control) · **Domain:** abstract · **n=4, D=1, response pool A–E.**

> Match each observed transfer symptom to its root cause. Not every cause is used.
>
> **Prompts (symptoms):**
> 1. A bulk transfer over a long-RTT satellite link plateaus near 2 Mbps though the path supports 50 Mbps; a capture shows the sender repeatedly stops sending and waits, then resumes — **with no retransmissions**.
> 2. A transfer over a clean gigabit LAN peaks, then repeatedly halves its rate in a regular sawtooth, with a retransmission at each drop.
> 3. A transfer through a device with a very large buffer sustains high throughput, but end-to-end latency climbs to several seconds and stays there; almost no packets are lost.
> 4. A transfer over WiFi runs well below capacity with frequent fast-retransmits, though the link's actual loss rate is low and RTT is stable.
>
> **Responses (causes):**
> A. The receive window is smaller than the bandwidth-delay product, so the sender exhausts the advertised window and stalls until ACKs return — a flow-control limit, not congestion.
> B. Congestion control operating normally: the sender probes upward until a real drop signals congestion, then multiplicatively decreases — the sawtooth is the algorithm working as designed.
> C. An oversized intermediate buffer absorbs overshoot instead of dropping, so the loss signal arrives only once the queue is saturated; the sender never sees a timely drop and latency inflates.
> D. Path reordering produces duplicate ACKs that trip fast-retransmit though little is truly lost, so the sender needlessly cuts its window.
> E. The path's available bandwidth is simply lower than the transfer demands; throughput is capacity-bound.

**Correct key: 1→A, 2→B, 3→C, 4→D. E unused.**

**Cross-viability (why the grid is dense):**

| Response | Surface-viable for | Attaches (under projection) to |
|---|---|---|
| A (window limit → stall) | 1, 4, and superficially 2 ("why not faster?") | 1 only — the stall-with-no-loss signature |
| B (normal congestion sawtooth) | 2, 4 (both show retransmits), 1 | 2 only — halving *coincides with real drops* on a clean path |
| C (bufferbloat) | 3, 1 (latency/stall confusion), 2 | 3 only — sustained throughput + inflated latency + ~no loss |
| D (reordering → spurious retransmit) | 4, 2 (both retransmit) | 4 only — fast-retransmits with *low actual loss, stable RTT* |
| E (capacity-bound) — orthodox lure | 1, 3, 4 (any slow transfer) | nothing — see below |

**Near-duplicate confusion cell:** prompts **2 and 4** (twin: both under-perform *with retransmits*) × responses **B and D** (twin: both about the loss/retransmit machinery). All four cells read as viable. The one differentiating projection: are the retransmits responding to **real drops** (2, clean LAN, rate halves at each drop → B) or to **reordering-induced duplicate ACKs** with little true loss (4 → D)? "There are retransmits" is the surface feature; *what the retransmits are responding to* is the projected differentiator. Cross-wiring 2↔4 / B↔D is the canonical transposition error.

**Orthodox-but-wrong distractor (E):** "insufficient bandwidth / capacity-bound" is the standard first diagnosis for any slow transfer — professionally common, reached for by convention. A learner deferring to it attaches prompt 1 or 4 to E. It matches nothing: 1 stalls with no loss on a 50 Mbps path (window, not capacity), 3 *sustains high throughput* (not capacity-bound), 4 carries the reordering signature. Attaching any prompt to E is the canonical selection error.

**Unique bijection:** 1 (stall, no loss) → only A; 3 (sustained throughput, high latency, no loss) → only C; 2 and 4 resolved to B and D by the near-duplicate projection; E excluded from all. No second complete assignment survives. Binary grade defensible.

**No-elimination-shortcut with D=1:** after correctly placing 1→A and 3→C, the learner still faces {2,4} × {B, D, E} — E remains cross-viable for both, so the final pairings are **not** a forced 2-cycle; the learner must genuinely project to resolve B vs D *and* to exclude E. The surplus does its job.

Every one of the five responses is a real TCP failure mode; nothing is rejectable on sight. Difficulty is structural.

### 8.2 Boundary-condition (condition → mechanism)

**Axis:** boundary-condition · **Concept:** tire thermal operating window · **Domain:** motorsport · **n=4, D=1, pool A–E.**

> Match each grip-loss situation to its mechanism. Not every mechanism is used.
>
> **Prompts:** 1. Out-lap, cold track, fresh tires: slides for two laps, then grip arrives and holds. · 2. Mid-stint, following closely through high-speed corners: fronts progressively lose bite; backing off a lap does **not** restore them, but a cooler sequence does. · 3. Late in a long stint, one compound: grip fades, surface marbled and greasy, **no** temperature management brings it back. · 4. Early in a stint, right after starting inflation was lowered: grip down from the first flying lap, flat all stint, tire runs **hotter** than telemetry expects.
>
> **Responses:** A. Passed its **wear** life — rubber spent (marbling), grip structurally gone regardless of temperature. · B. Core temp **below** the window — cold compound slides until worked into the window, then grip appears and holds. · C. The driver is **overdriving** — sliding the car and overworking the rubber; manage pace, not tire. · D. Surface temp **above** the window — overheated compound greases over, recovering only once it cools back in. · E. Inflation **outside** the target window — wrong pressure distorts the contact patch and shifts thermal behaviour, depressing grip all run.

**Correct key: 1→B, 2→D, 3→A, 4→E. C unused.**

Cross-viability: the shared surface fact is "grip is low"; the differentiator is *which threshold was crossed*, read only from the onset/recovery signature. A (wear) viable for 2,3 · B (under-temp) for 1,2,4 · C (overdriving, orthodox lure) for 2,3,4 · D (over-temp) for 2,3,4 · E (pressure) for 1,2,4.

Near-duplicate cell: **{2,3} × {D,A}** — both are stint-long grip fade with a greasy surface. The projected differentiator is **reversibility**: 2 recovers on cooling → thermal → D; 3 won't return under any temperature management, surface marbled → structural wear → A. Each twin prompt embeds its firing condition (recovers-on-cooling vs. never-recovers) — §13's over-specify-to-preserve-a-single-key rule in action.

Orthodox-but-wrong (C): "the driver's overdriving, manage the pace" is the reflexive explanation for any fading grip; convention pulls hard toward it. It matches nothing — every prompt carries a threshold signature (grip arriving on warm-up, recovering on cooling, marbling, tracking a pressure change) that driving style does not produce.

Unique bijection: 1 (grip *arrives*)→B · 3 (*irreversible* + marbled)→A · 2 (reversible on cooling)→D · 4 (whole-run flat + *hotter* after a pressure drop)→E · C nowhere. No-elimination-shortcut (D=1): after 1→B and 4→E, {2,3}×{A,D,C} stays contested — reversibility must be projected to split A from D and reject C.

### 8.3 Transfer (the hostile axis — keyword-collapse defeated by domain-vocabulary inversion)

Transfer is R-2's danger axis: the naive form is "match term to definition," pure surface. This example defeats that by construction — **every response is phrased in the vocabulary of a domain other than its correct prompt**, so keyword matching is misdirected and only the mechanism resolves the grid.

**Axis:** transfer · **Concept:** Little's Law (average work-in-progress = arrival rate × time-in-system, L = λW, in a stable system) · **prompts span four domains by design** · **n=4, D=1, pool A–E.**

> Match each situation to the statement that correctly states what Little's Law predicts. Not every statement is used.
>
> **Prompts:** 1. **Hospital ED** — arrivals steady; a fast-track lane cuts each patient's average time in the department. · 2. **Software team** — ticket intake rate held constant; a strict work-in-progress cap enforced on the board. · 3. **Coffee shop** — a promotion lifts the walk-in rate by half, but the counter still serves faster than customers arrive. · 4. **Factory** — sales doubles the order arrival rate, past what the unchanged machines can complete.
>
> **Responses:** A. When customers arrive faster than the counter can ever serve them, there is no steady line length — the queue grows without bound. · B. At a fixed inflow rate, shortening the time each item is held in the buffer lowers the average number buffered. · C. Since throughput is work over time, cutting the time each item spends in the system raises the number processed per hour. · D. To hold the number of units on the floor at the imposed ceiling while the line keeps admitting parts at the same rate, each part's time on the floor is driven down. · E. With treatment capacity and per-patient time unchanged, a higher but still-manageable admission rate raises the ward's census proportionally to a new, stable level.

**Correct key: 1→B, 2→D, 3→E, 4→A. C unused.**

Keyword-lure table — every surface cue misleads:

| Response | Phrased in | Keyword-lures toward | Mechanism resolves to |
|---|---|---|---|
| A | coffee-shop | prompt 3 (coffee) ✗ | **4** — arrivals exceed capacity → unbounded |
| B | network/buffer | *no networking prompt exists* | **1** — fixed λ, cut W → L falls |
| D | factory | prompt 4 (factory) ✗ | **2** — clamp L at fixed λ → W falls |
| E | hospital | prompt 1 (hospital ED) ✗ | **3** — higher-but-servable λ → bounded rise |
| C | neutral | — | nothing |

Three of four responses keyword-lure toward the *wrong* prompt (A→3, D→4, E→1); the fourth (B) has no keyword home at all, forcing mechanism reasoning. Domain matching scores near zero.

Two near-duplicate cells: **{1,2}×{B,D}** — the dual levers of L=λW; the split is *which variable the intervention clamps* (1's fast-track clamps W directly → count falls → B; 2's cap clamps L directly → time-in-system falls → D). **{3,4}×{E,A}** — the **stability boundary**; arrivals still servable (3 → bounded proportional rise → E) vs. exceeding capacity (4 → no steady state → A). Little's Law holds only for a stable system, so a learner who lifts "more arrivals → proportionally more in system" past the boundary mis-assigns.

Orthodox-but-wrong (C): "throughput = work/time, so cutting time-in-system raises throughput" — the canonical Little's Law misapplication, surface-fitting prompts 1 and 2. It matches nothing: stable-system throughput equals the arrival rate, which 1 and 2 both hold fixed.

Unique bijection: 1→B, 2→D, 3→E, 4→A; C nowhere. No-elimination-shortcut (D=1): after 1→B and 2→D, {3,4}×{E,A,C} stays contested — the stability boundary must be projected to split E from A and reject C.

**Construction rule this example promotes (REQ-MAT-F-020):** for the transfer axis, phrase each response in a domain *other* than its correct prompt (domain-vocabulary inversion), so surface matching is systematically misdirected and the grid is resolvable only on mechanism. This is the transfer axis's answer to R-2.

---

## 9. Limit-test example (justifies edge cases in §13)

Built to expose the two matching-specific ceilings the §8 examples (all n=4) do not: **n=3 (worst elimination pressure)** and a **near-duplicate pushed to the defensibility boundary**. (The transfer keyword-collapse ceiling is fully worked in §8.3.)

**Axis:** boundary-condition · **Concept:** backpressure (bounded-queue flow control) · **n=3, D=2, pool A–E.** Three *different-domain* systems each under a load condition; responses are mechanism-level descriptions of what the bounded queue does *in that system's own terms*.

**Limit findings the type must codify:**

- **n=3 elimination pressure.** With only three prompts, a single surplus response is thin — after two correct placements the third is nearly forced. Mitigation: at n=3, `D ≥ 2` (not just ≥1), and the near-duplicate cell must span the *last-resolved* prompts so the grid cannot unzip. Captured as a risk (R-1) and a validation refinement.
- **Keyword collapse (cross-ref §8.3).** The transfer axis's failure mode — the grid degenerating to term→definition — and its fix, **domain-vocabulary inversion (REQ-MAT-F-020)**, are fully demonstrated in §8.3. At n=3 the same rule applies with less slack: fewer prompts means fewer domains to invert across, so the inversion must be exact or the grid leaks a keyword home.
- **Near-duplicate at the defensibility boundary.** As in Ordering's limit test, a near-duplicate response can read as *also correct* for its twin prompt ("that mechanism is true of both systems"). The hole is closable only by embedding in each twin prompt the one condition its correct response fires on — and if that cannot be done without leaking the pairing, regenerate. This proves the same two rules Ordering needed: (1) a prompt sometimes must over-specify its distinguishing condition to preserve a single key, and (2) if it cannot without leaking, regenerate.

---

## 10. Requirements

| ID | Requirement | Scope |
|---|---|---|
| REQ-MAT-F-001 | `select_question_type.py` returns one of `mcq`/`msq`/`ordering`/`matching` | script |
| REQ-MAT-F-002 | On Trial 1, load `MATCHING_PROMPT` alongside the other prompts; unreadable → halt | SKILL.md |
| REQ-MAT-F-003 | Matching trial presents **MAT** on its own line, a numeric prompt list (1…n), an alpha response pool (A…m > n), and a closing prompt disclosing the matching constraint: each prompt takes exactly one response, each response is used at most once, and some responses go unused. Response labels are shuffled so the correct pairing is not the identity diagonal (1→A, 2→B, …) | MATCHING_PROMPT |
| REQ-MAT-F-004 | Every response is cross-viable for ≥2 prompts; every prompt has ≥2 surface-viable responses; no pairing recoverable by lexical/category/textbook overlap or by elimination. Surplus D ≥ 1 (D ≥ 2 when n = 3); the no-elimination-shortcut simulation passes — after any subset of prompts is correctly matched, every remaining prompt still faces ≥2 surface-viable responses | MATCHING_PROMPT |
| REQ-MAT-F-005 | The correct assignment is a unique injective bijection under the axis; no second complete assignment survives projection | MATCHING_PROMPT |
| REQ-MAT-F-006 | ≥1 near-duplicate confusion cell (2 twin prompts × 2 twin responses, all four cells surface-viable, diagonal fixed only under projection); ≥1 orthodox-but-wrong distractor response; each distractor fails for a distinct reason, only under projection | MATCHING_PROMPT |
| REQ-MAT-F-007 | Parse response as a set of n prompt→response pairs; injective (no response reused, no prompt doubled); repeated/omitted prompt, reused response, or out-of-range label → resubmit | SKILL.md |
| REQ-MAT-F-008 | Grade correct iff every prompt→response pair equals the key exactly (binary; D distractors unused) | SKILL.md |
| REQ-MAT-F-009 | Feedback decomposes error into selection (prompt attached to a distractor; correct response left unused) and assignment (transposed pairs); each addressed individually; name the orthodox-but-wrong distractor; resolve the near-duplicate cell | SKILL.md / MATCHING_PROMPT |
| REQ-MAT-F-010 | At intake, the orchestrator determines once whether the concept affords ≥3 confusable cases with distinct cross-viable outcomes (`MATCHABLE`). If not, exclude `matching` from the session's type draw. Combines with the procedural gate: excludes may be `ordering`, `matching`, or both (comma-joined) | SKILL.md |
| REQ-MAT-F-011 | `select_question_type.py --exclude` accepts multiple comma-delimited types and draws from the remainder (already supported; add `matching` to the valid set) | script |
| REQ-MAT-F-012 | Matching construction consumes the intake `DOMAIN` (Step I3) and prioritized focus areas (Step I4), identically to the other types | MATCHING_PROMPT |
| REQ-MAT-F-013 | Matching prompts and responses obey the banned-language lists and abstraction-boundary rules; add: no sequencing/pointer cues that pre-wire a pairing; topic keyword unavoidable in prompts and responses | MATCHING_PROMPT |
| REQ-MAT-F-014 | Each matching case-set is fresh within the session and across prior sessions on the same concept | MATCHING_PROMPT |
| REQ-MAT-F-015 | On re-presentation (tangent resume, or after a clarification), the trial is shown with the same prompts, responses, and labels — no re-shuffle, no regeneration | SKILL.md |
| REQ-MAT-F-016 | Axis re-draw bookkeeping: a rejected axis is not recorded as used and stays available to later trials; only the finally-used axis enters the session's axis-exclusion list and Axis Coverage | SKILL.md |
| REQ-MAT-F-017 | The report's Gap Inventory entry for a matching trial states the submitted pairs, the correct key, Selection errors (attachments to distractors; unused correct responses), and Assignment errors (transposed pairs), each decomposed | SKILL.md |
| REQ-MAT-F-018 | Analysis-phase classification interprets matching's dual error structure: a single transposition in the near-duplicate cell with otherwise-correct pairs reads as a surface gap; repeated attachment to the orthodox-but-wrong distractor, or errors spanning both selection and assignment across trials, reads as a fundamental gap | SKILL.md |
| REQ-MAT-F-019 | Presentation and parsing: prompts one per numbered line, responses one per lettered line; accept the learner's pairs in common formats (`1-C`, `1:C`, `1C`, `1 → C`, comma/newline separated), case-insensitive; numeric prompt labels and alpha response labels are disjoint, so pair-token order (`1-C` or `C-1`) parses unambiguously | SKILL.md |
| REQ-MAT-F-020 | **Transfer-axis domain-vocabulary inversion:** on a `transfer` trial, each response is phrased in the vocabulary of a domain other than its correct prompt, so surface/keyword matching is systematically misdirected and the grid is resolvable only on the concept's mechanism. This is the transfer axis's construction answer to the keyword-collapse risk (R-2); worked in §8.3 | MATCHING_PROMPT |
| REQ-MAT-F-021 | Internal record & report: the per-trial record uses `question_type: matching` and populates `probe_target` (the discrimination tested, ≤6 words — e.g. "reversible vs. structural grip loss") and, on error, `gap_summary` (mis-attachments to distractors, unused correct responses, transpositions); the report Trial Log `Type` column shows **MAT**. Analogue of REQ-ORD-F-009; pairs with F-009 (feedback) and F-017 (Gap Inventory) | SKILL.md |
| REQ-MAT-E-001 | `MATCHING_PROMPT` unreadable → halt (extend existing REQ-MCQ-E-001) | SKILL.md |
| REQ-MAT-E-002 | Response with a repeated prompt, a reused response, an out-of-range label, a missing prompt, or otherwise unparseable → ask to resubmit; do not count. A well-formed set that attaches a prompt to a distractor is **valid and incorrect**, not a resubmit | SKILL.md |
| REQ-MAT-E-003 | For a matchable concept, if the assigned axis cannot make this trial's grid projection-resolvable, re-draw the axis (exclude used + rejected); on exhaustion, hold the axis and reconstruct the case-set. No mid-trial type substitution | SKILL.md / MATCHING_PROMPT |

---

## 11. Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-1 | Surface association leak (hole in one) | A response keyword/category/textbook-matches exactly one prompt | Pairing solvable without projection; trial is a knowledge quiz | **No** — cross-viability validation forbids; regenerate the response |
| FM-2 | Elimination / parity leak | Equal-size bijection, or surplus too thin at small n | Last pair(s) forced for free | **No** — surplus D≥1 (D≥2 at n=3) + no-elimination-shortcut simulation |
| FM-3 | Ambiguous key (multiple valid bijections) | Generator leaves a second complete assignment defensible | Binary grade marks a valid answer wrong | **No** — unique-bijection validation; regenerate |
| FM-4 | Distractor genuinely belongs to a prompt | A distractor is a defensible match under the axis | Learner penalized for a valid attachment | **No** — sharpen the distractor or embed the gating condition in the prompt |
| FM-5 | Near-duplicate cell reads as both-valid | Twin response defensible for both twin prompts | Two valid readings, ungradeable | **No** — embed each twin's firing condition, or regenerate (near-duplicate-forces-ambiguity) |
| FM-6 | Learner submits wrong count (missing/extra prompt) | Learner error | Malformed → resubmit (not counted); a complete set with a distractor attached is incorrect, not resubmit | **Yes** — documented parse rule |
| FM-7 | D derivable from visible counts | Two lists printed, m and n visible | Learner knows how many responses go unused | **Yes** — does not leak *which*; unused responses are cross-viable |
| FM-8 | `matching` drawn but MATCHING_PROMPT unreadable | Missing file | Halt (REQ-MAT-E-001) | **Yes** — halt is correct |
| FM-9 | Distribution shifts to 1/4 each | Adding to TYPES | Fewer MCQ/MSQ/ORD per session | **Yes** — intended; note for calibration |
| FM-10 | Assigned axis can't make a resolvable grid (matchable concept) | Bad axis×concept pairing | Grid surface-solvable or unforced | **Yes, via guard** — re-draw axis; on exhaustion reconstruct case-set (REQ-MAT-E-003) |
| FM-11 | Concept is flat — no confusable case structure | Concept has one definition, no variants | No valid matching trial exists | **Yes, via guard** — intake gate excludes matching from the type draw (REQ-MAT-F-010) |
| FM-12 | Two intake gates interact (non-procedural AND flat) | Concept excludes both ordering and matching | Type draw is mcq/msq only | **Yes** — excludes combine (comma-joined); script errors only if *all* types excluded |

---

## 12. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | Small n (3) makes elimination hard to defeat | High | Med | D≥2 at n=3; near-duplicate cell spans last-resolved prompts; no-elimination-shortcut simulation mandatory in validation |
| R-2 | Cross-viability collapses to keyword matching (esp. recognition/transfer axes) | High | High | Role-selection maps prompt/response to *mechanism*, not label; ban surface differentiators; per-axis dry-run gate before ship |
| R-3 | Matching harder than the other types → skews pass rate | Med | Low | Binary grade consistent; threshold unchanged; reweight distribution if data warrants |
| R-4 | Grading disputes / near-duplicate ambiguity | Med | Med | Unique-bijection validation; regenerate-on-ambiguity (FM-5); construction-defect replace protocol |
| R-5 | Response pool up to 10 inflates cognitive load | Med | Low | Cap D≤3; prompts ≤3 sentences, responses ≤2 |
| R-6 | `select_mcq_axis.py` name now serves 4 types | High | Low | Accept as debt; rename out of scope |
| R-7 | Two intake gates raise intake complexity / mis-gating | Med | Med | Single combined determination step at intake; explicit combined-exclude requirement (REQ-MAT-F-010); document the mcq/msq-only fallback |

---

## 13. Edge cases (for `MATCHING_GENERATION_PROMPT.md`)

| Edge case | Resolution |
|---|---|
| surface-association-leak | A response resolvable by keyword/category/textbook overlap with one prompt → regenerate it as cross-viable (plausible for ≥2 prompts, differentiator projected only). Do not output while any cell is surface-solvable. |
| elimination-shortcut | After simulating correct placement of any subset, a remaining prompt is forced → add/strengthen a cross-viable distractor (raise D), or re-site the near-duplicate cell. Do not output while any prompt is forced by elimination. |
| ambiguous-key | A second complete bijection survives projection → tighten a prompt's distinguishing condition or replace a response until exactly one assignment survives. |
| distractor-actually-belongs | A distractor is a defensible match under the axis → sharpen it, or embed in the target prompt the gating condition its true response fires on, so the distractor's omission of that condition becomes the error. Do not output while any distractor is a defensible pick. |
| near-duplicate-forces-ambiguity | The twin response cannot be made wrong for its off-diagonal prompt without a prompt leaking its pairing → regenerate the cell or the trial. |
| unfit-axis-for-concept | Matchable concept, but the assigned axis can't make a resolvable grid → re-draw axis (exclude used + rejected); on exhaustion reconstruct the case-set. No type substitution (REQ-MAT-E-003). |
| non-matchable-concept | Concept affords no confusable case structure → excluded at intake: `matching` dropped from the type draw (REQ-MAT-F-010). Never reaches construction. |
| learner-malformed-response | Repeated prompt, reused response, out-of-range label, or missing prompt → resubmit; do not count. A well-formed set that attaches a prompt to a distractor is valid-and-incorrect. |
| learner-challenges-question | If a genuine second valid bijection exists, it is a construction defect — acknowledge, replace, do not count. Otherwise hold the evaluation and explain the axis. |
| repeated-probe-scenario-availability | Change the domain anchor for the new session; axis and concept unchanged. |

---

## 14. Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `mcq-probe/prompts/MATCHING_GENERATION_PROMPT.md` | Create | Full XML generation prompt mirroring ORDERING's structure + matching constructs (grid-design law, near-duplicate cell, orthodox distractor, unique bijection) | Governs matching construction/eval |
| `mcq-probe/scripts/select_question_type.py` | Modify | Add `"matching"` to `TYPES` (`--exclude` already supports multiple) | Enables matching selection; lets the intake gate drop matching for flat concepts |
| `mcq-probe/SKILL.md` | Modify | Intake matchable gate (+ combined exclude), Constants, Active Constraints, prompt-load, trial-loop present/wait/evaluate + axis re-draw (+ bookkeeping), re-presentation stability, Response Protocol (Matching), record schema, Report (Type col + Gap Inventory format + analysis classification), Error Handling (extend E-001, add E-002/E-003) | Wire matching into orchestration |
| `mcq-probe/scripts/select_mcq_axis.py` | None | — | Axis-agnostic; reused as-is |
| `CLAUDE.md` (repo doctrine) | Optional note | Mention matching alongside MCQ/MSQ/Ordering in the "adding a question type" section | Keep doctrine current |

---

## 15. Open questions

| # | Question | Blocker for? | Recommendation |
|---|---|---|---|
| 1 | Surplus responses (n prompts, n+D responses) vs equal-size bijection | Whole design | **Surplus** — the parity/elimination leak makes an equal-size bijection surface-solvable at the last pair(s). Load-bearing. |
| 2 | Binary all-or-nothing vs partial credit | Grade + report | **Binary** — matches the skill and the spec ("match all the pairs"). |
| 3 | Injective (no reuse) vs reusable responses | Grid model + near-duplicate device | **No reuse** — reuse dissolves the 2×2 near-duplicate cell and muddies the binary grade. |
| 4 | Intake `MATCHABLE` gate vs no gate (construct always) | Orchestration | **Add the gate**, mirroring the procedural gate — keeps flat concepts from producing weak trials. |
| 5 | Equiprobable 1/4 vs weighted distribution | select_question_type | **Equiprobable**, revisit after pass-rate data. |
| 6 | Label scheme: numeric prompts + alpha responses vs alpha both | Prompt wording + parse | **Numeric prompts, alpha responses** — removes prompt/response confusion in the reply. |
| 7 | Disclose that D responses are unused (counts visible) vs hide | Prompt wording | **Visible** — both lists are printed; D is derivable and does not leak *which* responses are unused. |

---

## 16. Implementation order

1. ~~Confirm the readback (§0) and OQ 1–7.~~ **Done.** Resolved per §5; the surplus-response interpretation (OQ 1) is load-bearing throughout the shipped generation prompt.
2. ~~Author `MATCHING_GENERATION_PROMPT.md`~~ **Done** — full XML: purpose, 9 axes reframed for matching (prompt-role→response-role semantic + wrong-attachment failure mode per axis; the `transfer` reframing carries the domain-vocabulary-inversion rule, REQ-MAT-F-020), question/prompt/response requirements, the grid-design law (§4) and required constructs, construction sequence + validation checklist (§6), feedback protocols (§7), edge cases (§13), and — as of the dry-run gate below — 9 worked examples (one per axis) plus 3 axis-fit fallback exercises.
3. ~~Modify `select_question_type.py`~~ **Done** — `"matching"` is in `TYPES`.
4. ~~Modify `SKILL.md`~~ **Done** — Intake Phase (matchable determination → combined `--exclude`), File Path Constants, Active Constraints, prompt-load, Trial-loop present/wait/evaluate + axis re-draw, Response Protocol (Matching correct/incorrect), internal record schema, Report Format (Type column + Gap Inventory), Error Handling (E-001/E-002/E-003) are all wired.
5. **Mandatory gate — Done.** All 9 axes dry-run in `MATCHING_GENERATION_PROMPT.md`'s `<worked-examples>` (examples 1–9), each confirmed dense/cross-viable/uniquely-resolvable against the internal-validation checklist (§6). The axis-fit fallback (construction-sequence step 2 / REQ-MAT-E-003) is exercised for all three hostile axes (recognition, transfer, coupling) in the new `<axis-fit-fallback-exercises>` section. Results below.
6. Optional: reweight type distribution after observing pass rates; add the CLAUDE.md doctrine note.

### Dry-Run Gate Results (§16 step 5)

| Axis | Concept (domain) | Near-duplicate cell | Orthodox-but-wrong | Fallback exercised | Verdict |
|---|---|---|---|---|---|
| failure-diagnosis | TCP throughput anomalies (networking) | prompts 2×4, responses B×D | E — capacity-bound first guess | — (example 1, pre-existing) | PASS |
| boundary-condition | Tire thermal window (motorsport) | prompts 2×3, responses D×A | C — "driver overdriving" | — (example 2, pre-existing) | PASS |
| transfer | Little's Law (multi-domain: hospital/software/coffee/factory) | two cells: {1,2}×{B,D}, {3,4}×{E,A} | C — throughput-from-time-cut misapplication | Yes — exercise 1, concept without a non-strained cross-domain analogue (SameSite cookies), redraws to boundary-condition | PASS |
| recognition | Concurrency bug classification (software) | prompts 1×3 (deadlock/livelock), responses B×E | D — "split the lock" | Yes — exercise 1, concept with no true-identity ambiguity (retry-backoff params), redraws to application | PASS |
| application | Retry-with-backoff outcomes (distributed systems) | prompts 1×2, responses C×E | A — jitter-benefit generalization | — | PASS |
| time | Read-after-write visibility (replication + cache TTL) | prompts 3×4, responses A×D | C — write-relative TTL misconception (coincidentally correct once) | — | PASS |
| risk | Schema-migration constraints (databases) | prompts 1×2, responses D×B | E — "wrap it in a transaction" | — | PASS |
| coupling | Service-decomposition arrangements (architecture) | prompts 1×3, responses D×E | C — "separate databases ⇒ decoupled" | Yes — exercise 3, concept with no second component to entangle with (hash table resizing), redraws to boundary-condition | PASS |
| observability | Monitoring-signal selection (SRE) | prompts 2×4, responses C×E | D — aggregate error-rate/latency dashboard | — | PASS |

**Overall verdict: PASS, 9/9.** Every axis produces a grid satisfying the full internal-validation checklist (§6): cross-viability in both directions, no-elimination-shortcut under D=1 (all nine examples use n=4, D=1 — the n=3/D≥2 floor from §5 is untested by this gate and remains a construction-time responsibility, not a gate finding), a unique bijection, ≥1 near-duplicate cell, and ≥1 orthodox-but-wrong distractor whose failure is argued explicitly rather than asserted. The three hostile axes named in this gate (R-2) each additionally demonstrate the axis-fit-rejection path firing on a genuinely mismatched concept and landing cleanly on a fitting axis, closing out R-1/R-2/R-4 as mitigated rather than merely designed-for. This clears the item explicitly deferred at merge in commit `6715bc8`.
